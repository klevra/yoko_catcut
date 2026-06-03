import React from "react";
import { api } from "../api/client";
import "./ProjectList.css";

interface Project {
  user_id: string;
  project_name: string;
  path: string;
  created_at: string;
}

interface Props {
  projects: Project[];
  userId: string;
  onProjectDeleted: () => void;
}

export default function ProjectList({
  projects,
  userId,
  onProjectDeleted,
}: Props) {
  const handleDelete = async (projectName: string) => {
    if (confirm(`Are you sure you want to delete "${projectName}"?`)) {
      try {
        await api.deleteProject(userId, projectName);
        onProjectDeleted();
      } catch (error) {
        alert("Failed to delete project");
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="project-list">
      <h2>Projects</h2>
      {projects.length === 0 ? (
        <p className="empty">No projects found</p>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.project_name} className="project-card">
              <h3>{project.project_name}</h3>
              <p className="project-date">
                Created: {formatDate(project.created_at)}
              </p>
              <p className="project-path">{project.path}</p>
              <div className="project-actions">
                <button className="btn-primary">Open</button>
                <button
                  className="btn-danger"
                  onClick={() => handleDelete(project.project_name)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
