import type {
  Chapter,
  ChapterDetail,
  Character,
  Finding,
  Project,
  ProjectSummary,
  Revision,
  Run,
  Volume,
} from "./types";

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(path, {
    method,
    headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const message = (data && (data.detail || data.message)) || `请求失败 (${res.status})`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return data as T;
}

export const api = {
  listProjects: () => request<ProjectSummary[]>("GET", "/api/projects"),
  createProject: (body: Partial<Project>) => request<Project>("POST", "/api/projects", body),
  getProject: (id: string) => request<Project>("GET", `/api/projects/${id}`),
  updateProject: (id: string, body: Partial<Project>) =>
    request<Project>("PATCH", `/api/projects/${id}`, body),
  deleteProject: (id: string) => request<void>("DELETE", `/api/projects/${id}`),

  listCharacters: (pid: string) => request<Character[]>("GET", `/api/projects/${pid}/characters`),
  createCharacter: (pid: string, body: Partial<Character>) =>
    request<Character>("POST", `/api/projects/${pid}/characters`, body),
  updateCharacter: (cid: string, body: Partial<Character>) =>
    request<Character>("PATCH", `/api/projects/characters/${cid}`, body),
  deleteCharacter: (cid: string) => request<void>("DELETE", `/api/projects/characters/${cid}`),

  listVolumes: (pid: string) => request<Volume[]>("GET", `/api/projects/${pid}/volumes`),
  createVolume: (pid: string, body: Partial<Volume>) =>
    request<Volume>("POST", `/api/projects/${pid}/volumes`, body),
  updateVolume: (vid: string, body: Partial<Volume>) =>
    request<Volume>("PATCH", `/api/projects/volumes/${vid}`, body),
  deleteVolume: (vid: string) => request<void>("DELETE", `/api/projects/volumes/${vid}`),

  listChapters: (pid: string) => request<Chapter[]>("GET", `/api/projects/${pid}/chapters`),
  generatePlans: (pid: string, body: { start_seq: number; count: number; words?: number }) =>
    request<Chapter[]>("POST", `/api/projects/${pid}/chapters/generate-plans`, body),
  updatePlan: (chapterId: string, body: Record<string, unknown>) =>
    request<Chapter>("PATCH", `/api/chapters/${chapterId}/plan`, body),

  getChapter: (id: string) => request<ChapterDetail>("GET", `/api/chapters/${id}`),
  generateDraft: (id: string, note = "") =>
    request<Revision>("POST", `/api/chapters/${id}/generate`, { note }),
  acceptCandidate: (id: string) => request<Chapter>("POST", `/api/chapters/${id}/accept-candidate`),
  saveDraft: (id: string, content: string) =>
    request<Chapter>("POST", `/api/chapters/${id}/save-draft`, { content }),
  review: (id: string) => request<Finding[]>("POST", `/api/chapters/${id}/review`),
  updateFinding: (fid: string, status: string) =>
    request<Finding>("PATCH", `/api/findings/${fid}`, { status }),
  finalize: (id: string) => request<Chapter>("POST", `/api/chapters/${id}/finalize`),
  reopen: (id: string) => request<Chapter>("POST", `/api/chapters/${id}/reopen`),
  revert: (id: string, revisionId: string) =>
    request<Chapter>("POST", `/api/chapters/${id}/revert/${revisionId}`),

  listRuns: (pid?: string) =>
    request<Run[]>("GET", pid ? `/api/runs?project_id=${pid}` : "/api/runs"),
};
