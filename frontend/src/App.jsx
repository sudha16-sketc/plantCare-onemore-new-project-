import './App.css'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Home from './components/Home.jsx'
import Login from './components/Login.jsx'
import Profile from './components/Profile.jsx'
import Dashboard from './components/Dashboard.jsx'
import MyPlants from './components/MyPlants.jsx'
import PlantDetail from './components/PlantDetail.jsx'
import Identify from './components/Identify.jsx'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="app-wrapper">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/plants"
              element={
                <ProtectedRoute>
                  <MyPlants />
                </ProtectedRoute>
              }
            />
            <Route
              path="/plants/:id"
              element={
                <ProtectedRoute>
                  <PlantDetail />
                </ProtectedRoute>
              }
            />
            <Route path="/identify" element={<Identify />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  )
}

export default App
