# FirstAid AI – Emergency First-Aid Assistant

**Tagline:** *"Immediate Guidance. Clear Actions. Safer Decisions."*

FirstAid AI is a modern, responsive web application designed to provide immediate, clear, step-by-step first-aid guidance during common medical emergencies.
python -m venv venv
---

## 🚨 Medical Disclaimer
> **IMPORTANT:** FirstAid AI provides general first-aid information for educational guidance only. It is **not** a replacement for professional medical care, paramedics, or doctors. In any life-threatening situation, contact emergency medical services immediately (Dial **112** in India or your local emergency number).

---

## ✨ Features
1. **15 Predefined Emergency Categories**: Detailed step-by-step first-aid protocols for CPR, Choking, Severe Bleeding, Burns, Fractures, Fainting, Seizures, Electric Shock, Poisoning, Heat Stroke, Nosebleed, Allergic Reaction, Sprains, Cuts & Wounds, and Shock.
2. **AI Intent Classifier (NLP)**: Custom lightweight NLP engine matching natural language inputs (e.g., *"My friend is choking"*) to emergency categories.
3. **Interactive AI Assistant Chatbot**: Drawer widget providing instant recommendations and direct guide links based on user description.
4. **Voice Assistance (Text-to-Speech)**: Hands-free Web Speech API integration with Play, Pause, Stop controls and active text highlighting.
5. **Interactive Step Pager**: Step-by-step card navigation with explicit DO NOTs and when-to-call emergency triggers.
6. **Response Timer**: Integrated stopwatch (00:00) for timing CPR compressions, pressure application, or cooling procedures.
7. **Quick Emergency Mode**: High-contrast, minimal UI overlay with ultra-large text for rapid emergency assistance.
8. **One-Touch Emergency Access**: Prominent global **CALL 112** mobile button.
9. **Dynamic Search**: Instant keyword search filtering emergency cards.
10. **LocalStorage User History**: Persisted history tracking viewed topics with timestamp.

---

## 🛠️ Technology Stack
- **Backend**: Python 3.x, Flask (REST APIs & Page Routing)
- **NLP Engine**: Custom tokenization, weighted n-gram & TF-IDF similarity scoring
- **Frontend**: HTML5, CSS3 (Vanilla design system with CSS custom properties), Modern JS (ES6+)
- **Voice Engine**: Browser Web Speech API (`speechSynthesis`)
- **Icons**: Lucide Icons
- **Database**: Structured JSON (`data/first_aid_data.json`)

---

## 🚀 Quick Start Guide (Localhost Execution)

### 1. Prerequisites
Ensure Python 3.8+ is installed on your system.

### 2. Install Dependencies
Open terminal/command prompt in the project root directory and run:
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
Start the Flask web server:
```bash
python app.py
```

### 4. Open in Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 📁 Project Structure
```text
NLP Project 2/
│
├── app.py                     # Flask web server & REST endpoints
├── nlp_classifier.py          # Custom NLP Emergency Intent Classifier
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── data/
│   └── first_aid_data.json    # JSON dataset (15 emergency categories)
├── templates/
│   ├── index.html             # Main Dashboard & Grid
│   ├── emergency.html         # Step-by-Step Guidance & Timer
│   ├── history.html           # User Topic History page
│   └── about.html             # Project & Disclaimer info
└── static/
    ├── css/
    │   └── style.css          # Healthcare UI CSS Design System
    └── js/
        ├── script.js          # Main UI controller & LocalStorage
        ├── chatbot.js         # Chatbot REST API client
        ├── voice.js           # Web Speech API voice reader
        └── emergency_mode.js  # Quick Emergency Mode logic
```

---

## 📡 REST API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/emergencies` | `GET` | Returns list of all 15 emergency categories |
| `/api/emergencies/<id>` | `GET` | Returns detailed data for a specific emergency ID |
| `/api/classify` | `POST` | Accepts `{ "query": "..." }`, returns top matched category with confidence score |
