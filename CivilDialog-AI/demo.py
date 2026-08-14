from src.pipeline import analyze_text
import json

if __name__ == "__main__":
    print("CivilDialog AI/NLP Module — Demo")
    print("-" * 40)

    while True:
        text = input("\nEnter a message to analyze (or 'quit' to exit): ")
        if text.lower() == "quit":
            break

        result = analyze_text(text)
        print(json.dumps(result, indent=2))