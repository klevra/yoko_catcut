const API_URL =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;

export interface AuthSession {
  user_id: string;
  token: string;
  users_file: string;
}

export function getAuthSession(): AuthSession | null {
  const raw = window.localStorage.getItem("yoko-auth");
  return raw ? JSON.parse(raw) : null;
}

export function setAuthSession(session: AuthSession | null) {
  if (session) {
    window.localStorage.setItem("yoko-auth", JSON.stringify(session));
  } else {
    window.localStorage.removeItem("yoko-auth");
  }
}

function authHeaders(extra: Record<string, string> = {}) {
  const token = getAuthSession()?.token;
  return {
    ...extra,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function authQuery() {
  const token = getAuthSession()?.token;
  return token ? `?token=${encodeURIComponent(token)}` : "";
}

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || `Request failed with status ${response.status}`);
  }
  return data as T;
}

export interface Project {
  user_id: string;
  project_name: string;
  path: string;
  created_at: string;
  updated_at: string;
}

export interface MediaMetadata {
  duration: number | null;
  format: string | null;
  size: number | null;
  bit_rate: number | null;
  video: {
    codec: string | null;
    width: number | null;
    height: number | null;
    fps: number | null;
    pixel_format: string | null;
  };
  audio: {
    codec: string | null;
    sample_rate: number | null;
    channels: number | null;
  } | null;
}

export interface Job {
  job_id: string;
  user_id: string;
  project_name: string;
  job_type: string;
  status: string;
  metadata: {
    upload_id?: string;
    path?: string;
    media?: MediaMetadata;
    error?: string;
    subtitle_files?: SubtitleResult;
    export?: ExportResult;
  };
  created_at: string;
  updated_at: string;
}

export interface UploadResult {
  message: string;
  upload: Upload;
  job: Job;
}

export interface Upload {
  upload_id: string;
  user_id: string;
  project_name: string;
  filename: string;
  path: string;
  file_size: number;
  duration: number | null;
  metadata: MediaMetadata;
  created_at: string;
}

export interface SubtitleSegment {
  id: number;
  start: number;
  end: number;
  text: string;
  speaker_id?: string;
}

export interface SubtitleResult {
  upload_id: string;
  language: string;
  language_probability: number;
  duration?: number;
  segments: SubtitleSegment[];
  json?: string;
  srt?: string;
  vtt?: string;
}

export interface SpeechSpeaker {
  speaker_id: string;
  label: string;
  content_type: "speech" | "music";
  segment_count: number;
  duration: number;
  selected: boolean;
  preview: string;
}

export interface SpeechAnalysis {
  upload_id: string;
  language: string;
  language_probability: number;
  duration?: number;
  pipeline: string[];
  speakers: SpeechSpeaker[];
  segments: Array<SubtitleSegment & {
    speaker_id: string;
    music_score: number;
    content_type: "speech" | "music";
  }>;
}

export interface EditSegmentPayload {
  start: number;
  end: number;
  comment: string;
}

export interface ProcessingOptionsPayload {
  remove_silence: boolean;
  speed_up_excluded: boolean;
  excluded_speed: 2 | 4 | 8 | 16;
  assembly_only: boolean;
  remove_background_music: boolean;
  add_background_music: boolean;
  background_music_volume: number;
}

export interface ExportResult {
  export_id: string;
  editor_tool: string;
  aspect_ratio: string;
  subtitle_count: number;
  video: string;
  subtitle: string | null;
  capcut_package: string;
}

export const api = {
  login: (userId: string, password: string) =>
    fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, password }),
    }).then((r) => parseResponse<AuthSession>(r)),

  // Projects
  createProject: (userId: string, projectName: string) =>
    fetch(`${API_URL}/projects`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ user_id: userId, project_name: projectName }),
    }).then((r) => parseResponse<Project>(r)),

  listProjects: (userId: string) =>
    fetch(`${API_URL}/projects/${userId}`, {
      headers: authHeaders(),
    }).then((r) =>
      parseResponse<Project[]>(r)
    ),

  getProject: (userId: string, projectName: string) =>
    fetch(`${API_URL}/projects/${userId}/${projectName}`, {
      headers: authHeaders(),
    }).then((r) =>
      parseResponse<Project>(r)
    ),

  updateProject: (userId: string, projectName: string, newName: string) =>
    fetch(`${API_URL}/projects/${userId}/${projectName}`, {
      method: "PUT",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ project_name: newName }),
    }).then((r) => parseResponse<Project>(r)),

  deleteProject: (userId: string, projectName: string) =>
    fetch(`${API_URL}/projects/${userId}/${projectName}`, {
      method: "DELETE",
      headers: authHeaders(),
    }).then((r) => parseResponse<{ success: boolean; message: string }>(r)),

  // Uploads
  uploadFile: (userId: string, projectName: string, file: File) => {
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("project_name", projectName);
    formData.append("file", file);

    return fetch(`${API_URL}/uploads`, {
      method: "POST",
      headers: authHeaders(),
      body: formData,
    }).then((r) => parseResponse<UploadResult>(r));
  },

  listUploads: (userId: string, projectName: string) =>
    fetch(
      `${API_URL}/uploads?user_id=${encodeURIComponent(
        userId
      )}&project_name=${encodeURIComponent(projectName)}`
      ,
      { headers: authHeaders() }
    ).then((r) => parseResponse<Upload[]>(r)),

  getUpload: (uploadId: string) =>
    fetch(`${API_URL}/uploads/${uploadId}`, {
      headers: authHeaders(),
    }).then((r) =>
      parseResponse<Upload>(r)
    ),

  createSpeechAnalysis: (uploadId: string, language?: string) => {
    const query = language ? `?language=${encodeURIComponent(language)}` : "";
    return fetch(`${API_URL}/uploads/${uploadId}/speech-analysis${query}`, {
      method: "POST",
      headers: authHeaders(),
    }).then((r) => parseResponse<Job>(r));
  },

  getSpeechAnalysis: (uploadId: string) =>
    fetch(`${API_URL}/uploads/${uploadId}/speech-analysis`, {
      headers: authHeaders(),
    }).then((r) =>
      parseResponse<SpeechAnalysis>(r)
    ),

  createSubtitles: (
    uploadId: string,
    language?: string,
    selectedSpeakers: string[] = []
  ) =>
    fetch(`${API_URL}/uploads/${uploadId}/subtitles`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({
        language: language || null,
        selected_speakers: selectedSpeakers,
      }),
    }).then((r) => parseResponse<Job>(r)),

  getSubtitles: (uploadId: string) =>
    fetch(`${API_URL}/uploads/${uploadId}/subtitles`, {
      headers: authHeaders(),
    }).then((r) =>
      parseResponse<SubtitleResult>(r)
    ),

  updateSubtitles: (uploadId: string, segments: SubtitleSegment[]) =>
    fetch(`${API_URL}/uploads/${uploadId}/subtitles`, {
      method: "PUT",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ segments }),
    }).then((r) => parseResponse<SubtitleResult>(r)),

  createExport: (
    uploadId: string,
    payload: {
      aspect_ratio: string;
      editor_tool: string;
      segments: EditSegmentPayload[];
      burn_subtitles: boolean;
      processing_options: ProcessingOptionsPayload;
    }
  ) =>
    fetch(`${API_URL}/uploads/${uploadId}/exports`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(payload),
    }).then((r) => parseResponse<Job>(r)),

  uploadBackgroundMusic: (uploadId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return fetch(`${API_URL}/uploads/${uploadId}/background-music`, {
      method: "POST",
      headers: authHeaders(),
      body: formData,
    }).then((r) =>
      parseResponse<{
        upload_id: string;
        filename: string;
        path: string;
        file_size: number;
      }>(r)
    );
  },

  // Jobs
  getJob: (jobId: string) =>
    fetch(`${API_URL}/jobs/${jobId}`, { headers: authHeaders() }).then((r) =>
      parseResponse<Job>(r)
    ),

  listJobs: (userId: string, projectName: string) =>
    fetch(
      `${API_URL}/jobs?user_id=${userId}&project_name=${projectName}`,
      { headers: authHeaders() }
    ).then((r) => parseResponse<Job[]>(r)),

  updateJobStatus: (jobId: string, status: string) =>
    fetch(`${API_URL}/jobs/${jobId}/status`, {
      method: "PUT",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ status }),
    }).then((r) => parseResponse<Job>(r)),

  cancelJob: (jobId: string) =>
    fetch(`${API_URL}/jobs/${jobId}/cancel`, {
      method: "POST",
      headers: authHeaders(),
    }).then((r) => parseResponse<Job>(r)),
};

export function getUploadContentUrl(uploadId: string) {
  return `${API_URL}/uploads/${uploadId}/content${authQuery()}`;
}

export function getSubtitleFileUrl(
  uploadId: string,
  fileFormat: "srt" | "vtt" | "json"
) {
  return `${API_URL}/uploads/${uploadId}/subtitles/${fileFormat}${authQuery()}`;
}

export function getSpeakerPreviewUrl(uploadId: string, speakerId: string) {
  return `${API_URL}/uploads/${uploadId}/speech-analysis/speakers/${encodeURIComponent(
    speakerId
  )}/preview${authQuery()}`;
}

export function getExportFileUrl(uploadId: string, exportId: string) {
  return `${API_URL}/uploads/${uploadId}/exports/${exportId}${authQuery()}`;
}

export function getCapCutPackageUrl(uploadId: string, exportId: string) {
  return `${API_URL}/uploads/${uploadId}/exports/${exportId}/capcut${authQuery()}`;
}
