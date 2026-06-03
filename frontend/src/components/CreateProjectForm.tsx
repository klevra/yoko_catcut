import React, { useState } from "react";
import { api } from "../api/client";
import "./CreateProjectForm.css";

interface Props {
  userId: string;
  onProjectCreated: () => void;
}

export default function CreateProjectForm({ userId, onProjectCreated }: Props) {
  const [projectName, setProjectName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.createProject(userId, projectName);
      setProjectName("");
      onProjectCreated();
    } catch (err: any) {
      setError(err.message || "Failed to create project");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-project-form">
      <h2>New Project</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Project name"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          required
          disabled={loading}
        />
        <button type="submit" disabled={loading || !projectName}>
          {loading ? "Creating..." : "Create Project"}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}
