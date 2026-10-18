# PlantCare 🌱

A comprehensive plant care application with AI-powered recommendations, growth tracking, and personalized care guidance.

## Project Overview

PlantCare is a full-stack application that helps users manage and care for their plants using artificial intelligence. It provides plant identification, daily care instructions, problem diagnosis, and growth stage tracking through an intuitive web interface.

## Features

- 🤖 **AI-Powered Plant Analysis** - Get instant plant identification and care recommendations
- 📋 **Daily Care Instructions** - Receive personalized daily care tips for your plants
- 🔍 **Problem Diagnosis** - Identify and solve plant health issues with AI assistance
- 📈 **Growth Tracking** - Monitor plant growth stages and progress
- 📊 **Visual Guides** - Interactive guides and slides for plant care education
- 💡 **Extra Tips** - Valuable plant care tips and best practices
- 🎨 **Modern UI** - Beautiful, responsive interface with 3D background effects
- 📱 **Cross-Platform** - Web app (React), Mobile app (React Native with Expo), available soon on iOS/Android app stores

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Integration**: Google Gemini API, NotebookLM
- **Database**: MongoDB Atlas
- **Deployment**: Docker

### Frontend (Web)
- **Framework**: React 18+ with Vite
- **Styling**: CSS3 with responsive design
- **3D Graphics**: Three.js (Background3D component)
- **Build Tool**: Vite

### Mobile (New!)
- **Framework**: React Native with Expo
- **Navigation**: React Navigation (Stack + Tabs)
- **State Management**: Zustand + AsyncStorage
- **HTTP Client**: Axios
- **Build Tool**: Expo CLI
- **Platforms**: iOS, Android, Web

## Project Structure

```
PlantCare/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── routes/            # API route handlers
│   │   │   ├── gemini.py      # Gemini API integration
│   │   │   └── notebooklm.py  # NotebookLM integration
│   │   ├── schemas/           # Pydantic data schemas
│   │   │   └── plant.py       # Plant data models
│   │   ├── services/          # Business logic
│   │   │   ├── plant.py       # Plant service
│   │   │   └── ppt_service.py # PowerPoint generation
│   │   └── utils/             # Utilities
│   │       ├── config.py      # Configuration
│   │       └── formatter.py   # Data formatting
│   ├── requirements.txt       # Python dependencies
│   ├── test_api.py           # API tests
│   └── curl-command/         # Docker and deployment configs
│
├── frontend/                   # React Vite web frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── PlantForm.jsx      # Plant input form
│   │   │   ├── PlantOverview.jsx  # Plant overview page
│   │   │   ├── DailyCare.jsx      # Daily care instructions
│   │   │   ├── GrowthStage.jsx    # Growth tracking
│   │   │   ├── Problem.jsx        # Problem diagnosis
│   │   │   ├── ExtraTips.jsx      # Tips and advice
│   │   │   ├── SlideDesign.jsx    # Presentation slides
│   │   │   └── Background3D.jsx   # 3D background
│   │   ├── App.jsx            # Main app component
│   │   ├── main.jsx           # React entry point
│   │   └── index.html         # HTML template
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   └── public/                # Static assets
│
└── mobile/                     # React Native + Expo mobile app
    ├── App.js                 # Main entry point
    ├── app.json               # Expo configuration
    ├── package.json           # Dependencies
    │
    ├── README.md              # Mobile app quick start
    ├── SETUP.md               # Detailed setup guide
    ├── DEVELOPMENT.md         # Development guide
    ├── BUILD_SUMMARY.md       # Complete build summary
    │
    └── src/
        ├── navigation/        # Navigation structure
        │   └── RootNavigator.js
        ├── screens/           # Application screens (6 total)
        │   ├── HomeScreen.js
        │   ├── GuideScreen.js
        │   ├── MyPlantsScreen.js
        │   ├── LoginScreen.js
        │   ├── SignupScreen.js
        │   └── ProfileScreen.js
        ├── components/        # Reusable UI components
        │   ├── Button.js
        │   ├── Input.js
        │   └── Common.js
        ├── services/          # API and business logic
        │   ├── api.js
        │   ├── plantService.js
        │   └── authService.js
        ├── context/           # State management
        │   └── authStore.js
        ├── styles/            # Theme and styling
        │   └── theme.js
        └── utils/             # Helper functions
            ├── helpers.js
            └── config.js
```

## Getting Started

### Prerequisites

- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)
- Docker (optional, for containerized deployment)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the backend directory
   - Add required API keys and configuration:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     NOTEBOOKLM_API_KEY=your_notebooklm_api_key
     ```

5. Run the backend server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

### Mobile App Setup (NEW!)

1. Navigate to the mobile directory:
   ```bash
   cd mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure backend URL (edit `.env.local`):
   ```env
   EXPO_PUBLIC_API_URL=http://localhost:8000
   ```

4. Start development server:
   ```bash
   npm start
   ```

5. Run on device/emulator:
   ```bash
   npm run ios      # iOS Simulator (Mac)
   npm run android  # Android Emulator
   npm run web      # Web Browser
   ```

   Or scan QR code with **Expo Go** app for instant preview on your device.

See [mobile/README.md](mobile/README.md) for detailed mobile setup instructions.

### Running with Docker

1. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access the application:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`

## API Documentation

### Key Endpoints

- **POST /api/identify** - Identify a plant from an image or description
- **GET /api/daily-care** - Get daily care instructions for a plant
- **POST /api/diagnose** - Diagnose plant health problems
- **GET /api/growth-stages** - Get growth stage information
- **POST /api/generate-tips** - Generate personalized care tips

For detailed API documentation, see [backend/md-files/Api documentation.md](backend/md-files/Api%20documentation.md)

## Features Documentation

### Daily Care
Get customized daily care instructions based on your plant type and local conditions.

### Growth Stage Tracking
Monitor your plant's development from seedling to maturity with stage-specific care tips.

### Problem Diagnosis
Identify common plant problems (pests, diseases, nutrient deficiencies) and receive treatment recommendations.

### Visual Guides
Access interactive guides and educational content for plant care best practices.

## Testing

Run the API tests:
```bash
python test_api.py
```

## Configuration

### Backend Configuration
Edit `backend/app/utils/config.py` to adjust:
- API endpoints
- AI model parameters
- Timeout settings
- Default configurations

### Frontend Configuration
Edit `frontend/vite.config.js` for:
- Build settings
- Development server options
- Plugin configurations

## Development

### Adding New Routes
1. Create a new file in `backend/app/routes/`
2. Define route handlers and import in `backend/app/main.py`

### Adding New Components
1. Create a new file in `frontend/src/components/`
2. Import and use in the main app or other components

## Architecture

For detailed architecture information, see [backend/md-files/Architecture.md](backend/md-files/Architecture.md)

## Project Summary

For a quick project overview, see [backend/md-files/Project summary.md](backend/md-files/Project%20summary.md)

## Quick Start Guide

For quick setup instructions, see [backend/md-files/Quick start.md](backend/md-files/Quick%20start.md)

## Troubleshooting

### Backend Issues
- Ensure Python version is 3.8+
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check API keys are correctly set in `.env`

### Frontend Issues
- Clear node_modules and reinstall: `npm install`
- Clear npm cache: `npm cache clean --force`
- Ensure Node.js version is 16+

### Connection Issues
- Verify backend is running on `http://localhost:8000`
- Check CORS settings in `backend/app/main.py`
- Ensure frontend is configured to use correct API URL

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -m 'Add your feature'`
3. Push to the branch: `git push origin feature/your-feature`
4. Open a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

## Acknowledgments

- Built with FastAPI and React
- AI powered by Google Gemini and NotebookLM
- 3D graphics powered by Three.js

---

**Version**: 1.0.0  
**Last Updated**: January 2026
