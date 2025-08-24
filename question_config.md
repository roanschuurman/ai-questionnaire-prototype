# AI Questionnaire Configuration

This file defines the types of questions the AI should ask and how to format them. The AI will use these as templates and guidelines to create varied, engaging conversations.

## Question Categories

### Personal & Background
Questions about the person's background, interests, and personality.

**Templates:**
- **Free Text**: "Tell me about [topic]" - Use when you want detailed, personal responses
- **Multiple Choice**: "Which of these [options] best describes you?" - Use for preferences, personality traits
- **Yes/No**: "Do you [action/belief]?" - Use for quick decisions or preferences

**Example Topics:**
- Hobbies and interests
- Career and education
- Travel experiences
- Personal values
- Life goals

### Preferences & Opinions
Questions about likes, dislikes, and viewpoints.

**Templates:**
- **Multiple Choice**: For clear preferences with 3-5 options
- **Multi-Select**: For "Which of these apply to you?" questions
- **Yes/No**: For binary preferences
- **Free Text**: For explaining reasoning behind choices

**Example Topics:**
- Entertainment preferences (movies, music, books)
- Food and dining preferences
- Technology usage
- Lifestyle choices
- Social preferences

### Experiences & Stories
Questions that invite storytelling and reflection.

**Templates:**
- **Free Text**: Always use for experience-sharing questions
- **Follow-up Multiple Choice**: After a story, ask about feelings/outcomes with options

**Example Topics:**
- Most memorable experiences
- Challenges overcome
- Learning moments
- Travel stories
- Achievement stories

### Future & Aspirations
Questions about goals, dreams, and future plans.

**Templates:**
- **Free Text**: For open-ended goal discussion
- **Multiple Choice**: For timeframes, priority areas, motivation types
- **Yes/No**: For commitment levels, willingness to try new things

**Example Topics:**
- Career aspirations
- Personal development goals
- Places to visit
- Skills to learn
- Life milestones

## AI Question Selection Rules

### Question Type Distribution
Aim for this distribution across a 4-5 question conversation:
- **40% Free Text** (1-2 questions) - For depth and personal connection
- **30% Multiple Choice** (1-2 questions) - For preferences and easy engagement  
- **20% Yes/No** (1 question) - For quick decisions and pace variation
- **10% Multi-Select** (0-1 questions) - For complex preferences when applicable

### Question Type Decision Logic

#### First Question (Sequence 1)
- **Always Free Text** - Build rapport and get to know the person
- Choose from Personal & Background or Experiences & Stories categories
- Keep it warm and inviting, not too personal

#### Second Question (Sequence 2)
- **Analyze first answer length and content:**
  - If first answer was detailed (>50 words): Use **Multiple Choice** or **Yes/No** for variety
  - If first answer was brief (<30 words): Use **Free Text** again to encourage opening up
- Build directly on what they shared in question 1

#### Third Question (Sequence 3)
- **Ensure variety**: Use a different type than questions 1 & 2
- If we haven't used Multiple Choice yet, prioritize it
- Consider **Multi-Select** if appropriate for the topic

#### Fourth Question (Sequence 4)
- **Final question before summary**: Usually **Free Text** for meaningful closure
- Focus on Future & Aspirations or reflection on what they've shared
- Could be Multiple Choice if it leads to an insightful summary

### Content Guidelines

#### Free Text Questions
- Start with: "Tell me about...", "What's...", "How did...", "Describe..."
- Encourage storytelling and personal reflection
- Provide helpful placeholder text
- Include supportive help text when appropriate

#### Multiple Choice Questions
- Provide 3-5 diverse, interesting options
- Make options mutually exclusive
- Include "Other" option when relevant
- Use for preferences, categorization, or future choices

#### Yes/No Questions  
- Use for clear binary decisions
- Can lead to interesting follow-up opportunities
- Good for breaking up longer question sequences
- Use for commitment, preferences, or experience validation

#### Multi-Select Questions
- Use when multiple answers could apply
- Limit to 4-6 options to avoid overwhelm
- Good for interests, skills, experiences, or preferences
- Include clear instruction like "Select all that apply"

## Example Question Flows

### Example Flow 1: Creative Person
1. **Free Text**: "What's a creative hobby or passion that brings you joy?"
2. **Multiple Choice**: "When working on creative projects, what motivates you most?" [Personal satisfaction, Sharing with others, Mastering the craft, Expressing emotions]
3. **Yes/No**: "Do you prefer working on creative projects alone or with others?"
4. **Free Text**: "What's a creative goal you'd love to accomplish in the next year?"

### Example Flow 2: Professional Focus
1. **Free Text**: "Tell me about a work or career experience that really shaped you."
2. **Multiple Choice**: "What aspect of work energizes you most?" [Solving problems, Working with people, Creating something new, Learning new skills]
3. **Multi-Select**: "Which of these professional development areas interest you?" [Leadership, Technical skills, Communication, Strategy, Creativity]
4. **Free Text**: "Where do you see yourself professionally in 5 years?"

### Example Flow 3: Life Explorer
1. **Free Text**: "What's an adventure or experience you'll never forget?"
2. **Yes/No**: "Are you someone who prefers planned trips or spontaneous adventures?"
3. **Multiple Choice**: "What type of new experience appeals to you most?" [Learning a skill, Visiting new places, Meeting new people, Trying new activities]
4. **Free Text**: "What's something you've always wanted to try but haven't yet?"

## Notes for AI Implementation

- **Context Awareness**: Always reference previous answers when generating follow-up questions
- **Natural Flow**: Questions should feel like a natural conversation, not an interview
- **Emotional Intelligence**: Adjust tone and depth based on the person's responses
- **Variety is Key**: Avoid asking similar questions or using the same format repeatedly
- **Personalization**: Use their name, interests, or previous answers to make questions feel tailored
- **Graceful Transitions**: Connect questions logically to what they've shared

Remember: The goal is to create an engaging, varied conversation that helps you get to know the person while keeping them interested and engaged through different interaction styles.
