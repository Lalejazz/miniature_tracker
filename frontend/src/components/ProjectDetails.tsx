import React, { useState } from 'react';
import { ProjectWithMiniatures, Miniature, ProjectUpdate } from '../types';
import { projectApi } from '../services/api';
import MiniatureCard from './MiniatureCard';
import AddMiniaturesToProject from './AddMiniaturesToProject';

interface ProjectDetailsProps {
  project: ProjectWithMiniatures;
  onBack: () => void;
  onUpdate: (updates: ProjectUpdate) => void;
  onDelete: () => void;
  onError: (error: string) => void;
}

const ProjectDetails: React.FC<ProjectDetailsProps> = ({
  project,
  onBack,
  onUpdate,
  onDelete,
  onError
}) => {
  const [showAddMiniatures, setShowAddMiniatures] = useState(false);
  const [projectMiniatures, setProjectMiniatures] = useState(project.miniatures);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusText = (completionPercentage: number) => {
    if (completionPercentage === 0) return 'Not Started';
    if (completionPercentage < 25) return 'Just Started';
    if (completionPercentage < 75) return 'In Progress';
    if (completionPercentage < 100) return 'Nearly Complete';
    return 'Completed';
  };

  const handleRemoveMiniature = async (miniatureId: string) => {
    if (!window.confirm('Remove this miniature from the project?')) {
      return;
    }

    try {
      await projectApi.removeMiniature(project.id, miniatureId);
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

  const isOverdue = project.target_date && new Date(project.target_date) < new Date();
  const daysUntilTarget = project.target_date 
    ? Math.ceil((new Date(project.target_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    : null;

  return (
    <div className="project-details">
      <div className="project-details-header">
        <button onClick={onBack} className="back-button">
          ← Back to Projects
        </button>
        <div className="project-title-section">
          <h2 style={{ color: project.color }}>{project.name}</h2>
          <div className="project-actions">
            <button 
              onClick={() => setShowAddMiniatures(true)}
              className="add-button"
            >
              + Add Miniatures
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

      {project.description && (
        <div className="project-description-section">
          <p>{project.description}</p>
        </div>
      )}

      <div className="project-overview">
        <div className="project-progress-large">
          <div className="progress-header">
            <h3>{Math.round(project.completion_percentage)}% Complete</h3>
            <span className="status-text">
              {getStatusText(project.completion_percentage)}
            </span>
          </div>
          <div className="progress-bar-large">
            <div 
              className="progress-fill"
              style={{ 
                width: `${project.completion_percentage}%`,
                backgroundColor: project.color
              }}
            />
          </div>
        </div>

        <div className="project-info-grid">
          <div className="info-card">
            <h4>{projectMiniatures.length}</h4>
            <p>Total Miniatures</p>
          </div>
          
          {project.target_date && (
            <div className={`info-card ${isOverdue ? 'overdue' : ''}`}>
              <h4>{formatDate(project.target_date)}</h4>
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
            <h4>{formatDate(project.created_at)}</h4>
            <p>Created</p>
          </div>
        </div>
      </div>

      {project.notes && (
        <div className="project-notes-section">
          <h3>Notes</h3>
          <p>{project.notes}</p>
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
          projectId={project.id}
          existingMiniatureIds={projectMiniatures.map(m => m.id)}
          onClose={() => setShowAddMiniatures(false)}
          onMiniaturesAdded={handleMiniaturesAdded}
          onError={onError}
        />
      )}
    </div>
  );
};

export default ProjectDetails; 