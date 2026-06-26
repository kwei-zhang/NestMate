import { useParams } from "react-router-dom";

import { useListing } from "../api/hooks";
import ContactGate from "../components/ContactGate";

export default function ListingDetail() {
  const { id } = useParams();
  const listingId = Number(id);
  const { data, isLoading, isError } = useListing(listingId);

  if (isLoading) return <p className="text-gray-400 text-center py-8">加载中…</p>;
  if (isError || !data) return <p className="text-red-500 text-center py-8">房源不存在或已下架</p>;

  return (
    <article className="bg-white rounded-lg border p-6 space-y-4 max-w-2xl mx-auto">
      <div className="flex items-center gap-2">
        <span className="text-xs px-2 py-0.5 rounded bg-nest/10 text-nest">
          {data.intent === "offering" ? "招租" : data.intent === "seeking" ? "求租" : "房源"}
        </span>
        {data.area && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
            {data.area}
          </span>
        )}
      </div>

      <h1 className="text-xl font-semibold">{data.title ?? "未命名房源"}</h1>

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
