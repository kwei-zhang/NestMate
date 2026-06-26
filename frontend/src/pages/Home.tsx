import { useState } from "react";

import { useListings } from "../api/hooks";
import type { ListingFilters } from "../api/types";
import FilterBar from "../components/FilterBar";
import ListingCard from "../components/ListingCard";

export default function Home() {
  const [filters, setFilters] = useState<ListingFilters>({});
  const { data, isLoading, isError } = useListings(filters);

  return (
    <div className="space-y-4">
      <FilterBar value={filters} onChange={setFilters} />

      {isLoading && <p className="text-gray-400 text-center py-8">加载中…</p>}
      {isError && <p className="text-red-500 text-center py-8">加载失败，请稍后重试</p>}
      {data && data.length === 0 && (
        <p className="text-gray-400 text-center py-8">没有符合条件的房源</p>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        {data?.map((l) => (
          <ListingCard key={l.id} listing={l} />
        ))}
      </div>
    </div>
  );
}
