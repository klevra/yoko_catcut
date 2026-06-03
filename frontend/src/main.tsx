import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const API_BASE = 'http://localhost:8000/api/v1';

function App() {
  const [userId, setUserId] = useState('klevra');
  const [projectName, setProjectName] = useState('default_project');
  const [message, setMessage] = useState('');

  async function createProject() {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, project_name: projectName }),
    });
    const data = await res.json();
    setMessage(JSON.stringify(data, null, 2));
  }

  async function uploadFile(file: File) {
    const form = new FormData();
    form.append('user_id', userId);
    form.append('project_name', projectName);
    form.append('file', file);

    const res = await fetch(`${API_BASE}/uploads`, {
      method: 'POST',
      body: form,
    });
    const data = await res.json();
    setMessage(JSON.stringify(data, null, 2));
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  }

  return (
    <main>
      <h1>Yoko CatCut</h1>
      <p>AI 기반 영상 편집 웹 플랫폼 MVP</p>

      <section className="panel">
        <label>User ID</label>
        <input value={userId} onChange={(e) => setUserId(e.target.value)} />

        <label>Project Name</label>
        <input value={projectName} onChange={(e) => setProjectName(e.target.value)} />

        <button onClick={createProject}>Create Project</button>
      </section>

      <section
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
      >
        <strong>Drag & Drop Video File</strong>
        <p>mp4, mov, mkv, webm</p>
        <input
          type="file"
          accept="video/mp4,video/quicktime,video/x-matroska,video/webm"
          onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])}
        />
      </section>

      <pre>{message}</pre>
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
