import { useEffect, useState } from "react";
import { api } from "../api";
import type { Character, Project, Volume } from "../types";

const LEVELS = ["L1", "L2", "L3", "L4"];

export default function Architecture({
  project,
  notify,
}: {
  project: Project;
  notify: (m: string, e?: boolean) => void;
}) {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [volumes, setVolumes] = useState<Volume[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [draft, setDraft] = useState<Partial<Character>>({});
  const [newName, setNewName] = useState("");

  const load = async () => {
    try {
      const [cs, vs] = await Promise.all([
        api.listCharacters(project.id),
        api.listVolumes(project.id),
      ]);
      setCharacters(cs);
      setVolumes(vs);
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  useEffect(() => {
    void load();
  }, [project.id]);

  const addCharacter = async () => {
    if (!newName.trim()) return;
    try {
      await api.createCharacter(project.id, { name: newName.trim(), level: "L3" });
      setNewName("");
      await load();
      notify("角色已添加");
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  const startEdit = (c: Character) => {
    setEditing(c.id);
    setDraft({ ...c });
  };

  const saveEdit = async () => {
    if (!editing) return;
    try {
      await api.updateCharacter(editing, draft);
      setEditing(null);
      await load();
      notify("角色已更新");
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  const remove = async (id: string) => {
    try {
      await api.deleteCharacter(id);
      await load();
      notify("角色已删除");
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  const addVolume = async () => {
    try {
      await api.createVolume(project.id, { name: `第 ${volumes.length + 1} 卷` });
      await load();
    } catch (e) {
      notify((e as Error).message, true);
    }
  };

  return (
    <>
      <h1>架构</h1>
      <p className="sub">
        这一层决定「谁在推动故事」。角色按层级填不同深度，卷只写功能与卷末状态，不写事件清单。
      </p>

      <div className="section">
        <div className="row">
          <h2>角色</h2>
          <div className="spacer" />
          <span className="muted mono">{characters.length} 人</span>
        </div>

        {characters.length === 0 ? (
          <div className="empty">还没有角色。先在下面加一个主角。</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: 130 }}>姓名</th>
                <th style={{ width: 60 }}>层级</th>
                <th>功能</th>
                <th style={{ width: 120 }} />
              </tr>
            </thead>
            <tbody>
              {characters.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>
                    <span className="badge">{c.level}</span>
                  </td>
                  <td className="plan-cell">{c.function || <span className="muted">未填</span>}</td>
                  <td>
                    <div className="row">
                      <button className="btn btn-ghost" onClick={() => startEdit(c)}>
                        编辑
                      </button>
                      <button className="btn btn-ghost btn-danger" onClick={() => remove(c.id)}>
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {editing && (
          <div className="section" style={{ borderBottom: "none" }}>
            <h3>编辑角色</h3>
            <div className="grid-3">
              <div className="field">
                <label>姓名</label>
                <input
                  className="input"
                  value={draft.name || ""}
                  onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                />
              </div>
              <div className="field">
                <label>层级</label>
                <select
                  className="select"
                  value={draft.level || "L2"}
                  onChange={(e) => setDraft({ ...draft, level: e.target.value })}
                >
                  {LEVELS.map((l) => (
                    <option key={l}>{l}</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>故事功能</label>
                <input
                  className="input"
                  value={draft.function || ""}
                  onChange={(e) => setDraft({ ...draft, function: e.target.value })}
                  placeholder="推动第二幕转折"
                />
              </div>
            </div>
            <div className="grid-2">
              <div className="field">
                <label>Want（想要什么）</label>
                <textarea
                  className="textarea"
                  value={draft.desire || ""}
                  onChange={(e) => setDraft({ ...draft, desire: e.target.value })}
                />
              </div>
              <div className="field">
                <label>Lie / Wound（谎言与伤痛）</label>
                <textarea
                  className="textarea"
                  value={draft.flaw || ""}
                  onChange={(e) => setDraft({ ...draft, flaw: e.target.value })}
                />
              </div>
            </div>
            <div className="grid-2">
              <div className="field">
                <label>弧线要点</label>
                <textarea
                  className="textarea"
                  value={draft.arc_note || ""}
                  onChange={(e) => setDraft({ ...draft, arc_note: e.target.value })}
                />
              </div>
              <div className="field">
                <label>当前状态</label>
                <textarea
                  className="textarea"
                  value={draft.status_note || ""}
                  onChange={(e) => setDraft({ ...draft, status_note: e.target.value })}
                  placeholder="第 N 章时：受伤 / 失去线索 / 与某人决裂"
                />
              </div>
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

        <div className="row" style={{ marginTop: 18 }}>
          <input
            className="input"
            style={{ maxWidth: 240 }}
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="新角色姓名"
            onKeyDown={(e) => e.key === "Enter" && addCharacter()}
          />
          <button className="btn" onClick={addCharacter}>
            添加角色
          </button>
        </div>
      </div>

      <div className="section">
        <div className="row">
          <h2>卷</h2>
          <div className="spacer" />
          <button className="btn" onClick={addVolume}>
            加一卷
          </button>
        </div>

        {volumes.length === 0 ? (
          <div className="empty">还没有分卷。长篇建议先切 3-4 卷，每卷写清卷末状态。</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: 50 }}>卷</th>
                <th style={{ width: 180 }}>名称</th>
                <th style={{ width: 110 }}>核心功能</th>
                <th>卷末状态（谁做了什么选择 → 什么结果）</th>
              </tr>
            </thead>
            <tbody>
              {volumes.map((v) => (
                <tr key={v.id}>
                  <td className="mono">{v.seq}</td>
                  <td>
                    <input
                      className="input"
                      defaultValue={v.name}
                      onBlur={async (e) => {
                        if (e.target.value !== v.name) {
                          await api.updateVolume(v.id, { name: e.target.value });
                          await load();
                        }
                      }}
                    />
                  </td>
                  <td>
                    <input
                      className="input"
                      defaultValue={v.core_function}
                      placeholder="引入/转折/收束"
                      onBlur={async (e) => {
                        if (e.target.value !== v.core_function) {
                          await api.updateVolume(v.id, { core_function: e.target.value });
                          await load();
                        }
                      }}
                    />
                  </td>
                  <td>
                    <textarea
                      className="textarea"
                      style={{ minHeight: 54 }}
                      defaultValue={v.end_state}
                      onBlur={async (e) => {
                        if (e.target.value !== v.end_state) {
                          await api.updateVolume(v.id, { end_state: e.target.value });
                          await load();
                        }
                      }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
