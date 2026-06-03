import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import ProjectList from "../components/ProjectList";
import CreateProjectForm from "../components/CreateProjectForm";
import "./Dashboard.css";

export default function Dashboard() {
  const [userId] = useState("default-user");
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await api.listProjects(userId);
      setProjects(data);
    } catch (error) {
      console.error("Failed to load projects:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectCreated = () => {
    loadProjects();
  };

  const handleProjectDeleted = () => {
    loadProjects();
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Yoko CatCut</h1>
        <p>AI-powered video editing platform</p>
      </div>

      <div className="dashboard-content">
        <div className="create-section">
          <CreateProjectForm
            userId={userId}
            onProjectCreated={handleProjectCreated}
          />
        </div>

        <div className="projects-section">
          {loading ? (
            <p>Loading projects...</p>
          ) : projects.length === 0 ? (
            <p>No projects yet. Create one to get started!</p>
          ) : (
            <ProjectList
              projects={projects}
              userId={userId}
              onProjectDeleted={handleProjectDeleted}
            />
          )}
        </div>
      </div>
    </div>
  );
}
