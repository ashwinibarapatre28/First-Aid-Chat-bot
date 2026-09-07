import json
import os
from flask import Flask, render_template, jsonify, request

from nlp_classifier import EmergencyNLPClassifier
from services.emergency_detector import EmergencyDetector
from services.decision_tree_engine import DecisionTreeEngine
from services.chatbot_engine import ChatbotEngine

app = Flask(__name__)

# Initialize NLP classifier & Decision Tree engines
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "first_aid_data.json")
SYMPTOMS_PATH = os.path.join(os.path.dirname(__file__), "data", "symptoms_qa_data.json")
TREES_PATH = os.path.join(os.path.dirname(__file__), "data", "decision_trees.json")

classifier = EmergencyNLPClassifier(data_path=DATA_PATH, symptoms_path=SYMPTOMS_PATH)
emergency_detector = EmergencyDetector(classifier)
decision_tree_engine = DecisionTreeEngine(trees_path=TREES_PATH)
chatbot_engine = ChatbotEngine(detector=emergency_detector, tree_engine=decision_tree_engine)

def load_emergency_data():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return []

@app.route("/")
def index():
    emergencies = load_emergency_data()
    return render_template("index.html", emergencies=emergencies)

@app.route("/guide/<emergency_id>")
def emergency_guide(emergency_id):
    emergencies = load_emergency_data()
    item = next((e for e in emergencies if e["id"] == emergency_id), None)
    if not item:
        # Fallback to first emergency if ID not found
        item = emergencies[0] if emergencies else None
    return render_template("emergency.html", emergency=item, all_emergencies=emergencies)

@app.route("/history")
def history_page():
    return render_template("history.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

# --- REST API ENDPOINTS ---

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        payload = request.get_json(force=True)
        message = payload.get("message", "")
        conversation_id = payload.get("conversation_id", None)
        
        result = chatbot_engine.handle_chat(message, conversation_id=conversation_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 400

@app.route("/api/chat/reset", methods=["POST"])
def api_chat_reset():
    try:
        payload = request.get_json(force=True) if request.data else {}
        conversation_id = payload.get("conversation_id", "")
        result = chatbot_engine.reset_chat(conversation_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 400

@app.route("/api/emergencies", methods=["GET"])
def api_get_emergencies():
    emergencies = load_emergency_data()
    return jsonify({"success": True, "count": len(emergencies), "data": emergencies})

@app.route("/api/emergencies/<emergency_id>", methods=["GET"])
def api_get_emergency_by_id(emergency_id):
    emergencies = load_emergency_data()
    item = next((e for e in emergencies if e["id"] == emergency_id), None)
    if item:
        return jsonify({"success": True, "data": item})
    return jsonify({"success": False, "message": "Emergency category not found"}), 404

@app.route("/api/classify", methods=["POST"])
def api_classify_emergency():
    try:
        payload = request.get_json(force=True)
        query = payload.get("query", "")
        gender = payload.get("gender", None)
        
        # Check if query triggers symptom QA
        symptom_qa = classifier.detect_symptom_qa(query, gender=gender)
        if symptom_qa.get("is_symptom_qa"):
            return jsonify({
                "success": True,
                "is_symptom_qa": True,
                "qa_data": symptom_qa
            })

        result = classifier.classify(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 400

@app.route("/api/symptom-qa/categories", methods=["GET"])
def api_get_symptom_categories():
    categories = [
        {"id": s["id"], "name": s["symptom_name"], "question": s["initial_question"]}
        for s in classifier.symptoms_qa
    ]
    return jsonify({"success": True, "data": categories})

@app.route("/api/symptom-qa/start", methods=["POST"])
def api_symptom_qa_start():
    try:
        payload = request.get_json(force=True)
        query = payload.get("query", "")
        symptom_id = payload.get("symptom_id", "")
        gender = payload.get("gender", None)

        if symptom_id:
            symptom = next((s for s in classifier.symptoms_qa if s["id"] == symptom_id), None)
            if symptom:
                valid_opts = classifier._filter_options_by_gender(symptom["options"], gender)
                return jsonify({
                    "success": True,
                    "is_symptom_qa": True,
                    "qa_data": {
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
                })

        qa_res = classifier.detect_symptom_qa(query, gender=gender)
        return jsonify({"success": True, "is_symptom_qa": qa_res.get("is_symptom_qa", False), "qa_data": qa_res})
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 400

@app.route("/api/symptom-qa/answer", methods=["POST"])
def api_symptom_qa_answer():
    try:
        payload = request.get_json(force=True)
        symptom_id = payload.get("symptom_id", "")
        option_id = payload.get("option_id", "")
        gender = payload.get("gender", None)

        result = classifier.evaluate_symptom_answer(symptom_id, option_id, gender=gender)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 400

if __name__ == "__main__":
    print("Starting FirstAid AI Web Server")
    app.run(host="0.0.0.0", port=5000, debug=False)


