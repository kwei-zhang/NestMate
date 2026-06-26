import type { ListingFilters } from "../api/types";

const AREAS = [
  "North York",
  "Scarborough",
  "Downtown",
  "Markham",
  "Richmond Hill",
  "Mississauga",
  "Waterloo",
];

interface Props {
  value: ListingFilters;
  onChange: (next: ListingFilters) => void;
}

export default function FilterBar({ value, onChange }: Props) {
  function set<K extends keyof ListingFilters>(key: K, v: ListingFilters[K]) {
    onChange({ ...value, [key]: v === "" ? undefined : v });
  }

  return (
    <div className="bg-white rounded-lg border p-3 flex flex-wrap gap-2 items-center">
      <input
        className="border rounded px-2 py-1 text-sm flex-1 min-w-[160px]"
        placeholder="搜索关键词…"
        value={value.q ?? ""}
        onChange={(e) => set("q", e.target.value)}
      />
      <select
        className="border rounded px-2 py-1 text-sm"
        value={value.intent ?? ""}
        onChange={(e) => set("intent", e.target.value)}
      >
        <option value="">全部</option>
        <option value="offering">招租</option>
        <option value="seeking">求租</option>
      </select>
      <select
        className="border rounded px-2 py-1 text-sm"
        value={value.area ?? ""}
        onChange={(e) => set("area", e.target.value)}
      >
        <option value="">地区</option>
        {AREAS.map((a) => (
          <option key={a} value={a}>
            {a}
          </option>
        ))}
      </select>
      <input
        type="number"
        className="border rounded px-2 py-1 text-sm w-28"
        placeholder="预算上限"
        value={value.budget_max ?? ""}
        onChange={(e) => set("budget_max", e.target.value ? Number(e.target.value) : undefined)}
      />
      <input
        className="border rounded px-2 py-1 text-sm w-20"
        placeholder="MBTI"
        value={value.mbti ?? ""}
        onChange={(e) => set("mbti", e.target.value.toUpperCase())}
      />
      <label className="text-sm flex items-center gap-1">
        <input
          type="checkbox"
          checked={value.has_room === true}
          onChange={(e) => set("has_room", e.target.checked ? true : undefined)}
        />
        有房源
      </label>
      <label className="text-sm flex items-center gap-1">
        <input
          type="checkbox"
          checked={value.has_pets === true}
          onChange={(e) => set("has_pets", e.target.checked ? true : undefined)}
        />
        可养宠物
      </label>
    </div>
  );
}
