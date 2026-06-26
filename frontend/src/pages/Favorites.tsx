import { Link } from "react-router-dom";

import { useFavorites, useRemoveFavorite, useUpdateFavorite } from "../api/hooks";

const STATUS_LABELS: Record<string, string> = {
  saved: "已收藏",
  contacted: "已联系",
  closed: "已关闭",
};

export default function Favorites() {
  const { data, isLoading } = useFavorites();
  const update = useUpdateFavorite();
  const remove = useRemoveFavorite();

  if (isLoading) return <p className="text-gray-400 text-center py-8">加载中…</p>;
  if (!data || data.length === 0)
    return <p className="text-gray-400 text-center py-8">还没有收藏的房源</p>;

  return (
    <div className="space-y-3">
      <h1 className="text-lg font-semibold">我的收藏</h1>
      {data.map((f) => (
        <div
          key={f.listing_id}
          className="bg-white border rounded-lg p-4 flex items-center justify-between gap-3"
        >
          <Link to={`/listing/${f.listing_id}`} className="text-nest hover:underline">
            房源 #{f.listing_id}
          </Link>
          <div className="flex items-center gap-2">
            <select
              className="border rounded px-2 py-1 text-sm"
              value={f.personal_status}
              onChange={(e) =>
                update.mutate({ listingId: f.listing_id, personal_status: e.target.value })
              }
            >
              {Object.entries(STATUS_LABELS).map(([v, label]) => (
                <option key={v} value={v}>
                  {label}
                </option>
              ))}
            </select>
            <button
              onClick={() => remove.mutate(f.listing_id)}
              className="text-sm text-gray-400 hover:text-red-500"
            >
              删除
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
