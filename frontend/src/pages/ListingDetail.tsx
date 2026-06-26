import { Link, useParams } from "react-router-dom";

import { useHideListing, useListing } from "../api/hooks";
import ContactGate from "../components/ContactGate";
import { useAuth } from "../store/auth";
import { formatDate } from "../utils/date";

export default function ListingDetail() {
  const { id } = useParams();
  const listingId = Number(id);
  const { user, isAdmin } = useAuth();
  const { data, isLoading, isError } = useListing(listingId);
  const hide = useHideListing();

  if (isLoading) return <p className="text-gray-400 text-center py-8">加载中…</p>;
  if (isError || !data) return <p className="text-red-500 text-center py-8">房源不存在或已下架</p>;

  const isAuthor = data.created_by != null && data.created_by === user?.id;
  const isHidden = data.status !== "published";

  return (
    <article className="bg-white rounded-lg border p-6 space-y-4 max-w-2xl mx-auto">
      <div className="flex items-center gap-2">
        <span className="text-xs px-2 py-0.5 rounded bg-nest/10 text-nest">
          {data.has_room === true ? "有房源" : data.has_room === false ? "求房源" : "找室友"}
        </span>
        {data.area && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
            {data.area}
          </span>
        )}
        {isHidden && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600">
            {data.status === "expired" ? "已过期" : data.status === "hidden" ? "已隐藏" : data.status}
          </span>
        )}
        <div className="ml-auto flex items-center gap-3 text-sm">
          {isAuthor && (
            <Link to={`/listing/${listingId}/edit`} className="text-nest hover:underline">
              编辑
            </Link>
          )}
          {isAdmin && (
            <button
              onClick={() => hide.mutate({ id: listingId, hide: !isHidden })}
              className="text-gray-400 hover:text-nest"
            >
              {isHidden ? "取消隐藏" : "隐藏"}
            </button>
          )}
        </div>
      </div>

      <h1 className="text-xl font-semibold">{data.title ?? "未命名房源"}</h1>

      {data.images && data.images.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {data.images.map((src) => (
            <a key={src} href={src} target="_blank" rel="noreferrer">
              <img
                src={src}
                alt="房屋图片"
                loading="lazy"
                className="w-full h-32 object-cover rounded-lg border"
              />
            </a>
          ))}
        </div>
      )}

      {data.highlights && data.highlights.length > 0 && (
        <ul className="flex flex-wrap gap-2">
          {data.highlights.map((h) => (
            <li
              key={h}
              className="text-sm px-3 py-1 rounded-full bg-nest/10 text-nest"
            >
              {h}
            </li>
          ))}
        </ul>
      )}

      <dl className="grid grid-cols-2 gap-2 text-sm">
        {data.budget_min || data.budget_max ? (
          <Field label="预算">
            {data.budget_min ?? "?"}–{data.budget_max ?? "?"} CAD/月
          </Field>
        ) : null}
        {data.mbti && <Field label="MBTI">{data.mbti}</Field>}
        {data.has_pets !== null && <Field label="宠物">{data.has_pets ? "有/可" : "无"}</Field>}
        {data.move_in_date && <Field label="入住">{data.move_in_date}</Field>}
        {data.gender_pref && <Field label="性别偏好">{data.gender_pref}</Field>}
      </dl>

      <p className="whitespace-pre-wrap text-gray-700 leading-relaxed">{data.raw_text}</p>

      <ContactGate listingId={listingId} />

      <div className="text-xs text-gray-400 border-t pt-3 space-y-1">
        <p>最后更新 {formatDate(data.updated_at)}</p>
        {data.source_url && (
          <p>
            原帖：
            <a
              href={data.source_url}
              target="_blank"
              rel="noreferrer"
              className="text-nest hover:underline break-all"
            >
              {data.source_url}
            </a>
          </p>
        )}
        <p>信息来自小红书公开帖子，仅作聚合展示。如为原作者并希望下架，请联系我们。</p>
      </div>
    </article>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="text-gray-400">{label}</dt>
      <dd className="font-medium">{children}</dd>
    </div>
  );
}
