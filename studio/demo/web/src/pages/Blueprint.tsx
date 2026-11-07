import { useEffect, useState } from "react";
import { api } from "../api";
import { navigate } from "../router";
import type { Chapter, Project } from "../types";

const STATUS_LABEL: Record<string, string> = {
  not_started: "待写",
  draft: "草稿",
  finalized: "定稿",
};

export default function Blueprint({
  project,
  notify,
}: {
  project: Project;
  notify: (m: string, e?: boolean) => void;
}) {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState<Chapter | null>(null);
  const [draft, setDraft] = useState<Record<string, string | number>>({});
  const [count, setCount] = useState(10);

  const load = async () => {
    try {
      setChapters(await api.listChapters(project.id));
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  useEffect(() => {
    void load();
  }, [project.id]);

  const generate = async () => {
    setBusy(true);
    try {
      const start = chapters.length ? chapters[chapters.length - 1].seq + 1 : 1;
      const created = await api.generatePlans(project.id, { start_seq: start, count });
      await load();
      notify(`已生成 ${created.length} 章蓝图`);
    } catch (e) {
      notify((e as Error).message, true);
    } finally {
      setBusy(false);
    }
  };

  const startEdit = (c: Chapter) => {
    if (!c.plan) return;
    setEditing(c);
    setDraft({
      title: c.plan.title,
      goal: c.plan.goal,
      conflict: c.plan.conflict,
      hook: c.plan.hook,
      cast: c.plan.cast,
      words: c.plan.words,
    });
  };

  const saveEdit = async () => {
    if (!editing) return;
    try {
      await api.updatePlan(editing.id, draft);
      setEditing(null);
      await load();
      notify("蓝图已更新");
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  return (
    <>
      <div className="row">
        <div>
          <h1>蓝图</h1>
          <p className="sub">
            这一层决定「每章干什么」。蓝图是写作的唯一依据，AI 写稿只读本章这一条。
          </p>
        </div>
        <div className="spacer" />
        <div className="row">
          <select
            className="select"
            style={{ width: 110 }}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          >
            {[5, 10, 20, 50].map((n) => (
              <option key={n} value={n}>
                生成 {n} 章
              </option>
            ))}
          </select>
          <button className="btn btn-primary" onClick={generate} disabled={busy}>
            {busy ? "生成中…" : "生成蓝图"}
          </button>
        </div>
      </div>

      {chapters.length === 0 ? (
        <div className="empty">还没有蓝图。点右上角「生成蓝图」批量起草，之后再逐章改。</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: 46 }}>章</th>
              <th style={{ width: 130 }}>标题</th>
              <th>目标</th>
              <th>冲突</th>
              <th style={{ width: 120 }}>章末钩子</th>
              <th style={{ width: 60 }}>字数</th>
              <th style={{ width: 66 }}>状态</th>
              <th style={{ width: 100 }} />
            </tr>
          </thead>
          <tbody>
            {chapters.map((c) => (
              <tr key={c.id}>
                <td className="mono">{c.seq}</td>
                <td>{c.plan?.title || "—"}</td>
                <td className="plan-cell">{c.plan?.goal || "—"}</td>
                <td className="plan-cell">{c.plan?.conflict || "—"}</td>
                <td className="plan-cell">{c.plan?.hook || "—"}</td>
                <td className="mono">{c.plan?.words || 0}</td>
                <td>
                  <span className={`badge ${c.status}`}>{STATUS_LABEL[c.status]}</span>
                </td>
                <td>
                  <div className="row">
                    <button className="btn btn-ghost" onClick={() => startEdit(c)}>
                      改
                    </button>
                    <button
                      className="btn btn-ghost"
                      onClick={() => navigate(`p/${project.id}/chapter/${c.id}`)}
                    >
                      写
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {editing && (
        <div className="section" style={{ marginTop: 24 }}>
          <h3>编辑第 {editing.seq} 章蓝图</h3>
          <div className="grid-3">
            <div className="field">
              <label>标题</label>
              <input
                className="input"
                value={String(draft.title || "")}
                onChange={(e) => setDraft({ ...draft, title: e.target.value })}
              />
            </div>
            <div className="field">
              <label>出场人物</label>
              <input
                className="input"
                value={String(draft.cast || "")}
                onChange={(e) => setDraft({ ...draft, cast: e.target.value })}
              />
            </div>
            <div className="field">
              <label>目标字数</label>
              <input
                className="input"
                type="number"
                value={Number(draft.words || 0)}
                onChange={(e) => setDraft({ ...draft, words: Number(e.target.value) })}
              />
            </div>
          </div>
          <div className="field">
            <label>主角本章小目标</label>
            <textarea
              className="textarea"
              value={String(draft.goal || "")}
              onChange={(e) => setDraft({ ...draft, goal: e.target.value })}
            />
          </div>
          <div className="field">
            <label>冲突与转折</label>
            <textarea
              className="textarea"
              value={String(draft.conflict || "")}
              onChange={(e) => setDraft({ ...draft, conflict: e.target.value })}
            />
          </div>
          <div className="field">
            <label>章末钩子</label>
            <input
              className="input"
              value={String(draft.hook || "")}
              onChange={(e) => setDraft({ ...draft, hook: e.target.value })}
            />
          </div>
          <div className="row">
            <button className="btn btn-primary" onClick={saveEdit}>
              保存
            </button>
            <button className="btn" onClick={() => setEditing(null)}>
              取消
            </button>
          </div>
        </div>
      )}
    </>
  );
}
