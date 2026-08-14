# CivilDialog — AI/NLP Module

This module handles the NLP Processing stage of the CivilDialog pipeline: 
tokenization, toxicity detection, hate speech detection, logical fallacy 
detection, and civility scoring.

## Setup

pip install -r requirements.txt
python -m spacy download en_core_web_sm

## Usage (for backend integration)

from src.pipeline import analyze_text

result = analyze_text("some user message")

## Output format

{
  "text": "...",
  "preprocessing": { "tokens": [...], "num_tokens": int },
  "toxicity": { "is_toxic": bool, "toxicity_score": float, "labels": {...} },
  "hate_speech": { "is_hate_speech": bool, "hate_speech_score": float, "label": str },
  "fallacy": { "has_fallacy": bool, "detected_fallacies": [...], "matches": {...} },
  "civility_score": float,        # 0-100
  "civility_breakdown": {...},
  "timestamp": "ISO 8601 string"
}

## Notes for backend integration

- First call to `analyze_text` will be slower (~few seconds) as Hugging Face
  models load into memory. Subsequent calls are fast.
- No network calls are made at runtime after initial model download —
  everything runs locally/offline once set up.
- civility_score: higher = more civil (100 = perfectly civil, 0 = least civil)

## Demo

python demo.py

## Tests

pytest -v