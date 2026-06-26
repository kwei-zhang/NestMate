import { useState } from "react";
import { Link } from "react-router-dom";

import { useAdminListings, useHideListing } from "../api/hooks";
import { formatDate } from "../utils/date";

const STATUS_LABELS: Record<string, string> = {
  published: "已发布",
  hidden: "已隐藏",
  expired: "已过期",
  archived: "已归档",
  pending_review: "审核中",
};

const FILTERS = ["", "published", "hidden", "expired", "pending_review", "archived"];

export default function AdminListings() {
  const [status, setStatus] = useState("");
  const { data, isLoading } = useAdminListings(status || undefined);
  const hide = useHideListing();

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold">全部帖子</h1>
        <select
          className="border rounded px-2 py-1 text-sm ml-auto"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          {FILTERS.map((f) => (
            <option key={f} value={f}>
              {f === "" ? "全部状态" : STATUS_LABELS[f]}
            </option>
          ))}
        </select>
      </div>

      {isLoading && <p className="text-gray-400 text-center py-8">加载中…</p>}
      {data?.length === 0 && <p className="text-gray-400 text-sm">没有帖子</p>}

      {data?.map((l) => {
        const isHidden = l.status !== "published";
        return (
          <div key={l.id} className="bg-white border rounded-lg p-4 flex items-center gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <Link to={`/listing/${l.id}`} className="font-medium truncate hover:text-nest">
                  {l.title ?? "未命名房源"}
                </Link>
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                  {STATUS_LABELS[l.status] ?? l.status}
                </span>
                <span className="text-xs text-gray-400">{l.source === "xhs" ? "小红书" : "用户"}</span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">
                {l.area ?? "—"} · 最后更新 {formatDate(l.updated_at)}
              </p>
            </div>
            <button
              onClick={() => hide.mutate({ id: l.id, hide: !isHidden })}
              className="text-sm text-gray-500 hover:text-nest"
            >
              {isHidden ? "取消隐藏" : "隐藏"}
            </button>
          </div>
        );
      })}
    </div>
  );
}
