import React, { useState, useEffect } from "react";
import { api, Job, Project, Upload } from "../api/client";
import ProjectList from "../components/ProjectList";
import CreateProjectForm from "../components/CreateProjectForm";
import "./Dashboard.css";

interface Props {
  userId: string;
  usersFile: string;
  onLogout: () => void;
  onEditUpload: (uploadId: string) => void;
}

export default function Dashboard({
  userId,
  usersFile,
  onLogout,
  onEditUpload,
}: Props) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string>("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [loading, setLoading] = useState(true);
  const [projectLoading, setProjectLoading] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (!selectedProject) {
      setJobs([]);
      setUploads([]);
      return;
    }

    let active = true;
    const refreshJobs = async () => {
      try {
        const data = await api.listJobs(userId, selectedProject.project_name);
        if (active) {
          setJobs(data);
        }
      } catch (error) {
        console.error("Failed to load jobs:", error);
      }
    };

    const refreshUploads = async () => {
      try {
        const data = await api.listUploads(
          userId,
          selectedProject.project_name
        );
        if (active) {
          setUploads(data);
        }
      } catch (error) {
        console.error("Failed to load uploads:", error);
      }
    };

    refreshJobs();
    refreshUploads();
    const timer = window.setInterval(refreshJobs, 2000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [selectedProject, userId]);

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

  const openProject = async (projectName: string) => {
    setProjectLoading(true);
    try {
      const project = await api.getProject(userId, projectName);
      setSelectedProject(project);
      setSelectedFile(null);
      setUploadMessage("");
    } catch (error) {
      console.error("Failed to open project:", error);
      alert("Failed to open project, please try again.");
    } finally {
      setProjectLoading(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setUploadMessage("");
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0] ?? null;
    if (file) {
      setSelectedFile(file);
      setUploadMessage(`Selected file: ${file.name}`);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleUpload = async () => {
    if (!selectedProject || !selectedFile) {
      setUploadMessage("Please choose a file first.");
      return;
    }

    setUploading(true);
    setUploadMessage("");
    try {
      const result = await api.uploadFile(
        userId,
        selectedProject.project_name,
        selectedFile
      );
      setUploadMessage(
        `Uploaded ${selectedFile.name} (${formatDuration(
          result.upload.duration
        )})`
      );
      setJobs((current) => [result.job, ...current]);
      setUploads((current) => [result.upload, ...current]);
      setSelectedFile(null);
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadMessage(
        error instanceof Error ? error.message : "Upload failed. Please try again."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleProjectCreated = () => {
    loadProjects();
  };

  const handleProjectDeleted = () => {
    loadProjects();
    setSelectedProject(null);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Yoko CatCut</h1>
          <p>AI-powered video editing platform</p>
        </div>
        <div className="account-badge">
          <strong>{userId}</strong>
          <small>{usersFile}</small>
          <button className="btn-secondary" onClick={onLogout}>
            Logout
          </button>
        </div>
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
              onProjectOpen={openProject}
            />
          )}
        </div>

        {selectedProject && (
          <div className="project-details">
            <h2>Opened Project</h2>
            <p>
              <strong>Name:</strong> {selectedProject.project_name}
            </p>
            <p>
              <strong>Path:</strong> {selectedProject.path}
            </p>
            <p>
              <strong>Created:</strong>{" "}
              {new Date(selectedProject.created_at).toLocaleString()}
            </p>
            <button
              className="btn-secondary"
              onClick={() => setSelectedProject(null)}
              disabled={projectLoading || uploading}
            >
              Close
            </button>
            {projectLoading && <p>Loading project details...</p>}

            <div className="upload-panel">
              <h3>Upload File</h3>
              <div
                className="dropzone"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
              >
                Drag and drop a video file here, or choose one below.
              </div>
              <label htmlFor="project-upload">Select file</label>
              <input
                id="project-upload"
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                disabled={uploading}
              />
              <button
                className="btn-primary"
                onClick={handleUpload}
                disabled={uploading || !selectedFile}
              >
                {uploading ? "Uploading..." : "Upload"}
              </button>
              {uploadMessage && <p className="upload-message">{uploadMessage}</p>}
            </div>

            <div className="jobs-panel">
              <h3>Uploaded Videos</h3>
              {uploads.length === 0 ? (
                <p>No uploaded videos for this project.</p>
              ) : (
                <div className="upload-list">
                  {uploads.map((upload) => (
                    <article className="upload-card" key={upload.upload_id}>
                      <div>
                        <strong>{upload.filename}</strong>
                        <small>
                          {upload.metadata.video.width}x
                          {upload.metadata.video.height} ·{" "}
                          {formatDuration(upload.duration)} ·{" "}
                          {formatFileSize(upload.file_size)}
                        </small>
                      </div>
                      <button
                        className="btn-primary"
                        onClick={() => onEditUpload(upload.upload_id)}
                      >
                        편집
                      </button>
                    </article>
                  ))}
                </div>
              )}
            </div>

            <div className="jobs-panel">
              <h3>Jobs</h3>
              {jobs.length === 0 ? (
                <p>No jobs for this project.</p>
              ) : (
                <div className="jobs-list">
                  {jobs.map((job) => (
                    <article className="job-row" key={job.job_id}>
                      <div>
                        <strong>{job.job_type}</strong>
                        <span className={`job-status status-${job.status.toLowerCase()}`}>
                          {job.status}
                        </span>
                      </div>
                      {job.metadata.media?.video && (
                        <small>
                          {job.metadata.media.video.width}x
                          {job.metadata.media.video.height} ·{" "}
                          {job.metadata.media.video.codec || "unknown codec"} ·{" "}
                          {formatDuration(job.metadata.media.duration)}
                        </small>
                      )}
                      {job.metadata.error && (
                        <small className="job-error">{job.metadata.error}</small>
                      )}
                    </article>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function formatDuration(duration: number | null | undefined) {
  if (duration == null) {
    return "duration unknown";
  }
  return `${duration.toFixed(1)}s`;
}

function formatFileSize(bytes: number) {
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
