import spacy
import nltk
from nltk.tokenize import word_tokenize

# Load spaCy's small English model (make sure it's downloaded — see requirements below)
nlp = spacy.load("en_core_web_sm")


def preprocess_text(text: str) -> dict:
    """
    Runs basic NLP preprocessing on a piece of text:
    - Tokenization
    - POS tagging
    - Lemmatization
    - Stopword flagging

    Returns a dict so downstream stages (toxicity, hate speech, fallacy)
    can consume structured data instead of raw text.
    """
    doc = nlp(text)

    tokens = []
    for token in doc:
        tokens.append({
            "text": token.text,
            "lemma": token.lemma_,
            "pos": token.pos_,
            "is_stop": token.is_stop,
            "is_punct": token.is_punct,
        })

    return {
        "original_text": text,
        "tokens": tokens,
        "num_tokens": len(tokens),
    }


if __name__ == "__main__":
    sample = "You are stupid. Nobody agrees with you."
    result = preprocess_text(sample)
    for tok in result["tokens"]:
        print(tok)