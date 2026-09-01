import json
import os
from typing import Dict, Any, Optional, List, Tuple

class DecisionTreeEngine:
    """
    Engine to manage decision tree loading, active conversation state traversal,
    option matching, evaluator rules execution, and urgency/guidance generation.
    """

    def __init__(self, trees_path: str = "data/decision_trees.json"):
        self.trees_path = trees_path
        self.trees = self._load_trees()
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def _load_trees(self) -> Dict[str, Any]:
        try:
            with open(self.trees_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading decision trees from {self.trees_path}: {e}")
            return {}

    def start_conversation(self, conversation_id: str, topic_id: str) -> Dict[str, Any]:
        """
        Starts a new decision tree flow for the given topic.
        """
        tree = self.trees.get(topic_id)
        if not tree:
            return {"error": f"Topic '{topic_id}' not found."}

        start_node_id = tree.get("start_node")
        state = {
            "topic": topic_id,
            "current_node": start_node_id,
            "answers": {},
            "is_complete": False
        }
        self.sessions[conversation_id] = state

        return self._render_node(conversation_id, topic_id, start_node_id)

    def process_answer(self, conversation_id: str, user_input: str) -> Dict[str, Any]:
        """
        Processes a user's answer or option selection for an active conversation.
        """
        state = self.sessions.get(conversation_id)
        if not state or state.get("is_complete"):
            return {"error": "No active conversation state found."}

        topic_id = state["topic"]
        node_id = state["current_node"]
        tree = self.trees.get(topic_id, {})
        nodes = tree.get("nodes", {})
        current_node = nodes.get(node_id, {})

        if current_node.get("type") != "question":
            return {"error": "Current state is not expecting an answer."}

        options = current_node.get("options", [])
        matched_option = self._match_user_input(user_input, options)

        if not matched_option:
            # Could not understand selection, return question again with friendly guidance
            response = self._render_node(conversation_id, topic_id, node_id)
            response["message"] = f"I didn't quite catch that. {current_node.get('question')}"
            response["invalid_input"] = True
            return response

        # Store answer
        state["answers"][node_id] = matched_option["value"]

        # Check if option transitions directly to a new topic decision tree
        if matched_option.get("next_topic"):
            next_topic = matched_option["next_topic"]
            return self.start_conversation(conversation_id, next_topic)

        next_node_id = matched_option.get("next_node")

        # Advance state
        return self._advance_to_node(conversation_id, topic_id, next_node_id)

    def _match_user_input(self, user_input: str, options: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not user_input or not options:
            return None

        clean_input = user_input.strip().lower()

        # 1. Exact value match or label match
        for opt in options:
            if clean_input == opt["value"].lower() or clean_input == opt["label"].lower():
                return opt

        # 2. Number choice (e.g. "1", "2", "3")
        if clean_input.isdigit():
            idx = int(clean_input) - 1
            if 0 <= idx < len(options):
                return options[idx]

        # 3. Substring / keyword match in label or value
        for opt in options:
            label_clean = opt["label"].lower()
            val_clean = opt["value"].lower()
            if clean_input in label_clean or label_clean in clean_input:
                return opt
            if clean_input in val_clean or val_clean in clean_input:
                return opt

        # 4. Partial word overlap
        input_words = set(clean_input.split())
        best_opt = None
        best_score = 0
        for opt in options:
            opt_words = set(opt["label"].lower().split())
            overlap = len(input_words.intersection(opt_words))
            if overlap > best_score:
                best_score = overlap
                best_opt = opt

        if best_opt and best_score > 0:
            return best_opt

        return None

    def _advance_to_node(self, conversation_id: str, topic_id: str, node_id: str) -> Dict[str, Any]:
        tree = self.trees.get(topic_id, {})
        nodes = tree.get("nodes", {})
        node = nodes.get(node_id, {})

        if node.get("type") == "evaluator":
            # Process evaluator rules
            state = self.sessions.get(conversation_id, {})
            answers = state.get("answers", {})
            next_node = node.get("default_node")
            
            for rule in node.get("rules", []):
                req_answers = rule.get("if_answers", {})
                match = all(answers.get(k) == v for k, v in req_answers.items())
                if match:
                    next_node = rule.get("next_node")
                    break
            
            return self._advance_to_node(conversation_id, topic_id, next_node)

        # Update active node in session
        state = self.sessions.get(conversation_id)
        if state:
            state["current_node"] = node_id
            if node.get("type") == "result":
                state["is_complete"] = True

        return self._render_node(conversation_id, topic_id, node_id)

    def _render_node(self, conversation_id: str, topic_id: str, node_id: str) -> Dict[str, Any]:
        tree = self.trees.get(topic_id, {})
        nodes = tree.get("nodes", {})
        node = nodes.get(node_id, {})
        node_type = node.get("type")
        state = self.sessions.get(conversation_id, {})

        if node_type == "question":
            options_labels = [opt["label"] for opt in node.get("options", [])]
            return {
                "success": True,
                "message": node.get("question"),
                "options": options_labels,
                "option_details": node.get("options", []),
                "conversation_state": {
                    "topic": topic_id,
                    "current_question": node_id,
                    "answers": state.get("answers", {})
                },
                "emergency": False,
                "is_complete": False
            }

        elif node_type == "result":
            return {
                "success": True,
                "title": node.get("title", "First-Aid Guidance"),
                "message": node.get("message"),
                "warning": node.get("warning"),
                "guidance": node.get("guidance", []),
                "urgency": node.get("urgency", "LOW"),
                "emergency": node.get("emergency", False),
                "options": ["Start Again / Reset"],
                "conversation_state": {
                    "topic": topic_id,
                    "current_question": node_id,
                    "answers": state.get("answers", {})
                },
                "is_complete": True
            }

        return {"error": "Invalid node."}

    def get_session(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(conversation_id)

    def reset_session(self, conversation_id: str):
        if conversation_id in self.sessions:
            del self.sessions[conversation_id]
