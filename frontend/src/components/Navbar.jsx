import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import './Navbar.css';

function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsMenuOpen(false);
  };

  const handleProfileClick = () => {
    navigate('/profile');
    setIsMenuOpen(false);
  };

  const handleSignInClick = () => {
    navigate('/login');
    setIsMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
      <div className="logo-container">
        <svg
          className="logo-icon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 2C12 2 8 6 8 10C8 11.0609 8.42143 12.0783 9.17157 12.8284C9.92172 13.5786 10.9391 14 12 14C13.0609 14 14.0783 13.5786 14.8284 12.8284C15.5786 12.0783 16 11.0609 16 10C16 6 12 2 12 2Z"
            fill="currentColor"
          />
          <path
            d="M12 14V22M8 18H16"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
        <h1 className="app-title">
          <span className="title-main">PlantCare</span>
          <span className="title-sub">AI Guide</span>
        </h1>
      </div>
        </Link>

        {/* Mobile Menu Toggle */}
        <button
          className={`menu-toggle ${isMenuOpen ? 'active' : ''}`}
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        {/* Nav Items */}
        <div className={`navbar-menu ${isMenuOpen ? 'active' : ''}`}>
          <Link to="/" className="nav-item" onClick={() => setIsMenuOpen(false)}>
            Home
          </Link>

          <Link to="/identify" className="nav-item" onClick={() => setIsMenuOpen(false)}>
            Identify
          </Link>

          {isAuthenticated && (
            <>
              <Link to="/dashboard" className="nav-item" onClick={() => setIsMenuOpen(false)}>
                Dashboard
              </Link>
              <Link to="/plants" className="nav-item" onClick={() => setIsMenuOpen(false)}>
                My Plants
              </Link>
            </>
          )}

          {isAuthenticated ? (
            <>
              <div className="nav-user-info">
                <span className="user-name">{user?.username}</span>
              </div>
              <button
                className="nav-button profile-button"
                onClick={handleProfileClick}
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
                  <path
                    d="M6 20C6 16.134 8.686 13 12 13C15.314 13 18 16.134 18 20"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
                Profile
              </button>
              <button
                className="nav-button logout-button"
                onClick={handleLogout}
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M17 16L21 12M21 12L17 8M21 12H9M13 3H6C4.89543 3 4 3.89543 4 5V19C4 20.1046 4.89543 21 6 21H13"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                Sign Out
              </button>
            </>
          ) : (
            <button
              className="nav-button signin-button"
              onClick={handleSignInClick}
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M15 3H7C5.89543 3 5 3.89543 5 5V19C5 20.1046 5.89543 21 7 21H15M19 16L23 12M23 12L19 8M23 12H9"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Sign In
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
