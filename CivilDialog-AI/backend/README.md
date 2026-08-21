# CivilDialog AI Moderation Engine (Member 4 Module)

This module provides real-time discussion moderation features for the **CivilDialog** platform, specializing in LLM integration, logical fallacy detection, intent-preserving respectful rewrites, and constructive feedback generation.

It is designed as an independent FastAPI service that can be run standalone and later integrated into the larger CivilDialog ecosystem.

---

## Features

1. **Logical Fallacy Detection:** Identifies 6 core logical fallacies:
   - *Ad Hominem* (attacking character)
   - *Strawman* (misrepresentation of arguments)
   - *False Dilemma* (presenting only two extreme choices)
   - *Slippery Slope* (unsubstantiated causal chains)
   - *Hasty Generalization* (conclusions from small sample sizes)
   - *Appeal to Emotion* (manipulating feelings)
2. **Respectful Rewrite Engine:** Re-evaluates toxic or fallacious text, rewriting it into civil, clear statements. Crucially, **the user's core intent, facts, and stance are preserved** (it does not convert disagreement into agreement).
3. **Constructive Feedback Service:** Provides context-aware explanations, reasons, and tips appropriate for display in real-time UIs.
4. **Performance & Cost Optimization:** Uses local heuristic pre-screening rules to skip expensive LLM calls for clearly constructive/clean comments.
5. **Robust Error Handling:** Intercepts rate limits, timeout, and API failures, returning safe fallback JSON schemas instead of throwing raw stack traces or crashing.
## Project Structure
The Member 4 backend module is organized as follows:

```text
backend/
├── api/          # FastAPI route definitions
├── prompts/      # LLM prompts and prompt templates
├── schemas/      # Pydantic request/response models
├── services/     # Gemini LLM integration and moderation logic
├── tests/        # Backend LLM and API tests
├── utils/        # Shared utility functions
├── main.py       # FastAPI application entry point
├── .env.example  # Environment variable template
└── requirements.txt

---

## Installation & Setup

Commands are written for Windows environments as per project requirements.

### 1. Prerequisite
Ensure you have **Python 3.10+** installed on your system.

### 2. Activate the Project Virtual Environment

The project uses a single virtual environment located at the root of `CivilDialog-AI`.

From the `CivilDialog-AI` directory, activate it using PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration Setup (`.env`)
Copy the `.env.example` file to create your local configuration:
```bash
copy .env.example .env
```
Open the `.env` file and insert your Google Gemini API key:
```ini
GEMINI_API_KEY=AIzaSy...your_actual_key_here
GEMINI_MODEL=gemini-3.5-flash
ENABLE_INTENT_VERIFICATION=true
DEBUG=true
```
*Note: `.env` is listed in `.gitignore` and will never be pushed to your repository.*

---

## Running the API Server
```markdown
From the `CivilDialog-AI` project root directory, make sure the project virtual environment is active:

```powershell
.\.venv\Scripts\Activate.ps1
You should see:
```
INFO:     Uvicorn server running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Open your browser to:
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Docs:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints

### 1. POST `/api/v1/llm/analyze`
Analyzes a text input. It pre-screens using local heuristics; if it looks clean, it returns a safe, clean response directly. Otherwise, it queries Gemini.

- **Request Body:**
  ```json
  {
    "text": "You are stupid. Your idea is completely useless."
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "is_problematic": true,
    "issues": [
      {
        "type": "personal_attack",
        "severity": "high",
        "confidence": 0.94,
        "evidence": "stupid"
      },
      {
        "type": "ad_hominem",
        "severity": "high",
        "confidence": 0.92,
        "evidence": "You are stupid"
      }
    ],
    "sentiment": "negative",
    "explanation": "Attacks the person directly rather than discussing the proposal.",
    "rewrite": "I disagree with this project because I believe it has several limitations.",
    "suggestions": [
      "Focus on the argument instead of criticizing the person."
    ],
    "confidence": 0.93
  }
  ```

### 2. POST `/api/v1/llm/rewrite`
Performs intent-preserving respectful rewrites, targeting specific previously detected issues.

- **Request Body:**
  ```json
  {
    "text": "Your code is absolute garbage.",
    "issues": [
      {
        "type": "toxic_language",
        "severity": "high",
        "confidence": 0.95,
        "evidence": "absolute garbage"
      }
    ]
  }
  ```
- **Response (200):**
  ```json
  {
    "rewrite": "I think this implementation needs major refactoring.",
    "original_intent_preserved": true
  }
  ```

### 3. POST `/api/v1/llm/fallacy`
Scans inputs specifically for logical fallacies.

- **Request Body:**
  ```json
  {
    "text": "Either you support this project or you don't care about the team."
  }
  ```
- **Response (200):**
  ```json
  {
    "fallacies": [
      {
        "type": "false_dilemma",
        "severity": "high",
        "confidence": 0.89,
        "evidence": "Either you support this project or you don't care about the team."
      }
    ]
  }
  ```

### 4. POST `/api/v1/llm/feedback`
Returns constructive feedback and improvement guidance based on the detected issues. This endpoint is designed for real-time UI feedback and does not require an additional Gemini API call.

### 5. GET `/api/v1/llm/health`
Returns status of API configuration.

---

## Running Unit Tests

```markdown
We have implemented **34 backend test cases** using `pytest` to test schemas, routes, fallacy detection, rewrites, LLM analysis, and error fallbacks. The Gemini API calls are mocked in the backend tests, so these tests can run without an internet connection or a real API key.

### Test Results

- **Backend LLM tests:** 34/34 passed
- **Original `src` tests:** 21/21 passed
- **Complete project test suite:** **55/55 passed**

The complete test suite covers both the original moderation functionality and the Member 4 LLM integration and rewrite engine.```bash
# From the CivilDialog-AI project root
python -m pytest tests/
```

---

## Integration Guide (For Team Members)

### Frontend Integration (Real-Time typing / Debounce)
For the real-time feedback UI (where suggestions are displayed as the user types), **DO NOT call the API on every single keystroke**.
1. Implement a **debounce of 500ms - 800ms**.
2. Only send requests when text length is **at least 10 characters** (to avoid premature checks on words like "I", "He").
3. Use the `is_problematic` and `rewrite` fields to decide whether to prompt the user with the "Use Suggestion" button.

### Backend Integration
- All routes reside under `/api/v1/llm/`.
- Import `schemas.llm_schema` models to share data definitions.
- Set up an HTTP client (like Python's `httpx` or Node's `axios`) to call these endpoints from your main application router.
