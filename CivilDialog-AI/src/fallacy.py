import re

# Simple pattern-based fallacy detection.
# Each fallacy type has a set of trigger phrases/patterns commonly
# associated with that kind of flawed reasoning.

FALLACY_PATTERNS = {
    "ad hominem": [
        r"\byou'?re (an? )?(idiot|stupid|dumb|fool|moron|clueless)\b",
        r"\byou are (an? )?(idiot|stupid|dumb|fool|moron|clueless)\b",
        r"\bwhat would you know\b",
        r"\btypical [a-z]+ (thing to say|response)\b",
    ],
    "strawman": [
        r"\bso you'?re saying\b",
        r"\bso what you mean is\b",
        r"\byou basically just said\b",
    ],
    "false dichotomy": [
        r"\beither .+ or .+\b",
        r"\bthere are only two (options|choices|ways)\b",
        r"\byou'?re either with (us|me) or against (us|me)\b",
    ],
    "slippery slope": [
        r"\bif we allow .+ (then|,) .+ will (happen|follow)\b",
        r"\bnext thing you know\b",
        r"\bthis will lead to\b",
    ],
    "appeal to authority": [
        r"\bexperts (say|agree|claim)\b",
        r"\beveryone knows\b",
        r"\bscience says\b",
    ],
    "hasty generalization": [
        r"\ball [a-z]+ (are|do)\b",
        r"\bevery single (one|time)\b",
        r"\balways happens with\b",
    ],
}


def detect_fallacy(text: str) -> dict:
    """
    Detects common logical fallacies in text using rule-based
    pattern matching (regex over known fallacy phrasings).

    Returns a dict like:
    {
        "has_fallacy": True,
        "detected_fallacies": ["ad hominem"],
        "matches": {
            "ad hominem": ["you're an idiot"]
        }
    }
    """
    text_lower = text.lower()
    detected = {}

    for fallacy_type, patterns in FALLACY_PATTERNS.items():
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text_lower)
            if found:
                matches.append(pattern)
        if matches:
            detected[fallacy_type] = matches

    return {
        "has_fallacy": len(detected) > 0,
        "detected_fallacies": list(detected.keys()),
        "matches": detected,
    }


if __name__ == "__main__":
    sample = "You're an idiot, so your argument is wrong."
    result = detect_fallacy(sample)
    print(result)