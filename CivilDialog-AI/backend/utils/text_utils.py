import re
from typing import Set

# A set of common toxic words, insults, or aggressive language patterns
TOXIC_KEYWORDS: Set[str] = {
    "idiot", "stupid", "garbage", "trash", "useless", "dumb", "fool", "jerk", 
    "bastard", "disgusting", "pathetic", "hate", "liar", "cheat", "cheated",
    "moron", "shame", "crap", "terrible", "worst", "hate speech", "incompetent"
}

# Patterns matching logical fallacies or aggressive debate structures
FALLACY_PATTERNS = [
    # Ad Hominem patterns: addressing the person rather than the point
    r"\byou are\b.*\b(stupid|idiot|wrong|fool|clueless|lying|lazy)\b",
    r"\bdon't trust\b.*\b(he|she|they|him|her)\b",
    # Strawman / Misrepresentation patterns
    r"\bso you\b.*\b(want|mean|are saying|think)\b.*\b(stop|all|none|everything|nothing)\b",
    # False Dilemma patterns
    r"\beither\b.*\b(support|agree|join)\b.*\bor\b",
    r"\bif you don't\b.*\bthen you\b",
    # Slippery slope patterns
    r"\bif we allow\b.*\b(eventually|collapse|disaster|everyone will|nobody will)\b",
    r"\bif we let\b.*\b(always|never|leads to)\b",
    # Hasty generalization patterns
    r"\b(all|every|everyone|never|always)\b.*\b(are|is|do|does)\b.*\b(dishonest|bad|untrustworthy|lazy)\b"
]

def sanitize_text(text: str) -> str:
    """
    Cleans and sanitizes the input text by removing HTML tags, excess whitespace,
    and special characters that could disrupt processing.
    """
    if not text:
        return ""
    # Strip HTML tags
    text = re.sub(r"<[^>]*>", "", text)
    # Normalize whitespaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def is_potentially_problematic(text: str) -> bool:
    """
    Runs local heuristics (keywords & regex patterns) to check if the text
    might contain communication issues or logical fallacies.
    
    If it returns False, the text is highly likely to be constructive and clean,
    allowing us to bypass expensive Gemini API calls.
    """
    cleaned = sanitize_text(text).lower()
    
    # 1. Check for explicit toxic keywords
    for word in TOXIC_KEYWORDS:
        if word in cleaned:
            return True
            
    # 2. Check for fallacy/argumentative patterns
    for pattern in FALLACY_PATTERNS:
        if re.search(pattern, cleaned):
            return True
            
    # 3. Aggressive sentence endings or capitals (e.g. SHOUTING)
    # Check if there's a word in all caps (length > 3) that isn't an acronym
    words = text.split()
    shouting_words = [w for w in words if w.isupper() and len(w) > 3 and w.isalpha()]
    if shouting_words:
        return True
        
    # Check for excessive exclamation marks (e.g. "!!!")
    if "!!!" in text:
        return True
        
    # Default to false for normal, constructive-looking inputs
    return False
