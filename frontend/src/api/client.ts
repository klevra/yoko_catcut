const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const api = {
  // Projects
  createProject: (userId: string, projectName: string) =>
    fetch(`${API_URL}/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, project_name: projectName }),
    }).then((r) => r.json()),

  listProjects: (userId: string) =>
    fetch(`${API_URL}/projects/${userId}`).then((r) => r.json()),

  getProject: (userId: string, projectName: string) =>
    fetch(`${API_URL}/projects/${userId}/${projectName}`).then((r) =>
      r.json()
    ),

  updateProject: (userId: string, projectName: string, newName: string) =>
    fetch(`${API_URL}/projects/${userId}/${projectName}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_name: newName }),
    }).then((r) => r.json()),

  deleteProject: (userId: string, projectName: string) =>
    fetch(`${API_URL}/projects/${userId}/${projectName}`, {
      method: "DELETE",
    }).then((r) => r.json()),

  // Uploads
  uploadFile: (userId: string, projectName: string, file: File) => {
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("project_name", projectName);
    formData.append("file", file);

    return fetch(`${API_URL}/uploads`, {
      method: "POST",
      body: formData,
    }).then((r) => r.json());
  },

  // Jobs
  getJob: (jobId: string) =>
    fetch(`${API_URL}/jobs/${jobId}`).then((r) => r.json()),

  listJobs: (userId: string, projectName: string) =>
    fetch(
      `${API_URL}/jobs?user_id=${userId}&project_name=${projectName}`
    ).then((r) => r.json()),

  updateJobStatus: (jobId: string, status: string) =>
    fetch(`${API_URL}/jobs/${jobId}/status`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    }).then((r) => r.json()),

  cancelJob: (jobId: string) =>
    fetch(`${API_URL}/jobs/${jobId}/cancel`, {
      method: "POST",
    }).then((r) => r.json()),
};
