import { useEffect, useState } from "react";
import { api } from "../api";
import type { Project, Run } from "../types";

const KIND_LABEL: Record<string, string> = {
  plan_generation: "生成蓝图",
  draft_generation: "写稿",
  review: "审稿",
};

const STATUS_LABEL: Record<string, string> = {
  running: "进行中",
  succeeded: "成功",
  failed: "失败",
  cancelled: "已取消",
};

function duration(r: Run) {
  if (!r.finished_at) return "—";
  const start = new Date(r.started_at).getTime();
  const end = new Date(r.finished_at).getTime();
  const ms = Math.max(0, end - start);
  return ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`;
}

export default function Runs({ project }: { project: Project }) {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      setRuns(await api.listRuns(project.id));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [project.id]);

  return (
    <>
      <div className="row">
        <div>
          <h1>运行</h1>
          <p className="sub">AI 的每一次动作都留一条记录：做了什么、用了多久、产出什么。</p>
        </div>
        <div className="spacer" />
        <button className="btn" onClick={load}>
          刷新
        </button>
      </div>

      {loading ? (
        <div className="empty">读取中…</div>
      ) : runs.length === 0 ? (
        <div className="empty">还没有运行记录。</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: 150 }}>时间</th>
              <th style={{ width: 100 }}>类型</th>
              <th style={{ width: 80 }}>状态</th>
              <th style={{ width: 80 }}>耗时</th>
              <th style={{ width: 110 }}>提供方</th>
              <th>产出</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id}>
                <td className="mono">{r.started_at.slice(0, 16).replace("T", " ")}</td>
                <td>{KIND_LABEL[r.kind] || r.kind}</td>
                <td>
                  <span
                    className={`badge ${r.status === "succeeded" ? "finalized" : r.status === "failed" ? "block" : ""}`}
                  >
                    {STATUS_LABEL[r.status] || r.status}
                  </span>
                </td>
                <td className="mono">{duration(r)}</td>
                <td className="mono">
                  {r.provider}/{r.model}
                </td>
                <td className="plan-cell">{r.output_summary || r.error || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
