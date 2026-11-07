import { useState } from "react";
import { api } from "../api";
import type { Project } from "../types";

export default function Settings({
  project,
  onSaved,
  notify,
}: {
  project: Project;
  onSaved: () => Promise<void>;
  notify: (m: string, e?: boolean) => void;
}) {
  const [form, setForm] = useState({
    title: project.title,
    genre: project.genre,
    audience: project.audience,
    total_chapters: project.total_chapters,
    words_per_chapter: project.words_per_chapter,
    premise: project.premise,
    world_text: project.world_text,
  });
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      await api.updateProject(project.id, form);
      await onSaved();
      notify("设定已保存");
    } catch (e) {
      notify((e as Error).message, true);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <h1>设定</h1>
      <p className="sub">这一层决定「写什么」。章数与每章字数会作为蓝图的默认目标。</p>

      <div className="section">
        <div className="grid-2">
          <div className="field">
            <label>作品名</label>
            <input
              className="input"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </div>
          <div className="field">
            <label>类型</label>
            <input
              className="input"
              value={form.genre}
              onChange={(e) => setForm({ ...form, genre: e.target.value })}
            />
          </div>
        </div>

        <div className="grid-3">
          <div className="field">
            <label>目标读者</label>
            <input
              className="input"
              value={form.audience}
              onChange={(e) => setForm({ ...form, audience: e.target.value })}
            />
          </div>
          <div className="field">
            <label>计划章数</label>
            <input
              className="input"
              type="number"
              value={form.total_chapters}
              onChange={(e) => setForm({ ...form, total_chapters: Number(e.target.value) })}
            />
          </div>
          <div className="field">
            <label>每章字数</label>
            <input
              className="input"
              type="number"
              value={form.words_per_chapter}
              onChange={(e) => setForm({ ...form, words_per_chapter: Number(e.target.value) })}
            />
          </div>
        </div>
      </div>

      <div className="section">
        <h3>一句话前提</h3>
        <textarea
          className="textarea"
          value={form.premise}
          onChange={(e) => setForm({ ...form, premise: e.target.value })}
          placeholder="谁 + 困境 + 赌注 + 凭什么特别"
        />
      </div>

      <div className="section">
        <h3>世界观</h3>
        <textarea
          className="textarea"
          style={{ minHeight: 160 }}
          value={form.world_text}
          onChange={(e) => setForm({ ...form, world_text: e.target.value })}
          placeholder="时代、地理、规则体系、势力、禁忌。只写与剧情有关的部分。"
        />
      </div>

      <div className="row">
        <button className="btn btn-primary" onClick={save} disabled={saving}>
          {saving ? "保存中…" : "保存设定"}
        </button>
      </div>
    </>
  );
}
