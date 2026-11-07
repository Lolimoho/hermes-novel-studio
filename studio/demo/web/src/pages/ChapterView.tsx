import { useEffect, useState } from "react";
import { api } from "../api";
import { navigate } from "../router";
import type { Chapter, ChapterDetail, Project, Revision } from "../types";

const STATUS_LABEL: Record<string, string> = {
  not_started: "待写",
  draft: "草稿",
  finalized: "定稿",
};

const ROUND_LABEL: Record<number, string> = {
  1: "结构",
  2: "事实",
  3: "阅读体验",
  4: "项目规则",
};

function fmt(s: string | null) {
  if (!s) return "—";
  return s.slice(0, 16).replace("T", " ");
}

export default function ChapterView({
  project,
  chapterId,
  notify,
}: {
  project: Project;
  chapterId?: string;
  notify: (m: string, e?: boolean) => void;
}) {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [detail, setDetail] = useState<ChapterDetail | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState("");
  const [note, setNote] = useState("");

  const loadList = async () => {
    try {
      setChapters(await api.listChapters(project.id));
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  const load = async () => {
    if (!chapterId) return;
    try {
      const data = await api.getChapter(chapterId);
      setDetail(data);
      setEditing(false);
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  useEffect(() => {
    if (chapterId) {
      void load();
    } else {
      void loadList();
    }
  }, [chapterId, project.id]);

  if (!chapterId) {
    return (
      <>
        <h1>正文</h1>
        <p className="sub">选一章进入单章视图。草稿、候选、审稿、定稿都在同一页完成。</p>
        {chapters.length === 0 ? (
          <div className="empty">
            还没有章节。先去<button className="btn btn-ghost" onClick={() => navigate(`p/${project.id}/blueprint`)}>蓝图</button>生成。
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: 46 }}>章</th>
                <th style={{ width: 160 }}>标题</th>
                <th>目标</th>
                <th style={{ width: 80 }}>状态</th>
                <th style={{ width: 70 }} />
              </tr>
            </thead>
            <tbody>
              {chapters.map((c) => (
                <tr key={c.id}>
                  <td className="mono">{c.seq}</td>
                  <td>{c.plan?.title || "—"}</td>
                  <td className="plan-cell">{c.plan?.goal || "—"}</td>
                  <td>
                    <span className={`badge ${c.status}`}>{STATUS_LABEL[c.status]}</span>
                  </td>
                  <td>
                    <button
                      className="btn btn-ghost"
                      onClick={() => navigate(`p/${project.id}/chapter/${c.id}`)}
                    >
                      打开
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </>
    );
  }

  if (!detail) return <div className="empty">读取中…</div>;

  const currentRev = detail.revisions.find((r) => r.id === detail.current_revision_id) || null;
  const candidate = [...detail.revisions]
    .reverse()
    .find((r) => r.source === "ai" && !r.accepted_at) || null;
  const findings = detail.findings.filter((f) => f.revision_id === currentRev?.id);
  const pendingBlocks = findings.filter((f) => f.severity === "block" && f.status === "pending");
  const shown = editing ? text : candidate ? candidate.content : currentRev?.content || "";

  const run = async (name: string, fn: () => Promise<unknown>, ok: string) => {
    setBusy(name);
    try {
      await fn();
      await load();
      notify(ok);
    } catch (e) {
      notify((e as Error).message, true);
    } finally {
      setBusy(null);
    }
  };

  return (
    <>
      <div className="row" style={{ marginBottom: 6 }}>
        <button className="btn btn-ghost" onClick={() => navigate(`p/${project.id}/chapter`)}>
          ← 章节列表
        </button>
        <div className="spacer" />
        <span className={`badge ${detail.status}`}>{STATUS_LABEL[detail.status]}</span>
      </div>

      <h1>
        第 {detail.seq} 章 · {detail.plan?.title || "未命名"}
      </h1>
      <p className="sub">
        {detail.plan?.words || project.words_per_chapter} 字目标
        {currentRev ? ` · 当前 v${currentRev.seq_no}（${currentRev.source}）` : " · 尚无正文"}
        {candidate ? " · 有候选稿待处理" : ""}
      </p>

      <div className="chapter-layout">
        <div>
          {detail.plan && (
            <div className="section" style={{ paddingTop: 0 }}>
              <h3>本章蓝图</h3>
              <div className="plan-cell" style={{ display: "grid", gap: 6 }}>
                <div>
                  <b>目标：</b>
                  {detail.plan.goal || "—"}
                </div>
                <div>
                  <b>冲突：</b>
                  {detail.plan.conflict || "—"}
                </div>
                <div>
                  <b>钩子：</b>
                  {detail.plan.hook || "—"}
                </div>
                <div>
                  <b>出场：</b>
                  {detail.plan.cast || "—"}
                </div>
              </div>
            </div>
          )}

          {candidate && (
            <div
              className="section"
              style={{ paddingTop: 14, paddingBottom: 14, borderBottom: "1px solid var(--line)" }}
            >
              <div className="row">
                <span className="badge draft">候选稿 v{candidate.seq_no}</span>
                <span className="muted" style={{ fontSize: 12 }}>
                  未经接受，不改变章节状态
                </span>
                <div className="spacer" />
                <button
                  className="btn btn-primary"
                  disabled={busy !== null}
                  onClick={() => run("accept", () => api.acceptCandidate(detail.id), "已接受为草稿")}
                >
                  {busy === "accept" ? "处理中…" : "接受为草稿"}
                </button>
              </div>
            </div>
          )}

          <div className="section">
            <div className="row" style={{ marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>正文</h3>
              <div className="spacer" />
              <span className="muted mono">{shown.length} 字</span>
              {detail.status === "draft" && !candidate && (
                <button
                  className="btn btn-ghost"
                  onClick={() => {
                    if (editing) {
                      setEditing(false);
                    } else {
                      setText(currentRev?.content || "");
                      setEditing(true);
                    }
                  }}
                >
                  {editing ? "取消编辑" : "手动修改"}
                </button>
              )}
            </div>

            {editing ? (
              <>
                <textarea
                  className="editor"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
                <div className="row" style={{ marginTop: 12 }}>
                  <button
                    className="btn btn-primary"
                    disabled={busy !== null}
                    onClick={() => run("save", () => api.saveDraft(detail.id, text), "已保存为新版本")}
                  >
                    {busy === "save" ? "保存中…" : "保存为新版本"}
                  </button>
                  <button className="btn" onClick={() => setEditing(false)}>
                    取消
                  </button>
                </div>
              </>
            ) : shown ? (
              <div className="prose">
                {shown.split(/\n{2,}/).map((p, i) => (
                  <p key={i}>{p}</p>
                ))}
              </div>
            ) : (
              <div className="empty">这一章还没有正文。右侧点「AI 写稿」生成候选。</div>
            )}
          </div>
        </div>

        <aside className="aside">
          <h3>动作</h3>
          <div style={{ display: "grid", gap: 8 }}>
            <input
              className="input"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="给这一次写作的指导（可空）"
            />
            <button
              className="btn btn-primary"
              disabled={busy !== null}
              onClick={() => run("gen", () => api.generateDraft(detail.id, note), "候选稿已生成")}
            >
              {busy === "gen" ? "生成中…" : "AI 写稿"}
            </button>
            <button
              className="btn"
              disabled={busy !== null || !currentRev}
              onClick={() => run("review", () => api.review(detail.id), "审稿完成")}
            >
              {busy === "review" ? "审稿中…" : "审稿"}
            </button>
            {detail.status === "finalized" ? (
              <button
                className="btn"
                disabled={busy !== null}
                onClick={() => run("reopen", () => api.reopen(detail.id), "已重新打开为草稿")}
              >
                重新打开
              </button>
            ) : (
              <button
                className="btn"
                disabled={busy !== null || detail.status !== "draft" || pendingBlocks.length > 0}
                onClick={() => run("finalize", () => api.finalize(detail.id), "已定稿")}
              >
                {busy === "finalize" ? "处理中…" : "定稿"}
              </button>
            )}
            {pendingBlocks.length > 0 && (
              <p className="muted" style={{ fontSize: 11.5, margin: 0 }}>
                有 {pendingBlocks.length} 条阻断意见未处理，定稿被拦。
              </p>
            )}
          </div>

          <div className="section" style={{ marginTop: 8 }}>
            <h3>审稿意见 {findings.length ? `(${findings.length})` : ""}</h3>
            {findings.length === 0 ? (
              <p className="muted" style={{ fontSize: 12 }}>
                还没有意见。点上方「审稿」。
              </p>
            ) : (
              findings.map((f) => (
                <div key={f.id} className="finding">
                  <div className="row">
                    <span className={`badge ${f.severity}`}>{f.severity}</span>
                    <span className="muted" style={{ fontSize: 11 }}>
                      第{f.round}轮 · {ROUND_LABEL[f.round] || f.category}
                    </span>
                    <div className="spacer" />
                    {f.status === "pending" ? (
                      <>
                        <button
                          className="btn btn-ghost"
                          style={{ padding: "2px 6px", fontSize: 11 }}
                          onClick={async () => {
                            await api.updateFinding(f.id, "accepted");
                            await load();
                          }}
                        >
                          采纳
                        </button>
                        <button
                          className="btn btn-ghost"
                          style={{ padding: "2px 6px", fontSize: 11 }}
                          onClick={async () => {
                            await api.updateFinding(f.id, "rejected");
                            await load();
                          }}
                        >
                          忽略
                        </button>
                      </>
                    ) : (
                      <span className="muted" style={{ fontSize: 11 }}>
                        {f.status === "accepted" ? "已采纳" : "已忽略"}
                      </span>
                    )}
                  </div>
                  <p>{f.text}</p>
                </div>
              ))
            )}
          </div>

          <div className="section" style={{ borderBottom: "none" }}>
            <h3>版本 {detail.revisions.length ? `(${detail.revisions.length})` : ""}</h3>
            {detail.revisions.length === 0 ? (
              <p className="muted" style={{ fontSize: 12 }}>
                暂无版本。
              </p>
            ) : (
              [...detail.revisions].reverse().map((r: Revision) => (
                <div key={r.id} className="rev-item">
                  <span className={r.id === detail.current_revision_id ? "rev-current" : ""}>
                    v{r.seq_no} · {r.source}
                    {r.id === detail.current_revision_id ? " · 当前" : ""}
                  </span>
                  <span className="muted mono">{fmt(r.created_at)}</span>
                  {r.id !== detail.current_revision_id && (
                    <button
                      className="btn btn-ghost"
                      style={{ padding: "1px 6px", fontSize: 11 }}
                      onClick={() => run("revert", () => api.revert(detail.id, r.id), "已回退为新版本")}
                    >
                      回退
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </aside>
      </div>
    </>
  );
}
