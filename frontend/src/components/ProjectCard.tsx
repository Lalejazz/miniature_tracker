import React from 'react';
import { Project, STATUS_INFO } from '../types';

interface ProjectCardProps {
  project: Project;
  onView: () => void;
  onEdit: () => void;
  onDelete: () => void;
  statusColor: string;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ 
  project, 
  onView, 
  onEdit, 
  onDelete, 
  statusColor 
}) => {
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

  const isOverdue = project.target_completion_date && new Date(project.target_completion_date) < new Date();
  const daysUntilTarget = project.target_completion_date
    ? Math.ceil((new Date(project.target_completion_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    : null;

  return (
    <div className="project-card" style={{ borderLeftColor: project.color }}>
      <div className="project-card-header">
        <h3 className="project-name" onClick={onView}>
          {project.name}
        </h3>
        <div className="project-actions">
          <button 
            onClick={onEdit}
            className="edit-button-small"
            title="Edit project"
          >
            ✏️
          </button>
          <button 
            onClick={onDelete}
            className="delete-button-small"
            title="Delete project"
          >
            🗑️
          </button>
        </div>
      </div>

      {project.description && (
        <p className="project-description">{project.description}</p>
      )}

      <div className="project-progress">
        <div className="progress-header">
          <span className="progress-text">
            {Math.round(project.completion_percentage)}% Complete
          </span>
          <span className="status-text" style={{ color: statusColor }}>
            {getStatusText(project.completion_percentage)}
          </span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ 
              width: `${project.completion_percentage}%`,
              backgroundColor: statusColor
            }}
          />
        </div>
      </div>

      <div className="project-stats">
        <div className="stat">
          <span className="stat-value">{project.miniature_count}</span>
          <span className="stat-label">Miniatures</span>
        </div>
        
        {/* Status breakdown */}
        <div className="status-breakdown">
          {Object.entries(project.status_breakdown).map(([status, count]) => {
            if (count === 0) return null;
            const statusInfo = STATUS_INFO[status as keyof typeof STATUS_INFO];
            return (
              <div key={status} className="status-item" title={`${count} ${statusInfo.label}`}>
                <div 
                  className="status-dot"
                  style={{ backgroundColor: statusInfo.color }}
                />
                <span>{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      {project.target_completion_date && (
        <div className={`project-target ${isOverdue ? 'overdue' : ''}`}>
          <span className="target-label">Target:</span>
          <span className="target-date">{formatDate(project.target_completion_date)}</span>
          {daysUntilTarget !== null && (
            <span className="days-remaining">
              {isOverdue 
                ? `${Math.abs(daysUntilTarget)} days overdue`
                : `${daysUntilTarget} days left`
              }
            </span>
          )}
        </div>
      )}

      <div className="project-footer">
        <span className="created-date">
          Created {formatDate(project.created_at)}
        </span>
        <button 
          onClick={onView}
          className="view-button"
        >
          View Details →
        </button>
      </div>
    </div>
  );
};

export default ProjectCard; 