import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './Profile.css';

function Profile() {
  const { user, plants, updateUserProfile, removePlant, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [username, setUsername] = useState(user?.username || '');
  const [email, setEmail] = useState(user?.email || '');
  const [saveMessage, setSaveMessage] = useState('');

  const handleSaveProfile = () => {
    try {
      updateUserProfile(username, email);
      setSaveMessage('Profile updated successfully!');
      setIsEditing(false);
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      setSaveMessage('Error updating profile');
    }
  };

  const handleCancelEdit = () => {
    setUsername(user?.username || '');
    setEmail(user?.email || '');
    setIsEditing(false);
  };

  return (
    <div className="profile-container">
      <div className="profile-card">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="profile-avatar">
            {user?.username?.charAt(0).toUpperCase()}
          </div>
          <div className="profile-info">
            <h1>{user?.username}</h1>
            <p className="profile-email">{user?.email}</p>
            <p className="profile-joined">
              Joined {new Date(user?.createdAt).toLocaleDateString()}
            </p>
          </div>
        </div>

        {saveMessage && (
          <div className="success-message">{saveMessage}</div>
        )}

        {/* Profile Edit Section */}
        <div className="profile-section">
          <div className="section-header">
            <h2>Account Information</h2>
            {!isEditing && (
              <button
                className="edit-button"
                onClick={() => setIsEditing(true)}
              >
                Edit Profile
              </button>
            )}
          </div>

          {isEditing ? (
            <div className="edit-form">
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter username"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter email"
                />
              </div>
              <div className="form-actions">
                <button
                  className="save-button"
                  onClick={handleSaveProfile}
                >
                  Save Changes
                </button>
                <button
                  className="cancel-button"
                  onClick={handleCancelEdit}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="profile-details">
              <div className="detail-row">
                <span className="detail-label">Username:</span>
                <span className="detail-value">{user?.username}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Email:</span>
                <span className="detail-value">{user?.email}</span>
              </div>
            </div>
          )}
        </div>

        {/* Plants Section */}
        <div className="profile-section">
          <h2>Plants You've Asked About</h2>
          {plants.length > 0 ? (
            <div className="plants-list">
              {plants.map((plant) => (
                <div key={plant.id} className="plant-item">
                  <div className="plant-details">
                    <h3>{plant.plant_name || plant.name}</h3>
                    <p className="plant-type">
                      Type: {plant.plant_type || plant.type}
                    </p>
                    <p className="plant-date">
                      Asked on {new Date(plant.addedAt).toLocaleDateString()}
                    </p>
                    {plant.climate && (
                      <p className="plant-info">
                        Climate: {plant.climate}
                      </p>
                    )}
                  </div>
                  <button
                    className="delete-plant-button"
                    onClick={() => removePlant(plant.id)}
                    title="Remove from list"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z"
                        fill="currentColor"
                      />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <svg
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
              <p>No plants yet. Start by creating a plant care guide!</p>
            </div>
          )}
        </div>

        {/* Logout Button */}
        <div className="profile-section logout-section">
          <button className="logout-button" onClick={logout}>
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
        </div>
      </div>
    </div>
  );
}

export default Profile;
