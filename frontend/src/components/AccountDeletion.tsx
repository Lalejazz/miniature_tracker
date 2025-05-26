import React, { useState } from 'react';
import { authApi } from '../services/api';

interface AccountDeletionProps {
  onAccountDeleted: () => void;
}

const AccountDeletion: React.FC<AccountDeletionProps> = ({ onAccountDeleted }) => {
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      // Account deleted successfully
      onAccountDeleted();
    } catch (err) {
      console.error('Account deletion error:', err);
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

  if (!showConfirmation) {
    return (
      <div className="account-deletion-section">
        <h3>🗑️ Delete Account</h3>
        <div className="danger-zone">
          <p>
            <strong>⚠️ Warning:</strong> This action cannot be undone. Deleting your account will permanently remove:
          </p>
          <ul>
            <li>Your entire miniature collection</li>
            <li>All painting progress and status history</li>
            <li>Your player preferences and profile</li>
            <li>All associated data</li>
          </ul>
          <button 
            type="button" 
            className="delete-account-button"
            onClick={handleDeleteRequest}
          >
            🗑️ Request Account Deletion
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="account-deletion-confirmation">
      <h3>⚠️ Confirm Account Deletion</h3>
      <div className="confirmation-content">
        <p><strong>This action is permanent and cannot be undone!</strong></p>
        <p>All your data will be permanently deleted, including:</p>
        <ul>
          <li>Your entire miniature collection ({/* TODO: Add count */})</li>
          <li>All painting progress and status history</li>
          <li>Your player preferences and profile</li>
          <li>All associated data</li>
        </ul>
        
        <div className="confirmation-input">
          <label htmlFor="confirmation">
            Type <strong>"delete my account"</strong> to confirm:
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
            onClick={handleCancel}
            disabled={isDeleting}
            className="cancel-button"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirmDelete}
            disabled={isDeleting || confirmationText.toLowerCase() !== 'delete my account'}
            className="confirm-delete-button"
          >
            {isDeleting ? 'Deleting Account...' : '🗑️ Delete My Account'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountDeletion; 