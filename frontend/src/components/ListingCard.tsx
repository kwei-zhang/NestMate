import { Link } from "react-router-dom";

import type { Listing } from "../api/types";

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
          {listing.intent === "offering" ? "招租" : listing.intent === "seeking" ? "求租" : "房源"}
        </span>
        {listing.area && <Tag>{listing.area}</Tag>}
      </div>
      <h3 className="font-medium line-clamp-1">{listing.title ?? "未命名房源"}</h3>
      <p className="text-sm text-gray-500 line-clamp-2 mt-1">{listing.raw_text}</p>
      <div className="flex flex-wrap gap-1.5 mt-2">
        {budget && <Tag>{budget}</Tag>}
        {listing.mbti && <Tag>{listing.mbti}</Tag>}
        {listing.has_pets === true && <Tag>🐾 有宠物</Tag>}
        {listing.has_room === true && <Tag>有房源</Tag>}
        {listing.gender_pref && <Tag>{listing.gender_pref}</Tag>}
      </div>
    </Link>
  );
}
