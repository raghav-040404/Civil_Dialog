from typing import List, Dict, Any
from backend.services.llm_service import GeminiService, get_prompt_template

class FallacyService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    def detect_fallacies(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans a text for logical fallacies using the Gemini LLM fallacy detection prompt.
        Returns a list of detected fallacy issue dicts, excluding any marked as "none".
        """
        # Load the fallacy prompt template
        template = get_prompt_template("fallacy_prompt.txt")
        prompt = template.replace("{text}", text)
        
        # Query LLM service
        result_json = self.gemini_service.generate_json_response(prompt)
        
        fallacies = result_json.get("fallacies", [])
        
        # Filter out "none" types or empty records
        valid_fallacies = []
        for f in fallacies:
            f_type = f.get("type", "none").strip().lower()
            if f_type != "none" and f_type != "":
                valid_fallacies.append({
                    "type": f_type,
                    "severity": f.get("severity", "low").strip().lower(),
                    "confidence": float(f.get("confidence", 0.8)),
                    "evidence": f.get("evidence", "").strip()
                })
                
        return valid_fallacies
