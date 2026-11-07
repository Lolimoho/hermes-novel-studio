import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { navigate, useHash } from "./router";
import type { Project } from "./types";
import Library from "./pages/Library";
import Settings from "./pages/Settings";
import Architecture from "./pages/Architecture";
import Blueprint from "./pages/Blueprint";
import ChapterView from "./pages/ChapterView";
import Runs from "./pages/Runs";

type Toast = { message: string; error?: boolean } | null;

const NAV = [
  { key: "settings", label: "设定" },
  { key: "architecture", label: "架构" },
  { key: "blueprint", label: "蓝图" },
  { key: "chapter", label: "正文" },
  { key: "runs", label: "运行" },
];

export default function App() {
  const hash = useHash();
  const [project, setProject] = useState<Project | null>(null);
  const [toast, setToast] = useState<Toast>(null);
  const [error, setError] = useState<string | null>(null);

  const segments = hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  const pid = segments[0] === "p" ? segments[1] : null;
  const page = pid ? segments[2] || "settings" : "library";
  const rest = segments.slice(3);

  const notify = useCallback((message: string, isError = false) => {
    setToast({ message, error: isError });
    window.setTimeout(() => setToast(null), 3200);
  }, []);

  const reloadProject = useCallback(async () => {
    if (!pid) return;
    try {
      setProject(await api.getProject(pid));
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [pid]);

  useEffect(() => {
    setProject(null);
    void reloadProject();
  }, [reloadProject]);

  if (!pid) {
    return (
      <>
        <Library notify={notify} />
        {toast && <div className={`toast ${toast.error ? "error" : ""}`}>{toast.message}</div>}
      </>
    );
  }

  return (
    <div className="app">
      <aside className="side">
        <div className="brand">
          Novel Studio
          <small>验证 demo</small>
        </div>

        <div className="side-project">
          <h2>{project?.title || "读取中…"}</h2>
          <p>{project ? `${project.genre || "未设类型"} · 计划 ${project.total_chapters} 章` : ""}</p>
        </div>

        <nav className="nav">
          {NAV.map((item) => {
            const active = item.key === "chapter" ? page === "chapter" : page === item.key;
            return (
              <button
                key={item.key}
                className={`nav-item ${active ? "active" : ""}`}
                onClick={() => navigate(`p/${pid}/${item.key}`)}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        <button className="btn btn-ghost" onClick={() => navigate("")} style={{ textAlign: "left" }}>
          ← 返回书房
        </button>

        <div className="side-foot">
          内容以版本记录，候选稿需人接受
          <br />
          Agent: mock
        </div>
      </aside>

      <main className="main">
        {error && <div className="empty">{error}</div>}
        {!error && !project && <div className="empty">正在读取作品…</div>}
        {!error && project && page === "settings" && (
          <Settings project={project} onSaved={reloadProject} notify={notify} />
        )}
        {!error && project && page === "architecture" && (
          <Architecture project={project} notify={notify} />
        )}
        {!error && project && page === "blueprint" && (
          <Blueprint project={project} notify={notify} />
        )}
        {!error && project && page === "chapter" && (
          <ChapterView project={project} chapterId={rest[0]} notify={notify} />
        )}
        {!error && project && page === "runs" && <Runs project={project} />}
      </main>

      {toast && <div className={`toast ${toast.error ? "error" : ""}`}>{toast.message}</div>}
    </div>
  );
}
