import uuid
from typing import Dict, Any, Optional
from services.emergency_detector import EmergencyDetector
from services.decision_tree_engine import DecisionTreeEngine

class ChatbotEngine:
    """
    High-level orchestrator for the FirstAid AI decision-tree chatbot system.
    """

    RESET_COMMANDS = {"reset", "start again", "new problem", "restart", "clear"}

    def __init__(self, detector: EmergencyDetector, tree_engine: DecisionTreeEngine):
        self.detector = detector
        self.tree_engine = tree_engine

    def handle_chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        clean_msg = message.strip() if message else ""

        # Check for explicit reset command
        if clean_msg.lower() in self.RESET_COMMANDS:
            self.tree_engine.reset_session(conversation_id)
            return {
                "success": True,
                "message": "Conversation reset. Please describe what happened or what symptoms you are experiencing.",
                "options": [
                    "Pain (Find Location)", "Leg / Foot Pain", "Hand / Arm Pain", "Headache",
                    "Chest Pain", "Vomiting & Nausea", "Someone is Choking", "Severe Bleeding"
                ],
                "conversation_id": conversation_id,
                "emergency": False,
                "reset": True
            }

        session = self.tree_engine.get_session(conversation_id)

        # 1. If active incomplete session exists, try processing as answer
        if session and not session.get("is_complete"):
            res = self.tree_engine.process_answer(conversation_id, clean_msg)
            if res.get("invalid_input"):
                # Input couldn't match current question options.
                # Check if user typed a NEW emergency topic (e.g. "someone is choking" while in chest pain flow)
                new_topic = self.detector.detect_topic(clean_msg)
                if new_topic and new_topic != session.get("topic"):
                    # Switch to new topic decision tree!
                    self.tree_engine.reset_session(conversation_id)
                    res = self.tree_engine.start_conversation(conversation_id, new_topic)

            res["conversation_id"] = conversation_id
            return res

        # 2. No active session (or previous session completed): Detect topic from query
        topic = self.detector.detect_topic(clean_msg)
        if topic:
            res = self.tree_engine.start_conversation(conversation_id, topic)
            res["conversation_id"] = conversation_id
            return res

        # 3. Unknown input fallback
        return {
            "success": False,
            "message": "I want to make sure I understand correctly. Can you describe what happened or select one of the common first-aid topics?",
            "options": [
                "Pain (Find Location)", "Leg / Foot Pain", "Hand / Arm Pain", "Headache",
                "Chest Pain", "Vomiting & Nausea", "Someone is Choking", "Severe Bleeding"
            ],
            "conversation_id": conversation_id,
            "emergency": False
        }

    def reset_chat(self, conversation_id: str) -> Dict[str, Any]:
        self.tree_engine.reset_session(conversation_id)
        return {
            "success": True,
            "message": "Conversation reset. Please describe what happened or what symptoms you are experiencing.",
            "options": [
                "Pain (Find Location)", "Leg / Foot Pain", "Hand / Arm Pain", "Headache",
                "Chest Pain", "Vomiting & Nausea", "Someone is Choking", "Severe Bleeding"
            ],
            "conversation_id": conversation_id,
            "emergency": False,
            "reset": True
        }
