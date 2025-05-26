import React, { useState, useEffect } from 'react';
import { Project, ProjectCreate, ProjectWithMiniatures, ProjectStatistics, ProjectUpdate } from '../types';
import { projectApi } from '../services/api';
import ProjectForm from './ProjectForm';
import ProjectCard from './ProjectCard';
import ProjectDetails from './ProjectDetails';

interface ProjectsProps {
  onError: (error: string) => void;
}

const Projects: React.FC<ProjectsProps> = ({ onError }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [statistics, setStatistics] = useState<ProjectStatistics | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [selectedProject, setSelectedProject] = useState<ProjectWithMiniatures | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadProjects();
    loadStatistics();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await projectApi.getAll();
      setProjects(data);
    } catch (error: any) {
      onError(error.message || 'Failed to load projects');
    } finally {
      setIsLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const stats = await projectApi.getStatistics();
      setStatistics(stats);
    } catch (error) {
      // Statistics are optional, don't show error
      console.warn('Failed to load project statistics:', error);
    }
  };

  const handleCreateProject = async (projectData: ProjectCreate) => {
    try {
      const newProject = await projectApi.create(projectData);
      setProjects(prev => [...prev, newProject]);
      setShowCreateForm(false);
      loadStatistics(); // Refresh stats
    } catch (error: any) {
      onError(error.message || 'Failed to create project');
    }
  };

  const handleUpdateProject = async (id: string, updates: ProjectUpdate) => {
    try {
      const updatedProject = await projectApi.update(id, updates);
      setProjects(prev => 
        prev.map(p => p.id === id ? updatedProject : p)
      );
      setEditingProject(null);
      loadStatistics(); // Refresh stats
    } catch (error: any) {
      onError(error.message || 'Failed to update project');
    }
  };

  const handleDeleteProject = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this project? This will not delete the miniatures, only remove them from the project.')) {
      return;
    }

    try {
      await projectApi.delete(id);
      setProjects(prev => prev.filter(p => p.id !== id));
      if (selectedProject?.id === id) {
        setSelectedProject(null);
      }
      loadStatistics(); // Refresh stats
    } catch (error: any) {
      onError(error.message || 'Failed to delete project');
    }
  };

  const handleViewProject = async (project: Project) => {
    try {
      const projectWithMiniatures = await projectApi.getWithMiniatures(project.id);
      setSelectedProject(projectWithMiniatures);
    } catch (error: any) {
      onError(error.message || 'Failed to load project details');
    }
  };

  const getProjectStatusColor = (completionPercentage: number) => {
    if (completionPercentage === 0) return '#e0e0e0'; // Not started
    if (completionPercentage < 25) return '#ff9800'; // Just started
    if (completionPercentage < 75) return '#2196f3'; // In progress
    if (completionPercentage < 100) return '#ff5722'; // Nearly complete
    return '#4caf50'; // Completed
  };

  if (isLoading) {
    return (
      <div className="projects-loading">
        <div className="loading-spinner"></div>
        <p>Loading projects...</p>
      </div>
    );
  }

  if (selectedProject) {
    return (
      <ProjectDetails
        project={selectedProject}
        onBack={() => setSelectedProject(null)}
        onUpdate={(updates: ProjectUpdate) => handleUpdateProject(selectedProject.id, updates)}
        onDelete={() => handleDeleteProject(selectedProject.id)}
        onError={onError}
      />
    );
  }

  return (
    <div className="projects-container">
      <div className="projects-header">
        <h2>My Projects</h2>
        <button 
          className="add-button"
          onClick={() => setShowCreateForm(true)}
        >
          + Create Project
        </button>
      </div>

      {/* Statistics Overview */}
      {statistics && (
        <div className="projects-stats">
          <div className="stat-card">
            <h3>{statistics.total_projects}</h3>
            <p>Total Projects</p>
          </div>
          <div className="stat-card">
            <h3>{statistics.active_projects}</h3>
            <p>Active Projects</p>
          </div>
          <div className="stat-card">
            <h3>{statistics.completed_projects}</h3>
            <p>Completed</p>
          </div>
          <div className="stat-card">
            <h3>{Math.round(statistics.average_completion_rate)}%</h3>
            <p>Avg. Completion</p>
          </div>
        </div>
      )}

      {/* Create Project Form */}
      {showCreateForm && (
        <ProjectForm
          onSubmit={handleCreateProject}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {/* Edit Project Form */}
      {editingProject && (
        <ProjectForm
          project={editingProject}
          onSubmit={(data: ProjectCreate) => handleUpdateProject(editingProject.id, data)}
          onCancel={() => setEditingProject(null)}
          isEditing={true}
        />
      )}

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <div className="no-projects">
          <h3>No projects yet</h3>
          <p>Create your first project to organize your miniatures into painting goals, army lists, or themed collections.</p>
          <button 
            className="create-first-project-button"
            onClick={() => setShowCreateForm(true)}
          >
            Create Your First Project
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onView={() => handleViewProject(project)}
              onEdit={() => setEditingProject(project)}
              onDelete={() => handleDeleteProject(project.id)}
              statusColor={getProjectStatusColor(project.completion_percentage)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Projects; 