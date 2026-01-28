🌱 Smart Plant Growth Assistant (AI-Powered)

An AI-driven plant guidance system that helps users grow and maintain plants successfully—from planting to full maturity—using personalized, stage-wise care plans powered by artificial intelligence.

📌 Overview

The Smart Plant Growth Assistant is designed to act as a continuous AI gardening companion. Users provide plant-specific details through an interactive interface, and the system generates customized plant care guidance covering the entire lifecycle of the plant.

By leveraging Google Gemini AI for intelligent analysis and NotebookLM (or mock services) for visual content generation, the platform delivers both actionable insights and easy-to-understand visual guides, making plant care accessible even for beginners.

✨ Key Features

🌿 Personalized Plant Care Plans

📊 Stage-wise Growth Guidance

💧 Smart watering & fertilizer recommendations

🐛 Disease prevention & early warning signs

🧠 AI-generated expert insights using Gemini

🖼️ Visual guides (presentations / illustrations)

⚡ Fast, scalable backend using FastAPI

🧪 Fully tested API endpoints

🧠 How It Works

User submits plant details via frontend form

Backend validates input using Pydantic

Gemini AI analyzes data and generates structured plant care guidance

NotebookLM (or mock service) converts guidance into visual assets

Combined response is returned to the frontend for display

🏗️ System Architecture
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/Vue/etc)                  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Plant Input  │  │ Care Guide   │  │ Visual Guide │          │
│  │    Form      │  │   Display    │  │   Viewer     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (main.py)                   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    CORS Middleware                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  API Routes (routes/plant.py)             │  │
│  │                                                            │  │
│  │  • GET  /health                                           │  │
│  │  • POST /generate-plant-guide                            │  │
│  │  • GET  /                                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Pydantic Validation (schemas/plant.py)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│          ┌─────────────────┴─────────────────┐                 │
│          ▼                                     ▼                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │  Gemini Service  │              │ NotebookLM Service│        │
│  │  (AI Analysis)   │              │ (Visual Content)  │        │
│  └──────────────────┘              └──────────────────┘        │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │       Response Formatter (utils/formatter.py)             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

🔁 Request Flow
1. User Input
   └──> Frontend Form
        └──> POST /generate-plant-guide

2. Backend Processing
   └──> FastAPI
        └──> Pydantic Validation
             ├──> Gemini AI Analysis
             └──> NotebookLM Visual Generation

3. Response Formatting
   └──> Combined structured response

4. Frontend Display
   └──> Care guide + visual assets

📦 Data Flow
PlantInputData
   ├──> GeminiResponse
   │     ├── plant_overview
   │     ├── growth_stages
   │     ├── daily_care
   │     ├── common_problems
   │     └── additional_tips
   │
   ├──> NotebookLMResponse
   │     ├── file_url
   │     ├── file_type
   │     └── status
   │
   └──> PlantGuideResponse (Final Output)

🧩 Module Dependencies
main.py
 ├── app/routes/plant.py
 │    ├── app/schemas/plant.py
 │    ├── app/services/gemini.py
 │    ├── app/services/notebooklm.py
 │    └── app/utils/formatter.py
 └── app/utils/config.py

⚙️ Technology Stack
Backend

FastAPI – High-performance Python web framework

Pydantic – Data validation & serialization

Uvicorn – ASGI server

HTTPX – Async HTTP client

AI & Integrations

Google Gemini API – AI text & reasoning engine

NotebookLM API (or Mock Service) – Visual content generation

🚀 Running the Project
1️⃣ Install Dependencies
python -m pip install -r requirements.txt

2️⃣ Start Backend Server
python -m uvicorn app.main:app --reload


Server runs at:
👉 http://localhost:8000

3️⃣ API Documentation

Swagger UI: http://localhost:8000/docs

Health Check: GET /health

4️⃣ Run API Tests
python test_api.py

🔐 Environment Variables
GEMINI_API_KEY=your_api_key_here
NOTEBOOKLM_API_KEY=your_api_key_here
DEBUG=true


If API keys are not provided, the system automatically switches to mock responses for development and testing.

🎯 Use Cases

Beginner gardeners

Home plant enthusiasts

Urban farming solutions

Educational & agricultural platforms

AI-powered sustainability tools

📈 Future Enhancements

User authentication & profiles

Plant history tracking

Weather-based dynamic care updates

Mobile app integration

Image-based plant disease detection

🏁 Conclusion

The Smart Plant Growth Assistant combines modern backend architecture with AI-driven intelligence to deliver an end-to-end plant care solution. It demonstrates scalable system design, clean API architecture, and real-world AI integration—making it suitable for production use, hackathons, and portfolio showcases.
