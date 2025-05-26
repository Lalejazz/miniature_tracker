import React, { useState, useEffect } from 'react';
import { Project, ProjectCreate } from '../types';

interface ProjectFormProps {
  onSubmit: (project: ProjectCreate) => void;
  onCancel: () => void;
  project?: Project;
  isEditing?: boolean;
}

const ProjectForm: React.FC<ProjectFormProps> = ({ onSubmit, onCancel, project, isEditing = false }) => {
  const [formData, setFormData] = useState({
    name: project?.name || '',
    description: project?.description || '',
    target_date: project?.target_date || '',
    notes: project?.notes || '',
    color: project?.color || '#2196f3'
  });

  // Update form data when project prop changes
  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name || '',
        description: project.description || '',
        target_date: project.target_date || '',
        notes: project.notes || '',
        color: project.color || '#2196f3'
      });
    }
  }, [project]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      alert('Please enter a project name');
      return;
    }

    // Clean up the data
    const cleanedData: ProjectCreate = {
      name: formData.name.trim(),
      description: formData.description.trim() || undefined,
      target_date: formData.target_date || undefined,
      notes: formData.notes.trim() || undefined,
      color: formData.color
    };

    onSubmit(cleanedData);
  };

  const handleChange = (field: keyof typeof formData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const predefinedColors = [
    '#2196f3', // Blue
    '#4caf50', // Green
    '#ff9800', // Orange
    '#f44336', // Red
    '#9c27b0', // Purple
    '#00bcd4', // Cyan
    '#ff5722', // Deep Orange
    '#795548', // Brown
    '#607d8b', // Blue Grey
    '#e91e63'  // Pink
  ];

  return (
    <div className="project-form-overlay">
      <form className="project-form" onSubmit={handleSubmit}>
        <h3>{isEditing ? 'Edit Project' : 'Create New Project'}</h3>
        
        <div className="form-section">
          <div className="form-group">
            <label htmlFor="name">Project Name *</label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="e.g., Space Marine Army, Painting Challenge 2024"
              maxLength={200}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="What is this project about? Goals, theme, etc."
              rows={3}
              maxLength={1000}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="target_date">Target Completion Date</label>
              <input
                type="date"
                id="target_date"
                value={formData.target_date}
                onChange={(e) => handleChange('target_date', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="color">Project Color</label>
              <div className="color-picker">
                <input
                  type="color"
                  id="color"
                  value={formData.color}
                  onChange={(e) => handleChange('color', e.target.value)}
                  className="color-input"
                />
                <div className="predefined-colors">
                  {predefinedColors.map(color => (
                    <button
                      key={color}
                      type="button"
                      className={`color-option ${formData.color === color ? 'selected' : ''}`}
                      style={{ backgroundColor: color }}
                      onClick={() => handleChange('color', color)}
                      title={color}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="notes">Notes</label>
            <textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="Any additional notes about this project..."
              rows={3}
              maxLength={1000}
            />
          </div>
        </div>

        <div className="form-buttons">
          <button type="submit" className="submit-button">
            {isEditing ? 'Update Project' : 'Create Project'}
          </button>
          <button type="button" onClick={onCancel} className="cancel-button">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProjectForm; 