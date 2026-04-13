🚀 INTENTA — AI-Native Intent-Centric Software Development System

From Intent to System — Fully Local, Fully Autonomous

⸻



⸻

🎥 Demo

<p align="center">
  <img src="./assets/demo.gif" width="800"/>
</p>



⸻

📱 UI Preview

<p align="center">
  <img src="./assets/1.png" width="250"/>
  <img src="./assets/2.png" width="250"/>
  <img src="./assets/3.png" width="250"/>
</p>



⸻

🏗️ Architecture Diagram

<p align="center">
  <img src="./assets/architecture.png" width="800"/>
</p>



⸻

🧠 Overview

INTENTA is an AI-native platform that converts plain-English business intent into a complete enterprise-grade system design — fully offline, without any external APIs.

User Intent (text)
        ↓
INTENTA SuperAgent
        ↓
Local LLM + Rule Engine + Templates
        ↓
Enterprise System Design Output


⸻

✨ Key Features
	•	🔒 100% Local AI (No OpenAI / No Cloud APIs)
	•	🧠 Hybrid Intelligence (LLM + Rules + Templates)
	•	🏗️ Automated System Architecture Generation
	•	📊 Explainability & Risk Analysis
	•	🛡️ Compliance Mapping (GDPR, SOC2)
	•	🔐 Secure Authentication (JWT-based)
	•	🐳 Docker-ready deployment

⸻

🏗️ System Architecture

React Native (Frontend)
        ↓
FastAPI Backend
        ↓
INTENTA SuperAgent
        ↓
Ollama (Docker) → Mistral
        ↓
MongoDB


⸻

🤖 INTENTA SuperAgent

Module	Description
Intent Parser	Extracts structured intent
Architecture Generator	Chooses system pattern
Tech Stack Selector	Selects technologies
Code Blueprint Generator	Generates APIs & structure
Validation Engine	Defines testing strategy
Compliance Engine	Handles GDPR, SOC2
Governance Engine	RBAC roles & workflows
Explainability Engine	Explains decisions


⸻

🧠 Hybrid Intelligence Model

LLM → reasoning
Rules → correctness
Templates → structured output

Example:
	•	IF scale = high → microservices
	•	IF GDPR → encryption + audit logging

⸻

🚀 Quick Start

🐳 Run Full System

docker-compose up --build


⸻

⚙️ Backend Setup

cd backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload


⸻

📱 Frontend Setup

cd frontend

npm install
npx expo start


⸻

📡 API

POST /generate

Request

{
  "input": "Build a scalable fintech app with GDPR compliance"
}

Response

{
  "intent": {},
  "architecture": {},
  "tech_stack": {},
  "code_blueprint": {},
  "validation": {},
  "compliance": {},
  "governance": {},
  "explainability": {}
}


⸻

🔐 Authentication
	•	Email/password login
	•	Password hashing (bcrypt)
	•	JWT-based authentication
	•	MongoDB user storage

⸻

🗄️ Database
	•	MongoDB (local)
	•	Stores:
	•	Users
	•	Inputs
	•	Outputs
	•	Logs

⸻

📊 Observability
	•	Structured logging
	•	Error tracking
	•	Audit trail

⸻

🧪 Testing

pytest


⸻

🧱 Project Structure
<p>
intenta/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── auth/
│   │   ├── core/
│   │   ├── db/
│   │   └── main.py
├── frontend/
├── docker-compose.yml
├── README.md
</p>

⸻

🐳 Deployment

docker-compose up --build


⸻

🔥 Why INTENTA?

Traditional Tools	INTENTA
Static templates	AI-driven system design
No explainability	Full transparency
Cloud dependent	Fully local
Manual design	Automated architecture


⸻

🎯 Use Cases
	•	Enterprise system design
	•	Architecture prototyping
	•	AI-assisted development
	•	Compliance-aware engineering

⸻

🚀 Future Roadmap
	•	Multi-agent orchestration
	•	Code generation (files output)
	•	Vector database integration
	•	Kubernetes deployment

⸻

👨‍💻 Author

Built as a production-grade AI system.

⸻

📄 License

MIT License
:::

⸻

