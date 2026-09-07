import re
from typing import Optional, Dict, Any
from nlp_classifier import EmergencyNLPClassifier

class EmergencyDetector:
    """
    Detects emergency topics from natural language input using NLP classification
    and keyword mapping to decision tree topic IDs.
    """
    def __init__(self, nlp_classifier: EmergencyNLPClassifier):
        self.classifier = nlp_classifier
        
        # Direct keyword to decision tree topic ID mapping
        self.topic_mapping = {
            # Chest pain
            "chest_pain": ["chest pain", "chest hurt", "chest pressure", "chest tightness", "heart pain", "pain in chest", "angina", "cardiac"],
            # CPR / Unconscious
            "cpr": ["cpr", "cardiac arrest", "unresponsive", "stopped breathing", "no pulse", "unconscious person", "passed out cold", "collapse"],
            # Choking
            "choking": ["choking", "choke", "airway blocked", "cannot breathe", "food stuck", "strangling", "throat blocked", "heimlich"],
            # Severe bleeding
            "severe_bleeding": ["bleeding", "severe bleeding", "hemorrhage", "gushing blood", "spurting blood", "blood loss", "bleeding heavily", "bleeding badly"],
            # Burns
            "burns": ["burn", "burns", "scald", "fire", "hot water", "charred", "blister", "chemical burn", "thermal burn", "hand burned", "got burned"],
            # Fractures
            "fractures": ["fracture", "broken bone", "broken arm", "broken leg", "dislocation", "fractured", "snapped bone", "bone broken"],
            # Fainting
            "fainting": ["fainting", "fainted", "syncope", "passed out", "blackout", "dizzy collapse", "friend fainted", "person fainted"],
            # Seizures
            "seizures": ["seizure", "fit", "convulsion", "epilepsy", "epileptic", "shaking uncontrollably", "spasm"],
            # Electric shock
            "electric_shock": ["electric shock", "electrocution", "electric current", "shocked by wire", "live wire", "high voltage"],
            # Poisoning
            "poisoning": ["poisoning", "poison", "swallowed chemical", "overdose", "toxic ingestion", "acid swallowed", "pesticide"],
            # Heat stroke
            "heat_stroke": ["heat stroke", "heat exhaustion", "sunstroke", "overheating", "high body temp"],
            # Nosebleed
            "nosebleed": ["nosebleed", "epistaxis", "bleeding nose", "nose blood", "bloody nose"],
            # Allergic reaction
            "allergic_reaction": ["allergic reaction", "anaphylaxis", "allergy", "epipen", "bee sting", "swollen throat", "hives allergy"],
            # Sprains
            "sprains": ["sprain", "strain", "twisted ankle", "ligament", "swollen joint", "pulled muscle", "ankle sprain"],
            # Cuts and wounds
            "cuts_and_wounds": ["cut", "cuts", "minor wound", "scrape", "laceration", "bleeding cut", "scratched", "bandage"],
            # Medical shock
            "shock": ["medical shock", "circulatory shock", "clammy skin shock", "trauma shock", "state of shock"],
            # Headache
            "headache": ["headache", "head pain", "migraine", "head throbbing", "pain in head", "head hurt", "temple pain", "forehead pain"],
            # Vomiting and Nausea
            "nausea_vomiting": ["vomiting", "vomit", "nausea", "throwing up", "puking", "nauseous", "sick to stomach", "upset stomach", "food poisoning"],
            # Fever
            "fever": ["fever", "high temperature", "chills", "feeling hot", "body temperature", "feverish", "high fever", "pyrexia"],
            # Abdominal Pain
            "abdominal_pain": ["abdominal pain", "stomach ache", "belly pain", "stomach pain", "stomach cramp", "appendix", "abdominal cramp", "gastritis"],
            # Dizziness
            "dizziness": ["dizziness", "dizzy", "vertigo", "lightheaded", "spinning head", "unsteady", "lightheadedness"],
            # Hand and Arm Pain
            "hand_pain": [
                "hand pain", "arm pain", "wrist pain", "finger pain", "hand hurt", "pain in hand", "pain in arm",
                "wrist hurt", "thumb pain", "knuckle pain", "palm pain", "elbow pain", "left arm pain", "left hand pain",
                "left arm", "left hand", "right arm", "right hand", "pain in left arm", "pain in left hand",
                "thumb", "little finger", "middle finger", "index finger", "ring finger", "pinky", "pinky pain",
                "pain in finger", "finger hurt", "thumb hurt", "little finger pain", "middle finger pain"
            ],
            # Leg and Foot Pain
            "leg_pain": ["leg pain", "foot pain", "knee pain", "calf pain", "thigh pain", "ankle pain", "leg hurt", "foot hurt", "knee hurt", "pain in leg", "pain in foot", "pain in knee", "shin pain", "toe pain", "heel pain"],
            # Joint and Back Pain
            "joint_back_pain": ["back pain", "joint pain", "spine pain", "lumbar pain", "pain in back", "back hurt", "spinal pain", "hip pain"],
            # General / Disambiguation Pain (Checked after specific pain keywords)
            "general_pain": ["pain", "i have pain", "feeling pain", "body pain", "hurting", "pain in body", "severe pain", "sharp pain", "dull pain", "ache", "body ache", "discomfort"]
        }

    def detect_topic(self, text: str) -> Optional[str]:
        if not text or not text.strip():
            return None
            
        clean_text = text.strip().lower()
        
        # 1. First check explicit keyword phrases for exact decision tree topics
        for topic_id, keywords in self.topic_mapping.items():
            for kw in keywords:
                if kw in clean_text:
                    return topic_id

        # 2. Check symptom QA classifier
        symptom_qa = self.classifier.detect_symptom_qa(clean_text)
        if symptom_qa.get("is_symptom_qa"):
            sym_id = symptom_qa.get("symptom_id", "")
            symptom_map = {
                "headache": "headache",
                "nausea-vomiting": "nausea_vomiting",
                "fever": "fever",
                "abdominal-pain": "abdominal_pain",
                "dizziness": "dizziness",
                "chest-pain": "chest_pain",
                "hand-pain": "hand_pain",
                "leg-pain": "leg_pain",
                "joint-back-pain": "joint_back_pain",
                "general-pain": "general_pain"
            }
            if sym_id in symptom_map:
                return symptom_map[sym_id]

        # 3. Fall back to NLP classifier standard classification
        res = self.classifier.classify(clean_text)
        if res.get("success") and res.get("emergency"):
            emerg_id = res["emergency"].get("id", "")
            # Map emergency JSON id to decision tree topic key
            id_map = {
                "cpr": "cpr",
                "choking": "choking",
                "severe-bleeding": "severe_bleeding",
                "burns": "burns",
                "fractures": "fractures",
                "fainting": "fainting",
                "seizures": "seizures",
                "electric-shock": "electric_shock",
                "poisoning": "poisoning",
                "heat-stroke": "heat_stroke",
                "nosebleed": "nosebleed",
                "allergic-reaction": "allergic_reaction",
                "sprains": "sprains",
                "cuts-and-wounds": "cuts_and_wounds",
                "shock": "shock",
                "chest-pain": "chest_pain",
                "headache": "headache",
                "nausea-vomiting": "nausea_vomiting",
                "fever": "fever",
                "abdominal-pain": "abdominal_pain",
                "dizziness": "dizziness",
                "hand-pain": "hand_pain",
                "leg-pain": "leg_pain",
                "joint-back-pain": "joint_back_pain",
                "general-pain": "general_pain"
            }
            if emerg_id in id_map:
                return id_map[emerg_id]

        return None
