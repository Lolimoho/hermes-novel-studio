export type ChapterStatus = "not_started" | "draft" | "finalized";

export interface Project {
  id: string;
  title: string;
  genre: string;
  audience: string;
  language: string;
  total_chapters: number;
  words_per_chapter: number;
  premise: string;
  world_text: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectSummary extends Project {
  chapter_count: number;
  finalized_count: number;
  character_count: number;
  word_count: number;
}

export interface Character {
  id: string;
  project_id: string;
  name: string;
  level: string;
  function: string;
  desire: string;
  flaw: string;
  arc_note: string;
  status_note: string;
}

export interface Volume {
  id: string;
  project_id: string;
  seq: number;
  name: string;
  core_function: string;
  end_state: string;
}

export interface ChapterPlan {
  id: string;
  title: string;
  goal: string;
  conflict: string;
  hook: string;
  cast: string;
  words: number;
}

export interface Chapter {
  id: string;
  project_id: string;
  seq: number;
  status: ChapterStatus;
  current_revision_id: string | null;
  plan: ChapterPlan | null;
}

export interface Revision {
  id: string;
  chapter_id: string;
  seq_no: number;
  content: string;
  source: "ai" | "human" | "import";
  accepted_at: string | null;
  approved_at: string | null;
  created_at: string;
}

export interface Finding {
  id: string;
  chapter_id: string;
  revision_id: string;
  round: number;
  severity: "block" | "warn" | "hint";
  category: string;
  text: string;
  status: "pending" | "accepted" | "rejected";
}

export interface ChapterDetail extends Chapter {
  revisions: Revision[];
  findings: Finding[];
}

export interface Run {
  id: string;
  project_id: string;
  chapter_id: string | null;
  kind: string;
  status: "running" | "succeeded" | "failed" | "cancelled";
  provider: string;
  model: string;
  started_at: string;
  finished_at: string | null;
  output_summary: string;
  error: string;
}
