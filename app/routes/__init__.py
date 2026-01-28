"""Service modules for external API integrations."""

from .gemini import gemini_service
from .notebooklm import notebooklm_service

__all__ = ["gemini_service", "notebooklm_service"]

"""
╔═══════════════════════════════════════════════════════════════════════════╗
║        PLANTCARE BACKEND & FRONTEND INTEGRATION GUIDE - v1.0             ║
╚═══════════════════════════════════════════════════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ SYSTEM ARCHITECTURE
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Frontend (React)                    Backend (FastAPI)               External APIs
├─ App.jsx                          ├─ main.py                      ├─ Gemini AI
├─ components/                      ├─ app/                         └─ NotebookLM
│  ├─ PlantForm.jsx                 │  ├─ routes/
│  ├─ Loading.jsx                   │  │  ├─ __init__.py
│  ├─ PlantOverview.jsx             │  │  ├─ gemini.py
│  ├─ GrowthStage.jsx               │  │  └─ notebooklm.py
│  ├─ DailyCare.jsx                 │  ├─ services/
│  ├─ Problem.jsx                   │  │  ├─ __init__.py
│  ├─ VisualGuide.jsx               │  │  ├─ plant.py
│  └─ ExtraTips.jsx                 │  │  └─ ppt_service.py
└─ services/                        │  ├─ schemas/
   └─ api.js                        │  │  ├─ __init__.py
                                    │  │  └─ plant.py
                                    │  └─ utils/

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ BACKEND SETUP
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. INSTALL DEPENDENCIES
   > pip install fastapi uvicorn pydantic httpx python-pptx python-dotenv

2. CREATE .env FILE in backend/
   GEMINI_API_KEY=your_gemini_api_key
   NOTEBOOKLM_API_KEY=your_notebooklm_api_key
   DEBUG=False
   API_HOST=0.0.0.0
   API_PORT=8000
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173

3. DIRECTORY STRUCTURE
   backend/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── routes/
   │   │   ├── __init__.py
   │   │   ├── gemini.py
   │   │   └── notebooklm.py
   │   ├── services/
   │   │   ├── __init__.py
   │   │   ├── plant.py
   │   │   └── ppt_service.py
   │   ├── schemas/
   │   │   ├── __init_.py
   │   │   └── plant.py
   │   └── utils/
   │       └── __init__.py
   ├── generated_files/  (auto-created for PPT outputs)
   ├── .env
   ├── .env.example
   └── requirements.txt

4. RUN BACKEND
   > cd backend
   > python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   API will be available at: http://localhost:8000
   API Docs: http://localhost:8000/docs

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ FRONTEND SETUP
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. INSTALL DEPENDENCIES
   > cd frontend
   > npm install

2. CREATE .env.local
   REACT_APP_API_URL=http://localhost:8000

3. DIRECTORY STRUCTURE
   frontend/
   ├── public/
   ├── src/
   │   ├── App.jsx
   │   ├── App.css
   │   ├── components/
   │   │   ├── PlantForm.jsx
   │   │   ├── PlantForm.css
   │   │   ├── Loading.jsx
   │   │   ├── Loading.css
   │   │   ├── PlantOverview.jsx
   │   │   ├── PlantOverview.css
   │   │   ├── GrowthStage.jsx
   │   │   ├── GrowthStage.css
   │   │   ├── DailyCare.jsx
   │   │   ├── DailyCare.css
   │   │   ├── Problem.jsx
   │   │   ├── Problem.css
   │   │   ├── VisualGuide.jsx
   │   │   ├── ExtraTips.jsx
   │   │   └── services/
   │   │       └── api.js
   │   └── index.js (or main.jsx for Vite)
   ├── .env.local
   └── package.json

4. RUN FRONTEND (Development)
   > npm run dev
   Frontend will be available at: http://localhost:5173 (Vite) or http://localhost:3000 (CRA)

   For Production:
   > npm run build

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ API ENDPOINTS
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

GET /
  Returns: API information and available endpoints

GET /health
  Returns: {"status": "healthy", "message": "...", "version": "1.0.0"}

POST /generate-plant-guide
  Request Body: {
    "plant_name": "Tomato",
    "plant_type": "Vegetable",
    "climate": "Temperate",
    "sunlight_hours": 6,
    "soil_type": "Loamy",
    "watering_frequency": "Daily",
    "experience_level": "Beginner"
  }
  Returns: {
    "success": true,
    "plant_care_guidance": {...},
    "visual_guide": {...},
    "metadata": {...}
  }

GET /files/{filename}
  Returns: Generated PPT file for download

GET /docs
  Swagger UI for interactive API documentation

GET /redoc
  ReDoc for alternative API documentation

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ REQUEST/RESPONSE FLOW
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. User fills PlantForm and submits
   └─> App.jsx calls generatePlantGuide(formData)

2. Frontend transforms data and sends POST request
   └─> API_BASE_URL/generate-plant-guide

3. Backend receives and validates with Pydantic
   └─> PlantInputData schema validation

4. Gemini Service generates plant care guidance
   └─> Constructs prompt with plant data
   └─> Calls Google Gemini API
   └─> Parses JSON response to GeminiResponse

5. PPT Service creates visual guide
   └─> Converts GeminiResponse to presentation structure
   └─> Generates PPTX file using python-pptx
   └─> Returns file URL (NotebookLMResponse)

6. Response Formatter combines outputs
   └─> Creates PlantGuideResponse with:
       ├── success: bool
       ├── plant_care_guidance: GeminiResponse
       ├── visual_guide: NotebookLMResponse
       └── metadata: dict with timestamp, processing_time, etc.

7. Frontend receives response and displays results
   └─> Shows PlantOverview component
   └─> Shows GrowthStages timeline
   └─> Shows DailyCare routine
   └─> Shows Problems & Solutions
   └─> Shows ExtraTips
   └─> Shows VisualGuide with PPT download link

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CONFIGURATION DETAILS
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Environment Variables (backend/.env):
  • DEBUG: Enable/disable debug mode (True/False)
  • API_HOST: API server host (default: 0.0.0.0)
  • API_PORT: API server port (default: 8000)
  • GEMINI_API_KEY: Google Gemini API key (required for AI)
  • NOTEBOOKLM_API_KEY: NotebookLM API key (optional)
  • CORS_ORIGINS: Comma-separated list of allowed origins

Environment Variables (frontend/.env.local):
  • REACT_APP_API_URL: Backend API URL (default: http://localhost:8000)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ TESTING & DEBUGGING
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Backend API Testing:
  1. Check health: curl http://localhost:8000/health
  2. View docs: http://localhost:8000/docs
  3. Test endpoint from Swagger UI
  4. Check generated PPT files in: backend/generated_files/

Frontend Testing:
  1. Open http://localhost:5173 (or 3000)
  2. Check browser console for errors
  3. Use Network tab to see API calls
  4. Verify .env.local has correct API_URL

Troubleshooting:
  • CORS errors: Check CORS_ORIGINS in .env matches frontend URL
  • API not responding: Verify backend is running on port 8000
  • No Gemini response: Check GEMINI_API_KEY in .env
  • PPT not generating: Ensure python-pptx is installed
  • Frontend can't find API: Check REACT_APP_API_URL in .env.local

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ DEPLOYMENT NOTES
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Production Preparation:
  1. Set DEBUG=False in backend .env
  2. Update CORS_ORIGINS to production domain
  3. Remove localhost entries from CORS_ORIGINS
  4. Build frontend: npm run build
  5. Configure reverse proxy (nginx/Apache)
  6. Use HTTPS in production
  7. Set strong API keys
  8. Configure proper logging
  9. Setup error monitoring
  10. Enable rate limiting

Docker Deployment (optional):
  • Create Dockerfile for backend
  • Create Dockerfile for frontend
  • Use docker-compose.yml for orchestration
  • Mount volumes for generated_files persistence

"""