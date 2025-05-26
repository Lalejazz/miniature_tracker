import React, { useState, useEffect } from 'react';
import { ProjectWithMiniatures, Miniature, ProjectUpdate, ProjectCreate } from '../types';
import { projectApi } from '../services/api';
import MiniatureCard from './MiniatureCard';
import AddMiniaturesToProject from './AddMiniaturesToProject';
import ProjectForm from './ProjectForm';

interface ProjectDetailsProps {
  project: ProjectWithMiniatures;
  onBack: () => void;
  onUpdate: (updates: ProjectUpdate) => void;
  onDelete: () => void;
  onError: (error: string) => void;
}

const ProjectDetails: React.FC<ProjectDetailsProps> = ({
  project: initialProject,
  onBack,
  onUpdate,
  onDelete,
  onError
}) => {
  const [showAddMiniatures, setShowAddMiniatures] = useState(false);
  const [projectMiniatures, setProjectMiniatures] = useState(initialProject.miniatures);
  const [currentProject, setCurrentProject] = useState(initialProject);
  const [showEditForm, setShowEditForm] = useState(false);

  // Update local state when the project prop changes
  useEffect(() => {
    setCurrentProject(initialProject);
    setProjectMiniatures(initialProject.miniatures);
  }, [initialProject]);

  const handleProjectUpdate = async (updates: ProjectUpdate) => {
    try {
      // Call the parent's update handler
      await onUpdate(updates);
      
      // Re-fetch the project data to get the latest information
      const updatedProject = await projectApi.getWithMiniatures(currentProject.id);
      setCurrentProject(updatedProject);
      setProjectMiniatures(updatedProject.miniatures);
      setShowEditForm(false); // Close the edit form
    } catch (error: any) {
      onError(error.message || 'Failed to update project');
    }
  };

  const handleEditSubmit = async (projectData: ProjectCreate) => {
    await handleProjectUpdate(projectData);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusText = (completionPercentage: number | undefined) => {
    const percentage = completionPercentage || 0;
    if (percentage === 0) return 'Not Started';
    if (percentage < 25) return 'Just Started';
    if (percentage < 75) return 'In Progress';
    if (percentage < 100) return 'Nearly Complete';
    return 'Completed';
  };

  const handleRemoveMiniature = async (miniatureId: string) => {
    if (!window.confirm('Remove this miniature from the project?')) {
      return;
    }

    try {
      await projectApi.removeMiniature(currentProject.id, miniatureId);
      setProjectMiniatures(prev => prev.filter(m => m.id !== miniatureId));
      // Note: We should also update the project stats, but for now just remove from list
    } catch (error: any) {
      onError(error.message || 'Failed to remove miniature from project');
    }
  };

  const handleMiniaturesAdded = (addedMiniatures: Miniature[]) => {
    setProjectMiniatures(prev => [...prev, ...addedMiniatures]);
    setShowAddMiniatures(false);
  };

  const isOverdue = currentProject.target_completion_date && new Date(currentProject.target_completion_date) < new Date();
  const daysUntilTarget = currentProject.target_completion_date
    ? Math.ceil((new Date(currentProject.target_completion_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    : null;

  return (
    <div className="project-details">
      <div className="project-details-header">
        <button onClick={onBack} className="back-button">
          ← Back to Projects
        </button>
        <div className="project-title-section">
          <h2 style={{ color: currentProject.color }}>{currentProject.name}</h2>
          <div className="project-actions">
            <button 
              onClick={() => setShowAddMiniatures(true)}
              className="add-button"
            >
              + Add Miniatures
            </button>
            <button 
              onClick={() => setShowEditForm(true)}
              className="edit-button"
            >
              Edit Project
            </button>
            <button 
              onClick={onDelete}
              className="delete-button"
            >
              Delete Project
            </button>
          </div>
        </div>
      </div>

      {currentProject.description && (
        <div className="project-description-section">
          <p>{currentProject.description}</p>
        </div>
      )}

      <div className="project-overview">
        <div className="project-progress-large">
          <div className="progress-header">
            <h3>{Math.round(currentProject.completion_percentage || 0)}% Complete</h3>
            <span className="status-text">
              {getStatusText(currentProject.completion_percentage)}
            </span>
          </div>
          <div className="progress-bar-large">
            <div 
              className="progress-fill"
              style={{ 
                width: `${currentProject.completion_percentage || 0}%`,
                backgroundColor: currentProject.color
              }}
            />
          </div>
        </div>

        <div className="project-info-grid">
          <div className="info-card">
            <h4>{projectMiniatures.length}</h4>
            <p>Total Miniatures</p>
          </div>
          
          {currentProject.target_completion_date && (
            <div className={`info-card ${isOverdue ? 'overdue' : ''}`}>
              <h4>{formatDate(currentProject.target_completion_date)}</h4>
              <p>Target Date</p>
              {daysUntilTarget !== null && (
                <small>
                  {isOverdue 
                    ? `${Math.abs(daysUntilTarget)} days overdue`
                    : `${daysUntilTarget} days remaining`
                  }
                </small>
              )}
            </div>
          )}

          <div className="info-card">
            <h4>{formatDate(currentProject.created_at)}</h4>
            <p>Created</p>
          </div>
        </div>
      </div>

      {currentProject.notes && (
        <div className="project-notes-section">
          <h3>Notes</h3>
          <p>{currentProject.notes}</p>
        </div>
      )}

      <div className="project-miniatures-section">
        <h3>Miniatures in Project ({projectMiniatures.length})</h3>
        
        {projectMiniatures.length === 0 ? (
          <div className="no-miniatures">
            <p>No miniatures in this project yet.</p>
            <button 
              onClick={() => setShowAddMiniatures(true)}
              className="add-first-miniature-button"
            >
              Add Your First Miniature
            </button>
          </div>
        ) : (
          <div className="miniatures-grid">
            {projectMiniatures.map(miniature => (
              <div key={miniature.id} className="project-miniature-card">
                <MiniatureCard
                  miniature={miniature}
                  onEdit={() => {}} // We'll handle this later
                  onDelete={() => {}} // We'll handle this later
                />
                <button 
                  onClick={() => handleRemoveMiniature(miniature.id)}
                  className="remove-from-project-button"
                  title="Remove from project"
                >
                  Remove from Project
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {showAddMiniatures && (
        <AddMiniaturesToProject
          projectId={currentProject.id}
          existingMiniatureIds={projectMiniatures.map(m => m.id)}
          onClose={() => setShowAddMiniatures(false)}
          onMiniaturesAdded={handleMiniaturesAdded}
          onError={onError}
        />
      )}

      {showEditForm && (
        <ProjectForm
          project={currentProject}
          onSubmit={handleEditSubmit}
          onCancel={() => setShowEditForm(false)}
          isEditing={true}
        />
      )}
    </div>
  );
};

export default ProjectDetails; 