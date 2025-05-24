/**
 * User header component - shows logged in user and logout option
 */

import React from 'react';
import { User } from '../types';

interface UserHeaderProps {
  user: User;
  onLogout: () => void;
}

export const UserHeader: React.FC<UserHeaderProps> = ({ user, onLogout }) => {
  return (
    <div className="user-header">
      <div className="user-info">
        <span className="user-greeting">
          Welcome, <strong>{user.username}</strong>!
        </span>
        <span className="user-email">{user.email}</span>
      </div>
      
      <button 
        onClick={onLogout}
        className="logout-button"
        title="Logout"
      >
        Logout
      </button>
    </div>
  );
}; 