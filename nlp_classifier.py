import json
import re
import math
from typing import Dict, List, Tuple, Any

class EmergencyNLPClassifier:
    """
    Lightweight Natural Language Processing classifier for identifying
    emergency first-aid intent from unstructured user text.
    """
    
    def __init__(self, data_path: str = "data/first_aid_data.json", symptoms_path: str = "data/symptoms_qa_data.json"):
        self.data_path = data_path
        self.symptoms_path = symptoms_path
        self.emergencies = self._load_data(self.data_path)
        self.symptoms_qa = self._load_data(self.symptoms_path)
        self.stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
            "in", "on", "at", "to", "for", "with", "about", "against", "between",
            "into", "through", "during", "before", "after", "above", "below", "to",
            "from", "up", "down", "in", "out", "off", "over", "under", "again",
            "further", "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "any", "both", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "s", "t", "can", "will", "just", "don", "should", "now",
            "my", "friend", "someone", "person", "help", "please", "having", "got", "have", "i", "suffering", "feel", "feeling"
        }

    def _load_data(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data from {path}: {e}")
            return []

    def preprocess_text(self, text: str) -> List[str]:
        """Clean and tokenize input text."""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation and special characters
        text = re.sub(r"[^\w\s]", " ", text)
        # Tokenize by whitespace
        tokens = text.split()
        # Remove stop words and short noise
        filtered = [t for t in tokens if t not in self.stop_words and len(t) > 1]
        return filtered

    def _filter_options_by_gender(self, options: List[Dict[str, Any]], gender: str = None) -> List[Dict[str, Any]]:
        if not gender or gender.lower() == "other":
            return options

        gender_clean = gender.lower()
        filtered = []
        for opt in options:
            gt = opt.get("gender_target")
            if not gt or gt == gender_clean:
                filtered.append(opt)
        return filtered

    def detect_symptom_qa(self, user_query: str, gender: str = None) -> Dict[str, Any]:
        """
        Detects if the query refers to a specific symptom category requiring Q&A follow-up.
        Supports filtering options based on user gender.
        """
        if not user_query or not user_query.strip():
            return {"is_symptom_qa": False}

        clean_query = user_query.strip().lower()
        tokens = self.preprocess_text(clean_query)

        best_symptom = None
        highest_score = 0.0

        for symptom in self.symptoms_qa:
            keywords = symptom.get("keywords", [])
            sname = symptom.get("symptom_name", "").lower()
            
            # Check exact keyword match
            for kw in keywords:
                if kw in clean_query:
                    valid_opts = self._filter_options_by_gender(symptom["options"], gender)
                    return {
                        "is_symptom_qa": True,
                        "symptom_id": symptom["id"],
                        "symptom_name": symptom["symptom_name"],
                        "question": symptom["initial_question"],
                        "gender": gender,
                        "options": [
                            {
                                "id": opt["id"],
                                "label": opt["label"],
                                "description": opt["description"],
                                "severity": opt["severity"],
                                "is_emergency": opt.get("is_emergency", False),
                                "gender_target": opt.get("gender_target")
                            }
                            for opt in valid_opts
                        ]
                    }
            
            # Check token overlap
            symptom_tokens = set(re.sub(r"[^\w\s]", " ", sname).split())
            overlap = set(tokens).intersection(symptom_tokens)
            if overlap:
                score = len(overlap)
                if score > highest_score:
                    highest_score = score
                    best_symptom = symptom

        if best_symptom and highest_score > 0:
            valid_opts = self._filter_options_by_gender(best_symptom["options"], gender)
            return {
                "is_symptom_qa": True,
                "symptom_id": best_symptom["id"],
                "symptom_name": best_symptom["symptom_name"],
                "question": best_symptom["initial_question"],
                "gender": gender,
                "options": [
                    {
                        "id": opt["id"],
                        "label": opt["label"],
                        "description": opt["description"],
                        "severity": opt["severity"],
                        "is_emergency": opt.get("is_emergency", False),
                        "gender_target": opt.get("gender_target")
                    }
                    for opt in valid_opts
                ]
            }

        return {"is_symptom_qa": False}

    def evaluate_symptom_answer(self, symptom_id: str, option_id: str, gender: str = None) -> Dict[str, Any]:
        """
        Retrieves diagnosis and first-aid recommendations for a selected symptom option.
        """
        symptom = next((s for s in self.symptoms_qa if s["id"] == symptom_id), None)
        if not symptom:
            return {"success": False, "message": "Symptom category not found."}

        option = next((opt for opt in symptom["options"] if opt["id"] == option_id), None)
        if not option:
            return {"success": False, "message": "Selected symptom option not found."}

        return {
            "success": True,
            "symptom_id": symptom_id,
            "symptom_name": symptom["symptom_name"],
            "subtype_name": option["subtype_name"],
            "severity": option["severity"],
            "gender": gender,
            "is_emergency": option.get("is_emergency", False),
            "warning": option["warning"],
            "first_aid_steps": option["first_aid_steps"],
            "when_to_see_doctor": option["when_to_see_doctor"]
        }

    def _calculate_match_score(self, query_text: str, query_tokens: List[str], item: Dict[str, Any]) -> float:
        score = 0.0
        
        keywords = item.get("keywords", [])
        title = item.get("title", "").lower()
        desc = item.get("description", item.get("short_description", "")).lower()
        
        # 1. Exact phrase in query matches keyword or title
        for kw in keywords:
            kw_clean = kw.lower()
            if kw_clean in query_text:
                # Direct phrase match carries high weight
                score += 3.0
            else:
                # Token overlap in keyword
                kw_tokens = set(kw_clean.split())
                overlap = set(query_tokens).intersection(kw_tokens)
                if overlap:
                    score += 1.2 * len(overlap)
                    
        # 2. Title token matching
        title_tokens = set(re.sub(r"[^\w\s]", " ", title).split())
        title_overlap = set(query_tokens).intersection(title_tokens) - self.stop_words
        score += 2.0 * len(title_overlap)
        
        # 3. Description matching
        desc_tokens = set(re.sub(r"[^\w\s]", " ", desc).split())
        desc_overlap = set(query_tokens).intersection(desc_tokens) - self.stop_words
        score += 0.4 * len(desc_overlap)
        
        # Normalize score
        max_possible = 6.0
        normalized = min(score / max_possible, 1.0)
        return round(normalized, 3)

    def classify(self, user_query: str) -> Dict[str, Any]:
        """
        Classifies user query into closest emergency category or triggers symptom Q&A follow-up.
        """
        if not user_query or not user_query.strip():
            return {
                "success": False,
                "message": "Please enter a description of the emergency or symptom.",
                "confidence": 0.0,
                "emergency": None
            }

        # First check if query matches a symptom Q&A decision tree
        symptom_qa = self.detect_symptom_qa(user_query)
        if symptom_qa.get("is_symptom_qa"):
            return {
                "success": True,
                "is_symptom_qa": True,
                "qa_data": symptom_qa
            }
            
        clean_query = user_query.strip().lower()
        tokens = self.preprocess_text(clean_query)
        
        best_match = None
        highest_score = 0.0
        
        for item in self.emergencies:
            score = self._calculate_match_score(clean_query, tokens, item)
            if score > highest_score:
                highest_score = score
                best_match = item
                
        # Confidence thresholding
        CONFIDENCE_THRESHOLD = 0.18
        
        if highest_score < CONFIDENCE_THRESHOLD or not best_match:
            return {
                "success": False,
                "confidence": highest_score,
                "message": "I couldn't confidently identify the situation. Please describe your symptom (e.g., 'headache', 'chest pain', 'stomach ache') or select an emergency category directly.",
                "emergency": None
            }
            
        return {
            "success": True,
            "confidence": highest_score,
            "message": f"Identified Possible Emergency: {best_match['title']}",
            "emergency": best_match
        }

# Quick test helper when executed directly
if __name__ == "__main__":
    classifier = EmergencyNLPClassifier()
    test_queries = [
        "I have a headache",
        "Chest pain radiating to my arm",
        "Someone is choking and cannot breathe!",
        "Stomach ache"
    ]
    for q in test_queries:
        res = classifier.classify(q)
        print(f"Query: '{q}' -> Result: {res}")
