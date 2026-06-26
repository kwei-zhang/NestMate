import { Link } from "react-router-dom";

import type { Listing } from "../api/types";
import { formatDate } from "../utils/date";

function budgetText(l: Listing): string | null {
  if (l.budget_min && l.budget_max) return `$${l.budget_min}–${l.budget_max}/月`;
  if (l.budget_max) return `≤$${l.budget_max}/月`;
  if (l.budget_min) return `≥$${l.budget_min}/月`;
  return null;
}

function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{children}</span>
  );
}

export default function ListingCard({ listing }: { listing: Listing }) {
  const budget = budgetText(listing);
  return (
    <Link
      to={`/listing/${listing.id}`}
      className="block bg-white rounded-lg border hover:border-nest hover:shadow-sm transition p-4"
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs px-2 py-0.5 rounded bg-nest/10 text-nest">
          {listing.has_room === true ? "有房源" : listing.has_room === false ? "求房源" : "找室友"}
        </span>
        {listing.area && <Tag>{listing.area}</Tag>}
      </div>
      {listing.images && listing.images.length > 0 && (
        <img
          src={listing.images[0]}
          alt="房屋图片"
          loading="lazy"
          className="w-full h-36 object-cover rounded mb-2 border"
        />
      )}
      <h3 className="font-medium line-clamp-1">{listing.title ?? "未命名房源"}</h3>
      <p className="text-sm text-gray-500 line-clamp-2 mt-1">{listing.raw_text}</p>
      <div className="flex flex-wrap gap-1.5 mt-2">
        {budget && <Tag>{budget}</Tag>}
        {listing.mbti && <Tag>{listing.mbti}</Tag>}
        {listing.has_pets === true && <Tag>🐾 有宠物</Tag>}
        {listing.gender_pref && <Tag>{listing.gender_pref}</Tag>}
      </div>
      {listing.highlights && listing.highlights.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {listing.highlights.slice(0, 4).map((h) => (
            <span key={h} className="text-xs px-2 py-0.5 rounded-full bg-nest/10 text-nest">
              {h}
            </span>
          ))}
        </div>
      )}
      <p className="text-xs text-gray-300 mt-2">最后更新 {formatDate(listing.updated_at)}</p>
    </Link>
  );
}
