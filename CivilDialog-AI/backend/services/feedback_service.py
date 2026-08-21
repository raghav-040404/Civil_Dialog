from typing import List, Dict, Any
from backend.schemas.llm_schema import Issue

# Static mapping for zero-latency, consistent, and constructive feedback
FEEDBACK_TEMPLATES = {
    "toxic_language": {
        "explanation": "Your text contains offensive or aggressive language.",
        "reason": "Using harsh words can alienate other participants and divert the conversation from productive discussion.",
        "improvement_tip": "Try expressing your frustration or disagreement using neutral, constructive vocabulary."
    },
    "hate_speech": {
        "explanation": "This statement appears to target a specific group of people based on protected characteristics.",
        "reason": "Hate speech is harmful, violates community guidelines, and prevents a safe discussion environment.",
        "improvement_tip": "Please rephrase to focus on ideas and ensure your message does not stereotype or attack groups based on identity."
    },
    "personal_attack": {
        "explanation": "Your comment includes a direct personal attack.",
        "reason": "Attacking another user shifts the focus away from the topic and creates a hostile environment.",
        "improvement_tip": "Criticize the idea or the argument, not the person who made it."
    },
    "ad_hominem": {
        "explanation": "Ad Hominem fallacy detected (attacking the person instead of the argument).",
        "reason": "Attacking a person's intelligence, character, or background does not address the logic of their argument.",
        "improvement_tip": "Address the facts, logic, or merits of the statement, rather than the person's traits."
    },
    "strawman": {
        "explanation": "Strawman fallacy detected (misrepresenting an argument).",
        "reason": "Exaggerating or distorting the other person's point makes it easier to attack, but it doesn't address their actual view.",
        "improvement_tip": "Represent the other person's argument fairly and accurately before presenting your counter-argument."
    },
    "false_dilemma": {
        "explanation": "False Dilemma fallacy detected (presenting only two extreme choices).",
        "reason": "This structure oversimplifies a complex issue by ignoring other valid alternatives or middle ground.",
        "improvement_tip": "Acknowledge middle-ground options or alternative perspectives instead of framing it as an either-or scenario."
    },
    "slippery_slope": {
        "explanation": "Slippery Slope fallacy detected (assuming an inevitable extreme chain of events).",
        "reason": "Arguing that one action will automatically lead to a disastrous outcome without evidence is logically unsound.",
        "improvement_tip": "Focus on the direct, evidence-based consequences of the current proposal instead of projecting an extreme chain reaction."
    },
    "hasty_generalization": {
        "explanation": "Hasty Generalization fallacy detected (drawing broad conclusions from too little evidence).",
        "reason": "Making a sweeping claim based on one or two instances leads to stereotyping and incorrect assumptions.",
        "improvement_tip": "Limit your conclusion to the specific cases you have evidence for, or use qualifiers like 'some' or 'often' instead of 'all' or 'always'."
    },
    "appeal_to_emotion": {
        "explanation": "Appeal to Emotion fallacy detected.",
        "reason": "Relying on emotional reactions (like fear, pity, or guilt) instead of factual evidence can manipulate the debate.",
        "improvement_tip": "Support your argument with logical evidence, data, or objective reasons rather than emotional appeals."
    },
    "irrelevant_argument": {
        "explanation": "Irrelevant argument detected.",
        "reason": "Bringing up points that are unrelated to the core topic distracts from the ongoing discussion.",
        "improvement_tip": "Keep your points directly tied to the specific topic being discussed."
    },
    "none": {
        "explanation": "No communication issues detected.",
        "reason": "Your statement is polite, civil, and constructive.",
        "improvement_tip": "Continue sharing your perspective in this constructive manner!"
    }
}

class FeedbackService:
    def generate_feedback(self, text: str, issues: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generates simple and clear explanations, reasons, and tips from detected issues.
        If multiple issues are present, it selects the one with the highest severity
        to keep UI feedback focused and concise.
        """
        if not issues:
            return FEEDBACK_TEMPLATES["none"]
            
        # Map severities to numeric weights to find the most severe issue
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        
        # Sort issues by severity weight descending
        sorted_issues = sorted(
            issues, 
            key=lambda x: severity_weights.get(x.get("severity", "low").lower(), 1), 
            reverse=True
        )
        
        primary_issue = sorted_issues[0]
        issue_type = primary_issue.get("type", "none").strip().lower()
        
        # Retrieve feedback template or fall back to toxic_language template
        feedback = FEEDBACK_TEMPLATES.get(issue_type, FEEDBACK_TEMPLATES["toxic_language"])
        
        # Customize details if evidence is available
        evidence = primary_issue.get("evidence")
        if evidence and issue_type != "none":
            # Optional: We can dynamically append details based on evidence
            pass
            
        return feedback
