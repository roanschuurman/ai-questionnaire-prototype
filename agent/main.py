from typing import List, Optional, Literal, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import openai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from typing import List, Optional, Literal, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Question Orchestrator (Prototype)")

# Initialize OpenAI client
openai_client = OpenAI()  # Uses OPENAI_API_KEY from environment

# Initialize OpenAI client
openai_client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

# ---- Models -----------------------------------------------------------------

InputKind = Literal["free_text", "yes_no", "multiple_choice", "multi_select"]

class Input(BaseModel):
    kind: InputKind
    options: Optional[List[Dict[str, str]]] = None
    placeholder: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allow_other: Optional[bool] = None

class Question(BaseModel):
    id: str
    label: str
    input: Input
    required: bool = True
    help: Optional[str] = None

class Step(BaseModel):
    id: str
    type: Literal["question", "info", "summary", "decision"]
    question: Optional[Question] = None
    ui: Dict[str, Any] = {}
    validation: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

class CreateSession(BaseModel):
    user_id: Optional[str] = None
    flow: Optional[str] = None

class Answer(BaseModel):
    session_id: str
    question_id: str
    answer: Dict[str, Any]

# ---- In-memory store (for prototype) ----------------------------------------

SESSIONS: Dict[str, Dict[str, Any]] = {}  # session_id -> {"answers":{}, "sequence": int}

# ---- AI Question Generation --------------------------------------------------

# Load specific questions configuration
def load_questions_config():
    """Load the specific questions from questions.md file"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'questions.md')
        with open(config_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Could not load questions.md: {e}")
        return ""

def parse_questions_from_config(config_content: str) -> Dict[int, Dict[str, str]]:
    """Parse questions from the markdown content and return structured data"""
    questions = {}
    lines = config_content.split('\n')
    current_question = None
    current_text = ""
    in_question_content = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('## ') and any(char.isdigit() for char in line):
            # Save previous question if exists
            if current_question is not None:
                question_text = current_text.strip()
                questions[current_question] = {
                    'text': question_text,
                    'type': determine_question_type_with_ai(question_text, current_question)
                }
            
            # Extract question number
            try:
                parts = line.split('.', 1)
                current_question = int(parts[0].replace('##', '').strip())
                current_text = ""
                in_question_content = True
            except:
                continue
        elif line.startswith('---'):
            in_question_content = False
        elif current_question is not None and in_question_content and line:
            if not line.startswith('*') and not line.startswith('('):  # Skip examples and notes
                if current_text:
                    current_text += " "
                current_text += line
    
    # Don't forget the last question
    if current_question is not None:
        question_text = current_text.strip()
        questions[current_question] = {
            'text': question_text,
            'type': determine_question_type_with_ai(question_text, current_question)
        }
    
    return questions

def determine_question_type_with_ai(question_text: str, sequence: int) -> str:
    """Use AI to determine the most appropriate question type with high confidence"""
    
    system_prompt = """You are an expert in questionnaire design. Your task is to analyze a question and determine the BEST input type for it.

Available input types:
- free_text: Open-ended questions requiring written responses (stories, descriptions, explanations)
- yes_no: Simple binary questions that can be answered with yes or no
- multiple_choice: Questions where user selects ONE option from a predefined list
- multi_select: Questions where user can select MULTIPLE options from a list

Rules for classification:
1. free_text: Use for open-ended questions asking for descriptions, explanations, stories, or personal reflections
2. yes_no: ONLY for questions that are literally asking yes/no (contains "yes/no", starts with "Do you", "Are you", "Can you", "Will you")
3. multiple_choice: For questions asking to choose ONE from categories (emotions, preferences, methods)
4. multi_select: For questions asking for multiple selections (skills, activities, multiple actions)

Return ONLY the type name (free_text, yes_no, multiple_choice, or multi_select). Be 90%+ certain of your choice."""

    user_prompt = f"""Analyze this question and determine the best input type:

Question: "{question_text}"

Consider:
- Is this asking for an open description/explanation? → free_text
- Is this literally a yes/no question? → yes_no  
- Is this asking to select ONE option from categories? → multiple_choice
- Is this asking to select MULTIPLE items? → multi_select

Return only the input type."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50,
            temperature=0.1  # Low temperature for consistency
        )
        
        ai_type = response.choices[0].message.content.strip().lower()
        
        # Validate the response
        valid_types = ["free_text", "yes_no", "multiple_choice", "multi_select"]
        if ai_type in valid_types:
            print(f"AI determined type for Q{sequence}: '{question_text[:50]}...' → {ai_type}")
            return ai_type
        else:
            print(f"AI returned invalid type '{ai_type}', falling back to content analysis")
            return determine_question_type_from_content(question_text)
            
    except Exception as e:
        print(f"Error in AI type determination: {e}")
        return determine_question_type_from_content(question_text)
    """Determine question type based on content analysis"""
    question_lower = question_text.lower().strip()
    
    # Yes/No questions - be more specific
    if (question_lower.startswith('does this voice') or 
        question_lower.startswith('are you willing') or 
        question_lower.startswith('can you accept') or
        'yes / no' in question_lower or 
        'yes/no' in question_lower):
        return "yes_no"
    
    # Multiple choice indicators (emotion, feelings)
    if any(indicator in question_lower for indicator in ['what emotion', 'which emotion']):
        return "multiple_choice"
    
    # Multi-select indicators (multiple actions, steps)
    if any(indicator in question_lower for indicator in ['choose minimal', 'select multiple', 'specific steps', 'multiple actions']):
        return "multi_select"
    
    # Default to free text
    return "free_text"

def get_total_questions() -> int:
    """Get the total number of questions from the current questions.md file"""
    config_content = load_questions_config()
    questions = parse_questions_from_config(config_content)
    return len(questions)

def determine_question_type(sequence: int, answers: Dict[str, Any]) -> str:
    """Determine the appropriate question type based on the specific question sequence from questions.md"""
    config_content = load_questions_config()
    questions = parse_questions_from_config(config_content)
    
    if sequence in questions:
        return questions[sequence]['type']
    
    return "free_text"  # fallback

def determine_question_type_from_content(question_text: str) -> str:
    """Determine question type based on content analysis (fallback method)"""
    question_lower = question_text.lower()
    
    # Yes/No questions - be very specific
    if any(indicator in question_lower for indicator in [
        'yes / no', 'yes/no', 
        'does this voice often affect',
        'are you willing to try',
        'can you accept that'
    ]):
        return "yes_no"
    
    # Multi-select questions
    if any(indicator in question_lower for indicator in [
        'choose minimal', 'select all', 'which of these', 
        'what specific steps', 'multiple actions'
    ]):
        return "multi_select"
    
    # Multiple choice questions  
    if any(indicator in question_lower for indicator in [
        'what emotion', 'which emotion', 'what feeling'
    ]):
        return "multiple_choice"
    
    # Default to free text for open-ended questions
    return "free_text"

def generate_ai_question(session_id: str, answers: Dict[str, Any], sequence: int) -> Step:
    """Generate a question using OpenAI based on previous answers and configuration."""
    
    # Load fresh questions config and parse it
    questions_config = load_questions_config()
    parsed_questions = parse_questions_from_config(questions_config)
    total_questions = len(parsed_questions)
    
    # Check if we've answered all questions - generate summary
    if sequence > total_questions:
        return generate_summary_step(session_id, answers)
    
    # Get the specific question for this sequence
    current_question_data = parsed_questions.get(sequence)
    if not current_question_data:
        return generate_summary_step(session_id, answers)
    
    target_question_type = current_question_data['type']
    question_text = current_question_data['text']
    
    # Create context from previous answers
    context_parts = []
    for q_id, answer_data in answers.items():
        answer_value = answer_data.get('value', 'No answer')
        answer_type = answer_data.get('kind', 'unknown')
        context_parts.append(f"Q{len(context_parts)+1} ({answer_type}): {answer_value}")
    
    context_text = "\n".join(context_parts) if context_parts else "This is the first question."
    
    # Create comprehensive system prompt with your specific questions
    system_prompt = f"""You are conducting a therapeutic self-reflection interview using these specific questions:

{questions_config}

You must ask question #{sequence} of {total_questions} which is: "{question_text}"

CRITICAL REQUIREMENTS:
1. The question type MUST be: {target_question_type}
2. Return ONLY a JSON object (no markdown, no explanations)
3. Use the EXACT question text: "{question_text}"
4. For multiple_choice: provide realistic emotion options for emotion questions, or relevant options for other questions
5. For multi_select: provide multiple actionable options that can be selected together
6. For yes_no: no options needed
7. For free_text: provide encouraging placeholder text

JSON Format:
{{
  "question": "{question_text}",
  "input_type": "{target_question_type}",
  "help": "Optional helpful guidance text",
  "placeholder": "Optional placeholder for free_text",
  "options": [
    {{"value": "key1", "label": "Option 1"}},
    {{"value": "key2", "label": "Option 2"}}
  ]
}}

Use therapeutic, supportive language in help text."""

    if sequence == 1:
        user_prompt = f"""Generate question #{sequence} of {total_questions} from the questions.md file.
        Question text: "{question_text}"
        Question type must be: {target_question_type}
        Include a supportive placeholder to encourage open sharing."""
    
    else:
        user_prompt = f"""Based on the previous answers:
{context_text}

Generate question #{sequence} of {total_questions} from the questions.md file. 
Question text: "{question_text}"
Question type must be: {target_question_type}

Build on their previous answers to create continuity in this therapeutic conversation."""
    
    try:
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if ai_response.startswith("```json"):
            ai_response = ai_response.replace("```json", "").replace("```", "").strip()
        elif ai_response.startswith("```"):
            ai_response = ai_response.replace("```", "").strip()
        
        # Try to parse as JSON
        try:
            question_data = json.loads(ai_response)
        except json.JSONDecodeError:
            print(f"Failed to parse AI response as JSON: {ai_response}")
            # Fallback if AI doesn't return valid JSON
            question_data = {
                "question": ai_response.replace('"', '').replace('\n', ' ')[:200],
                "input_type": target_question_type,
                "placeholder": "Type your answer here" if target_question_type == "free_text" else None
            }
        
        # Validate and fix the question type
        actual_question_type = question_data.get("input_type", target_question_type)
        if actual_question_type != target_question_type:
            question_data["input_type"] = target_question_type
            
        # Create input object based on type
        if target_question_type == "multiple_choice":
            options = question_data.get("options", [
                {"value": "opt1", "label": "Option 1"},
                {"value": "opt2", "label": "Option 2"},
                {"value": "opt3", "label": "Option 3"}
            ])
            input_obj = Input(kind="multiple_choice", options=options)
        elif target_question_type == "multi_select":
            options = question_data.get("options", [
                {"value": "opt1", "label": "Option 1"},
                {"value": "opt2", "label": "Option 2"},
                {"value": "opt3", "label": "Option 3"}
            ])
            input_obj = Input(kind="multi_select", options=options)
        elif target_question_type == "yes_no":
            input_obj = Input(kind="yes_no")
        else:  # free_text
            input_obj = Input(
                kind="free_text",
                placeholder=question_data.get("placeholder", "Share your thoughts...")
            )
        
        # Create question
        question = Question(
            id=f"q_ai_{sequence}",
            label=question_data["question"],
            input=input_obj,
            required=True,
            help=question_data.get("help")
        )
        
        # Dynamic button label based on total questions
        total_questions = get_total_questions()
        button_label = "Continue" if sequence < total_questions else "Finish"
        
        return Step(
            id=f"step_{sequence}",
            type="question",
            question=question,
            ui={"next_button_label": button_label},
            context={
                "session_id": session_id, 
                "sequence": sequence, 
                "ai_generated": True,
                "target_type": target_question_type,
                "actual_type": actual_question_type,
                "total_questions": total_questions
            }
        )
    
    except Exception as e:
        print(f"Error generating AI question: {e}")
        # Fallback to a simple question
        return fallback_question(session_id, sequence, target_question_type)

def fallback_question(session_id: str, sequence: int, target_type: str = "free_text") -> Step:
    """Fallback question when AI generation fails - uses your specific questions."""
    
    # Load and parse questions dynamically
    questions_config = load_questions_config()
    parsed_questions = parse_questions_from_config(questions_config)
    total_questions = len(parsed_questions)
    
    # Get the question for this sequence
    current_question_data = parsed_questions.get(sequence)
    if current_question_data:
        question_text = current_question_data['text']
    else:
        question_text = "What's on your mind right now?"
    
    # Create appropriate input based on type and question content
    if target_type == "multiple_choice":
        if "emotion" in question_text.lower():
            # Emotion options
            options = [
                {"value": "fear", "label": "Fear"},
                {"value": "shame", "label": "Shame"},
                {"value": "anger", "label": "Anger"},
                {"value": "sadness", "label": "Sadness"},
                {"value": "guilt", "label": "Guilt"},
                {"value": "anxiety", "label": "Anxiety"},
                {"value": "other", "label": "Other emotion"}
            ]
        else:
            options = [
                {"value": "opt1", "label": "Option 1"},
                {"value": "opt2", "label": "Option 2"},
                {"value": "opt3", "label": "Option 3"}
            ]
        input_obj = Input(kind="multiple_choice", options=options)
    elif target_type == "multi_select":
        if "action" in question_text.lower() or "steps" in question_text.lower():
            # Action plan options
            options = [
                {"value": "daily_practice", "label": "Daily mindfulness practice"},
                {"value": "journaling", "label": "Regular journaling"},
                {"value": "support_network", "label": "Connect with support network"},
                {"value": "professional_help", "label": "Seek professional guidance"},
                {"value": "self_care", "label": "Prioritize self-care activities"},
                {"value": "boundaries", "label": "Set healthy boundaries"}
            ]
        else:
            options = [
                {"value": "opt1", "label": "Option 1"},
                {"value": "opt2", "label": "Option 2"},
                {"value": "opt3", "label": "Option 3"}
            ]
        input_obj = Input(kind="multi_select", options=options)
    elif target_type == "yes_no":
        input_obj = Input(kind="yes_no")
    else:
        # Free text - create appropriate placeholder
        if "voice" in question_text.lower() and sequence <= 2:
            placeholder = "Describe what you experience..."
        elif "value" in question_text.lower() or "commit" in question_text.lower():
            placeholder = "Write your commitment or value here..."
        else:
            placeholder = "Share your thoughts..."
        input_obj = Input(kind="free_text", placeholder=placeholder)
    
    # Dynamic button label
    button_label = "Continue" if sequence < total_questions else "Finish"
    
    return Step(
        id=f"step_{sequence}",
        type="question",
        question=Question(
            id=f"q_fallback_{sequence}",
            label=question_text,
            input=input_obj,
            required=True
        ),
        ui={"next_button_label": button_label},
        context={"session_id": session_id, "sequence": sequence, "fallback": True, "total_questions": total_questions}
    )

def generate_summary_step(session_id: str, answers: Dict[str, Any]) -> Step:
    """Generate a detailed AI-powered summary of all questions and answers."""
    
    # Load questions to get the actual question texts
    questions_config = load_questions_config()
    parsed_questions = parse_questions_from_config(questions_config)
    
    # Create detailed context with questions and answers
    qa_pairs = []
    for q_id, answer_data in answers.items():
        answer_value = answer_data.get('value', 'No answer')
        answer_kind = answer_data.get('kind', 'unknown')
        
        # Extract question number from q_id (e.g., "q_ai_1" -> 1)
        try:
            q_number = int(q_id.split('_')[-1])
            question_text = parsed_questions.get(q_number, {}).get('text', f'Question {q_number}')
        except:
            question_text = f'Question for {q_id}'
        
        qa_pairs.append(f"Q: {question_text}\nA: {answer_value}")
    
    qa_text = "\n\n".join(qa_pairs)
    total_questions = len(parsed_questions)
    
    try:
        # Generate comprehensive summary using AI
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a skilled therapeutic summarizer. Create a comprehensive, personalized summary that:
                    
                    1. SPECIFIC CONTENT: Reference their actual answers and insights, not generic statements
                    2. THERAPEUTIC INSIGHTS: Identify patterns in their responses about their inner voice, emotions, and behaviors
                    3. STRENGTHS & PROGRESS: Highlight their self-awareness, willingness to change, and specific commitments
                    4. ACTIONABLE REFLECTION: Connect their answers to show a coherent picture of their journey
                    5. ENCOURAGING TONE: Warm, professional, and validating
                    
                    Structure: 2-3 paragraphs, 4-6 sentences total. Be specific to their responses, not generic."""
                },
                {
                    "role": "user", 
                    "content": f"""Please create a detailed therapeutic summary based on these specific question-answer pairs from a self-reflection session:

{qa_text}

Create a summary that:
- References their specific answers (the voice they identified, emotions they selected, etc.)
- Acknowledges their insights about their inner voice and its impact
- Validates their commitment to the values/actions they mentioned
- Highlights their willingness to observe and accept difficult emotions
- Encourages their continued growth journey

Make it personal and specific to what they shared, not a generic response."""
                }
            ],
            max_tokens=400,
            temperature=0.6
        )
        
        summary = response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        # Create a basic fallback summary with their actual content
        first_answer = list(answers.values())[0].get('value', 'your inner voice') if answers else 'your inner voice'
        summary = f"Thank you for exploring your relationship with {first_answer} and reflecting on its impact on your life. Your willingness to examine these patterns and commit to positive change demonstrates real courage and self-awareness. This kind of honest self-reflection is a powerful foundation for continued growth and healing."
    
    return Step(
        id="step_summary",
        type="info",  # Flutter app expects 'info' type for summary
        question=None,
        ui={
            "next_button_label": "Start New Session",
            "summary_text": summary,
            "show_restart": True
        },
        context={
            "session_id": session_id, 
            "sequence": len(answers) + 1, 
            "summary": summary,
            "total_questions": total_questions,
            "completed": True
        }
    )

def next_step(session_id: str) -> Step:
    """Generate the next step using AI."""
    state = SESSIONS[session_id]
    answers = state["answers"]
    sequence = len(answers) + 1
    
    # Update sequence
    state["sequence"] = sequence
    
    # Generate AI question
    return generate_ai_question(session_id, answers, sequence)

# ---- Routes ------------------------------------------------------------------

@app.post("/sessions")
def create_session(payload: CreateSession):
    sid = str(uuid4())
    SESSIONS[sid] = {"answers": {}, "sequence": 0}
    step = next_step(sid)
    return {"session_id": sid, "step": step}

@app.post("/sessions/{sid}/answer")
def post_answer(sid: str, ans: Answer):
    if sid not in SESSIONS or ans.session_id != sid:
        raise HTTPException(404, "Session not found")
    state = SESSIONS[sid]
    # very light validation: ensure question progression is sensible
    state["answers"][ans.question_id] = ans.answer
    step = next_step(sid)
    return {"step": step}

@app.get("/sessions/{sid}")
def get_state(sid: str):
    if sid not in SESSIONS:
        raise HTTPException(404, "Session not found")
    return SESSIONS[sid]

@app.post("/next_step")
def post_next_step(payload: Dict[str, Any]):
    """Get the next step for a session based on current answers."""
    session_id = payload.get("session_id")
    answers = payload.get("answers", {})
    
    if not session_id:
        raise HTTPException(400, "session_id is required")
    
    # Initialize session if it doesn't exist
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {"answers": {}, "sequence": 0}
    
    # Update session with provided answers
    state = SESSIONS[session_id]
    state["answers"].update(answers)
    
    # Generate next step
    step = next_step(session_id)
    return step

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
