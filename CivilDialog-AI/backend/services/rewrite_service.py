from typing import List, Dict, Any, Optional
from backend.services.llm_service import GeminiService, get_prompt_template

class RewriteService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    def generate_rewrite(self, text: str, detected_issues: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Rewrites a piece of text to be civil and respectful while preserving the original intent.
        Optionally uses a list of detected issues to guide the rewrite.
        """
        # Load rewrite template
        template = get_prompt_template("rewrite_prompt.txt")
        
        issues_str = "None"
        if detected_issues:
            issues_str = ", ".join([f"{issue.get('type')} (severity: {issue.get('severity')})" for issue in detected_issues])
            
        prompt = template.replace("{text}", text).replace("{issues}", issues_str)
        
        # Query LLM service
        result_json = self.gemini_service.generate_json_response(prompt)
        
        return {
            "rewrite": result_json.get("rewrite", text),
            "original_intent_preserved": result_json.get("original_intent_preserved", True)
        }
