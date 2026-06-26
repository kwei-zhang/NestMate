import { Link } from "react-router-dom";

import { useMyListings, useRepublish } from "../api/hooks";
import { formatDate } from "../utils/date";

const STATUS: Record<string, { label: string; cls: string }> = {
  published: { label: "已发布", cls: "bg-green-100 text-green-700" },
  expired: { label: "已过期", cls: "bg-amber-100 text-amber-700" },
  archived: { label: "已归档", cls: "bg-gray-100 text-gray-600" },
  hidden: { label: "已被管理员隐藏", cls: "bg-red-100 text-red-600" },
  pending_review: { label: "审核中", cls: "bg-blue-100 text-blue-700" },
};

export default function MyPosts() {
  const { data, isLoading } = useMyListings();
  const republish = useRepublish();

  if (isLoading) return <p className="text-gray-400 text-center py-8">加载中…</p>;
  if (!data || data.length === 0)
    return <p className="text-gray-400 text-center py-8">你还没有发布过帖子</p>;

  return (
    <div className="space-y-3">
      <h1 className="text-lg font-semibold">我的发布</h1>
      <p className="text-xs text-gray-400">超过一个月没有修改的帖子会自动隐藏（过期），可随时重新发布。</p>
      {data.map((l) => {
        const s = STATUS[l.status] ?? { label: l.status, cls: "bg-gray-100 text-gray-600" };
        const canRepublish = l.status === "expired" || l.status === "archived";
        return (
          <div key={l.id} className="bg-white border rounded-lg p-4 flex items-center gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <Link to={`/listing/${l.id}`} className="font-medium truncate hover:text-nest">
                  {l.title ?? "未命名房源"}
                </Link>
                <span className={`text-xs px-2 py-0.5 rounded-full ${s.cls}`}>{s.label}</span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">最后更新 {formatDate(l.updated_at)}</p>
            </div>
            <div className="flex items-center gap-3 text-sm">
              {canRepublish && (
                <button
                  onClick={() => republish.mutate(l.id)}
                  className="text-nest hover:underline"
                >
                  重新发布
                </button>
              )}
              <Link to={`/listing/${l.id}/edit`} className="text-gray-500 hover:text-nest">
                编辑
              </Link>
            </div>
          </div>
        );
      })}
    </div>
  );
}
