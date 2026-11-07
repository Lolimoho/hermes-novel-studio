import { useEffect, useState } from "react";
import { api } from "../api";
import { navigate } from "../router";
import type { ProjectSummary } from "../types";

export default function Library({ notify }: { notify: (m: string, e?: boolean) => void }) {
  const [items, setItems] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    title: "",
    genre: "",
    audience: "",
    total_chapters: 12,
    words_per_chapter: 2500,
    premise: "",
  });

  const load = async () => {
    try {
      setItems(await api.listProjects());
    } catch (e) {
      notify((e as Error).message, true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const create = async () => {
    if (!form.title.trim()) {
      notify("请先填作品名", true);
      return;
    }
    setSaving(true);
    try {
      const project = await api.createProject(form);
      notify("作品已建立");
      navigate(`p/${project.id}/settings`);
    } catch (e) {
      notify((e as Error).message, true);
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="main" style={{ maxWidth: 1080 }}>
      <div className="row">
        <div>
          <h1>书房</h1>
          <p className="sub">每部作品按「设定 → 架构 → 蓝图 → 正文」推进，AI 只在你按下的那一步动手。</p>
        </div>
        <div className="spacer" />
        <button className="btn btn-primary" onClick={() => setOpen((v) => !v)}>
          {open ? "收起" : "新建作品"}
        </button>
      </div>

      {open && (
        <div className="section">
          <div className="grid-2">
            <div className="field">
              <label>作品名</label>
              <input
                className="input"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="如：雾港来信"
              />
            </div>
            <div className="field">
              <label>类型</label>
              <input
                className="input"
                value={form.genre}
                onChange={(e) => setForm({ ...form, genre: e.target.value })}
                placeholder="悬疑 / 都市 / 古言"
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
          <div className="field">
            <label>一句话前提</label>
            <textarea
              className="textarea"
              value={form.premise}
              onChange={(e) => setForm({ ...form, premise: e.target.value })}
              placeholder="谁 + 困境 + 赌注 + 凭什么特别"
            />
          </div>
          <div className="row">
            <button className="btn btn-primary" onClick={create} disabled={saving}>
              {saving ? "建立中…" : "建立作品"}
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="empty">读取中…</div>
      ) : items.length === 0 ? (
        <div className="empty">还没有作品。点右上角「新建作品」开始。</div>
      ) : (
        <div className="shelf">
          {items.map((p) => (
            <div key={p.id} className="book" onClick={() => navigate(`p/${p.id}/settings`)}>
              <h3>{p.title}</h3>
              <p>{p.premise || "尚未写前提"}</p>
              <div className="book-meta">
                <span>{p.chapter_count} 章</span>
                <span>定稿 {p.finalized_count}</span>
                <span>{p.word_count.toLocaleString()} 字</span>
                <span>{p.character_count} 角色</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
