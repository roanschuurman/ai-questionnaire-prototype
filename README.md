# AI Questionnaire Prototype (Flutter + FastAPI + OpenAI)

# AI Therapeutic Questionnaire Prototype

An intelligent questionnaire system that uses AI to conduct therapeutic self-reflection interviews. The system dynamically loads questions from a markdown file and automatically determines the most appropriate input types for each question.

## Features

- 🤖 **AI-Powered Question Generation**: Uses OpenAI GPT-4o-mini to generate contextual questions and responses
- 📱 **Cross-Platform Mobile App**: Flutter app that runs on iOS and Android
- 🔄 **Dynamic Question Loading**: Questions are loaded from `questions.md` file and can be updated without restarting
- 🧠 **Intelligent Type Detection**: AI automatically determines whether questions should be free text, multiple choice, yes/no, or multi-select
- 📊 **Therapeutic Summary**: AI generates personalized summaries after completing the questionnaire
- 🔗 **Real-time Sync**: Backend and mobile app communicate in real-time

## Architecture

```
├── agent/               # Python FastAPI backend
│   ├── main.py         # Main server with AI integration
│   └── requirements.txt
├── mobile/             # Flutter mobile app
│   └── main.dart       # Mobile app main file
├── questions.md        # Dynamic question configuration
└── .env               # Environment variables (OpenAI API key)
```

## Question Types

The system supports four input types, automatically determined by AI analysis:

- **free_text**: Open-ended questions for descriptions and reflections
- **yes_no**: Binary questions with yes/no answers
- **multiple_choice**: Single selection from predefined options
- **multi_select**: Multiple selections from predefined options

## Current Question Flow

1. **Define Your Primary Voice** (free_text)
2. **Voice's Message** (free_text)
3. **Voice's Emotion** (multiple_choice with emotion options)
4. **Negative Impact** (yes_no)
5. **Willingness to Observe** (yes_no)
6. **Acceptance** (yes_no)
7. **Values and Action** (free_text)
8. **Action Plan** (multi_select with action steps)

## Setup

### Prerequisites

- Python 3.8+ with pip
- Flutter SDK
- iOS device or Android device for testing
- OpenAI API key

### Backend Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   cd agent
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file in project root:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

5. Start the backend:
   ```bash
   python main.py
   ```
   Server will run on `http://0.0.0.0:8000`

### Mobile App Setup

1. Navigate to mobile directory:
   ```bash
   cd mobile
   ```

2. Get Flutter dependencies:
   ```bash
   flutter pub get
   ```

3. Update backend URL in `main.dart` if needed (line ~20)

4. Run on device:
   ```bash
   flutter run
   ```

## Configuration

### Updating Questions

Simply edit the `questions.md` file to add, remove, or modify questions. The AI will automatically:

- Determine the appropriate input type for each question
- Generate contextual follow-up prompts
- Provide relevant options for multiple choice questions

### Question Format

```markdown
## 1. Question Title
Question text goes here?

## 2. Another Question
Another question text?
```

## API Endpoints

- `POST /sessions` - Create new questionnaire session
- `POST /sessions/{id}/answer` - Submit answer and get next question
- `POST /next_step` - Get next question based on current answers
- `GET /sessions/{id}` - Get session state

## AI Integration

The system uses a two-phase AI approach:

1. **Type Detection**: AI analyzes each question to determine optimal input type with 90%+ confidence
2. **Question Generation**: AI generates contextual questions with appropriate options and help text

## Development Features

- **Hot Reload**: Flutter supports hot reload for rapid development
- **Dynamic Loading**: Questions reload from file on each new session
- **Comprehensive Logging**: Backend logs AI decisions and type determinations
- **Error Handling**: Fallback mechanisms for AI failures

## Therapeutic Use

This prototype is designed for self-reflection and therapeutic exploration, focusing on:

- Understanding internal voices and self-talk
- Identifying emotional patterns
- Building self-awareness and acceptance
- Creating actionable commitments for personal growth

## License

This is a prototype project for educational and therapeutic research purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Technical Notes

- Backend: FastAPI with OpenAI integration
- Frontend: Flutter with HTTP client
- AI Model: GPT-4o-mini for question generation and type detection
- Storage: In-memory session storage (prototype level)
- Network: Supports wireless device connection for testing

## ✨ Features
- **AI-Powered Questions**: Uses OpenAI GPT-4 to generate contextual questions
- **Dynamic Flow**: Questions adapt based on previous answers
- **Multiple Input Types**: Text, yes/no, multiple choice, multi-select
- **Smart Summaries**: AI-generated personalized summaries
- **Mobile-First**: Flutter app with iOS/Android support
- **Real-time**: Live question generation and progression

## 🏗️ Architecture
- `agent/` — FastAPI backend with OpenAI integration
- `lib/` — Flutter mobile app (moved to root for cleaner structure)
- `mobile/` — Original Flutter code reference

## 🚀 Quick Start

### 1) Set up OpenAI API
```bash
# Get your API key from https://platform.openai.com/api-keys
# Add it to .env file:
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2) Start the AI Backend
```bash
cd agent
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Run the Flutter App
```bash
# Make sure you're in the project root
flutter pub get
flutter run -d ios   # or -d android
```

## 🤖 How the AI Works

1. **First Question**: AI generates an engaging opening question
2. **Follow-ups**: Each subsequent question is generated based on all previous answers
3. **Context Building**: AI maintains conversation context throughout the session
4. **Smart Summary**: Final summary is personalized based on the entire conversation
5. **Fallback System**: If AI fails, intelligent fallback questions ensure smooth experience

## 📱 Mobile Configuration

The Flutter app is configured to work with:
- **iOS**: Network permissions for HTTP requests
- **Android**: Internet permissions (standard)
- **Network Discovery**: Automatically finds your backend IP

## 🔧 Configuration

### Backend Configuration
- OpenAI API key in `.env` file
- Configurable question limits (default: 5 questions)
- Customizable AI prompts and behavior

### Frontend Configuration
- Backend URL auto-detection or manual override
- Comprehensive error handling and debugging
- Offline fallback support

## 🧪 Testing

The app now includes:
- Detailed console logging for debugging
- Error state handling
- Network connectivity validation
- AI response validation with fallbacks

## 🔒 Environment Variables

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-openai-api-key-here
BACKEND_URL=http://192.168.1.149:8000
```

## 📊 AI Question Examples

The AI can generate various question types:
- **Personal**: "What's something you're passionate about?"
- **Contextual**: "Since you mentioned you love reading, what genre draws you in most?"
- **Exploratory**: "How do you like to unwind after a busy day?"
- **Multiple Choice**: Dynamic options based on previous answers

Ready to experience intelligent conversations! 🎯
