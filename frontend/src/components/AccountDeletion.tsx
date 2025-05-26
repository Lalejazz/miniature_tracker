import React, { useState } from 'react';
import { authApi } from '../services/api';

interface AccountDeletionProps {
  onAccountDeleted: () => void;
}

const AccountDeletion: React.FC<AccountDeletionProps> = ({ onAccountDeleted }) => {
  const [showDeletionSection, setShowDeletionSection] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleShowDeletion = () => {
    setShowDeletionSection(true);
    setError(null);
  };

  const handleDeleteRequest = () => {
    setShowConfirmation(true);
    setError(null);
  };

  const handleConfirmDelete = async () => {
    if (confirmationText.toLowerCase() !== 'delete my account') {
      setError('Please type "delete my account" exactly to confirm');
      return;
    }

    setIsDeleting(true);
    setError(null);

    try {
      await authApi.deleteAccount();
      onAccountDeleted();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete account');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCancel = () => {
    setShowConfirmation(false);
    setConfirmationText('');
    setError(null);
  };

  const handleCancelAll = () => {
    setShowDeletionSection(false);
    setShowConfirmation(false);
    setConfirmationText('');
    setError(null);
  };

  if (!showDeletionSection) {
    return (
      <div className="account-management-section">
        <h3>Account Management</h3>
        <p>Need to make changes to your account?</p>
        <button 
          type="button" 
          className="show-deletion-link"
          onClick={handleShowDeletion}
        >
          I want to delete my account
        </button>
      </div>
    );
  }

  if (showConfirmation) {
    return (
      <div className="account-deletion-section">
        <div className="account-deletion-confirmation">
          <div className="confirmation-content">
            <h3>⚠️ Final Confirmation</h3>
            <p>
              Are you absolutely sure you want to delete your account? This action will:
            </p>
            <ul>
              <li>Permanently delete your entire miniature collection</li>
              <li>Remove all painting progress and status history</li>
              <li>Delete your player preferences and profile</li>
              <li>Remove all associated data</li>
            </ul>
            <p><strong>This action cannot be undone.</strong></p>
            
            <div className="confirmation-input">
              <label htmlFor="confirmation">
                Type "delete my account" to confirm:
              </label>
              <input
                type="text"
                id="confirmation"
                value={confirmationText}
                onChange={(e) => setConfirmationText(e.target.value)}
                placeholder="delete my account"
                disabled={isDeleting}
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <div className="confirmation-actions">
              <button 
                type="button" 
                className="cancel-button"
                onClick={handleCancel}
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button 
                type="button" 
                className="confirm-delete-button"
                onClick={handleConfirmDelete}
                disabled={isDeleting || confirmationText.toLowerCase() !== 'delete my account'}
              >
                {isDeleting ? 'Deleting Account...' : 'Delete My Account'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="account-deletion-section">
      <h3>Delete Account</h3>
      
      <div className="deletion-info">
        <p>
          If you're no longer using Miniature Tracker, you can request to delete your account. 
          Here's what will happen:
        </p>
        
        <div className="deletion-process">
          <h4>What gets deleted:</h4>
          <ul>
            <li>Your entire miniature collection and data</li>
            <li>All painting progress and status history</li>
            <li>Your player preferences and profile information</li>
            <li>Any associated account data</li>
          </ul>
          
          <h4>The process:</h4>
          <ol>
            <li>You click "Request Account Deletion" below</li>
            <li>We'll ask you to confirm this decision</li>
            <li>Your account and all data will be permanently deleted</li>
            <li>You'll be logged out and redirected to the homepage</li>
          </ol>
          
          <div className="deletion-note">
            <p>
              <strong>Important:</strong> This action cannot be undone. If you're having issues 
              with the app, consider reaching out to support first - we might be able to help!
            </p>
          </div>
        </div>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="deletion-actions">
        <button 
          type="button" 
          className="cancel-button"
          onClick={handleCancelAll}
        >
          Never mind, keep my account
        </button>
        <button 
          type="button" 
          className="delete-request-button"
          onClick={handleDeleteRequest}
        >
          Request Account Deletion
        </button>
      </div>
    </div>
  );
};

export default AccountDeletion; 