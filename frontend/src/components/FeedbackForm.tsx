/**
 * Feedback form component for user feedback and feature requests
 */

import React, { useState } from 'react';

interface FeedbackFormProps {
  onClose?: () => void;
}

type FeedbackType = 'bug' | 'feature' | 'improvement' | 'general';

interface FeedbackData {
  type: FeedbackType;
  title: string;
  description: string;
  email: string;
  priority: 'low' | 'medium' | 'high';
}

export const FeedbackForm: React.FC<FeedbackFormProps> = ({ onClose }) => {
  const [formData, setFormData] = useState<FeedbackData>({
    type: 'general',
    title: '',
    description: '',
    email: '',
    priority: 'medium'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const feedbackTypes = [
    { value: 'bug', label: '🐛 Bug Report', description: 'Report a problem or error' },
    { value: 'feature', label: '✨ Feature Request', description: 'Suggest a new feature' },
    { value: 'improvement', label: '🔧 Improvement', description: 'Suggest an enhancement' },
    { value: 'general', label: '💬 General Feedback', description: 'General comments or questions' }
  ];

  const priorityLevels = [
    { value: 'low', label: 'Low', description: 'Nice to have' },
    { value: 'medium', label: 'Medium', description: 'Would be helpful' },
    { value: 'high', label: 'High', description: 'Important or urgent' }
  ];

  const handleInputChange = (field: keyof FeedbackData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setSubmitStatus('idle');
    setErrorMessage('');
  };

  const validateForm = (): boolean => {
    if (!formData.title.trim()) {
      setErrorMessage('Please provide a title for your feedback');
      return false;
    }
    if (!formData.description.trim()) {
      setErrorMessage('Please provide a description');
      return false;
    }
    if (!formData.email.trim()) {
      setErrorMessage('Please provide your email address');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setErrorMessage('Please provide a valid email address');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrorMessage('');

    try {
      // For now, we'll create a mailto link as a fallback
      // In the future, this could be replaced with an API call
      const subject = `[Miniature Tracker] ${formData.type.toUpperCase()}: ${formData.title}`;
      const body = `
Feedback Type: ${feedbackTypes.find(t => t.value === formData.type)?.label}
Priority: ${formData.priority.toUpperCase()}
From: ${formData.email}

Description:
${formData.description}

---
Submitted via Miniature Tracker Feedback Form
      `.trim();

      const mailtoLink = `mailto:developer@miniaturetracker.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      
      // Open email client
      window.location.href = mailtoLink;
      
      // Simulate successful submission
      setTimeout(() => {
        setSubmitStatus('success');
        setIsSubmitting(false);
      }, 1000);

    } catch (error) {
      console.error('Error submitting feedback:', error);
      setErrorMessage('Failed to submit feedback. Please try again.');
      setSubmitStatus('error');
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setFormData({
      type: 'general',
      title: '',
      description: '',
      email: '',
      priority: 'medium'
    });
    setSubmitStatus('idle');
    setErrorMessage('');
  };

  if (submitStatus === 'success') {
    return (
      <div className="feedback-form">
        <div className="feedback-success">
          <div className="success-icon">✅</div>
          <h3>Thank You for Your Feedback!</h3>
          <p>Your feedback has been prepared and your email client should have opened.</p>
          <p>If the email didn't open automatically, please send your feedback to:</p>
          <p className="email-address">developer@miniaturetracker.com</p>
          <div className="form-actions">
            <button type="button" onClick={handleReset} className="btn-secondary">
              Submit More Feedback
            </button>
            {onClose && (
              <button type="button" onClick={onClose} className="btn-primary">
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-form">
      <div className="feedback-header">
        <h2>📝 Send Feedback</h2>
        <p>Help us improve Miniature Tracker by sharing your thoughts, reporting bugs, or suggesting new features.</p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Feedback Type */}
        <div className="form-group">
          <label>What type of feedback are you providing?</label>
          <div className="feedback-type-grid">
            {feedbackTypes.map(type => (
              <label key={type.value} className="feedback-type-option">
                <input
                  type="radio"
                  name="feedbackType"
                  value={type.value}
                  checked={formData.type === type.value}
                  onChange={(e) => handleInputChange('type', e.target.value as FeedbackType)}
                />
                <div className="option-content">
                  <div className="option-label">{type.label}</div>
                  <div className="option-description">{type.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Title */}
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            id="title"
            type="text"
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            placeholder="Brief summary of your feedback"
            maxLength={100}
            required
          />
          <small>{formData.title.length}/100 characters</small>
        </div>

        {/* Description */}
        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="Please provide detailed information about your feedback, including steps to reproduce if reporting a bug"
            rows={6}
            maxLength={1000}
            required
          />
          <small>{formData.description.length}/1000 characters</small>
        </div>

        {/* Email */}
        <div className="form-group">
          <label htmlFor="email">Your Email *</label>
          <input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            placeholder="your.email@example.com"
            required
          />
          <small>We'll use this to follow up on your feedback if needed</small>
        </div>

        {/* Priority */}
        <div className="form-group">
          <label>Priority Level</label>
          <div className="priority-options">
            {priorityLevels.map(priority => (
              <label key={priority.value} className="priority-option">
                <input
                  type="radio"
                  name="priority"
                  value={priority.value}
                  checked={formData.priority === priority.value}
                  onChange={(e) => handleInputChange('priority', e.target.value as 'low' | 'medium' | 'high')}
                />
                <div className="priority-content">
                  <div className="priority-label">{priority.label}</div>
                  <div className="priority-description">{priority.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {errorMessage && (
          <div className="error-message">
            {errorMessage}
          </div>
        )}

        {/* Form Actions */}
        <div className="form-actions">
          <button type="button" onClick={handleReset} className="btn-secondary">
            Reset Form
          </button>
          <button type="submit" disabled={isSubmitting} className="btn-primary">
            {isSubmitting ? 'Preparing...' : 'Send Feedback'}
          </button>
          {onClose && (
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="feedback-footer">
        <p><strong>Note:</strong> This will open your default email client. If you prefer, you can also email us directly at <strong>developer@miniaturetracker.com</strong></p>
      </div>
    </div>
  );
}; 