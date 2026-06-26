import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { api } from "../api/client";
import type { Listing } from "../api/types";

interface AdminListing extends Listing {
  contact_value: string | null;
  check_state: string;
}

function useReviewQueue() {
  return useQuery({
    queryKey: ["admin", "pending"],
    queryFn: async () =>
      (await api.get<AdminListing[]>("/admin/listings", { params: { status: "pending_review" } }))
        .data,
  });
}

function useStale() {
  return useQuery({
    queryKey: ["admin", "stale"],
    queryFn: async () => (await api.get<AdminListing[]>("/admin/stale")).data,
  });
}

export default function AdminIngest() {
  const qc = useQueryClient();
  const [sourceUrl, setSourceUrl] = useState("");
  const [rawText, setRawText] = useState("");
  const queue = useReviewQueue();
  const stale = useStale();

  const ingest = useMutation({
    mutationFn: async () =>
      (
        await api.post("/admin/ingest", {
          source_url: sourceUrl || null,
          raw_text: rawText || null,
        })
      ).data,
    onSuccess: () => {
      setSourceUrl("");
      setRawText("");
      qc.invalidateQueries({ queryKey: ["admin", "pending"] });
    },
  });

  const publish = useMutation({
    mutationFn: (id: number) => api.post(`/admin/listings/${id}/publish`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "pending"] }),
  });

  const recheck = useMutation({
    mutationFn: (id: number) => api.post(`/admin/recheck/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "stale"] }),
  });

  const input = "border rounded px-3 py-2 text-sm w-full";

  return (
    <div className="space-y-8">
      <section className="bg-white border rounded-lg p-6 space-y-3">
        <h1 className="text-lg font-semibold">录入小红书帖子</h1>
        <p className="text-xs text-gray-400">
          只贴链接即可，后端会尝试自动抓取正文；抓取失败时可手动粘贴。AI 会抽取结构化信息和生活习惯标签。
        </p>
        <input
          className={input}
          placeholder="小红书帖子链接"
          value={sourceUrl}
          onChange={(e) => setSourceUrl(e.target.value)}
        />
        <textarea
          className={`${input} h-40`}
          placeholder="帖子正文（留空则尝试从链接自动抓取）"
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
        />
        <button
          onClick={() => ingest.mutate()}
          disabled={(!rawText && !sourceUrl) || ingest.isPending}
          className="px-4 py-2 rounded bg-nest text-white hover:bg-nest-dark disabled:opacity-50"
        >
          {ingest.isPending ? "抓取 / AI 处理中…" : "抓取并 AI 生成草稿"}
        </button>
        {ingest.isError && (
          <p className="text-sm text-red-500">
            抓取失败（小红书可能要求登录）。请手动粘贴正文后重试。
          </p>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="font-semibold">待审核队列（{queue.data?.length ?? 0}）</h2>
        {queue.data?.map((l) => (
          <div key={l.id} className="bg-white border rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-medium">{l.title ?? "未命名"}</span>
              <button
                onClick={() => publish.mutate(l.id)}
                className="text-sm px-3 py-1 rounded bg-nest text-white hover:bg-nest-dark"
              >
                发布
              </button>
            </div>
            <div className="text-xs text-gray-500 flex flex-wrap gap-2">
              <span>{l.intent === "offering" ? "招租" : "求租"}</span>
              {l.area && <span>{l.area}</span>}
              {(l.budget_min || l.budget_max) && (
                <span>
                  ${l.budget_min ?? "?"}–{l.budget_max ?? "?"}
                </span>
              )}
              {l.mbti && <span>{l.mbti}</span>}
              {l.contact_value && (
                <span>
                  {l.contact_type}: {l.contact_value}
                </span>
              )}
            </div>
            {l.highlights && l.highlights.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {l.highlights.map((h) => (
                  <span key={h} className="text-xs px-2 py-0.5 rounded-full bg-nest/10 text-nest">
                    {h}
                  </span>
                ))}
              </div>
            )}
            <p className="text-sm text-gray-600 line-clamp-2">{l.raw_text}</p>
          </div>
        ))}
        {queue.data?.length === 0 && <p className="text-gray-400 text-sm">队列为空</p>}
      </section>

      <section className="space-y-3">
        <h2 className="font-semibold">失效/待复核房源（{stale.data?.length ?? 0}）</h2>
        {stale.data?.map((l) => (
          <div
            key={l.id}
            className="bg-white border rounded-lg p-4 flex items-center justify-between"
          >
            <div>
              <span className="font-medium">{l.title ?? `#${l.id}`}</span>
              <span className="ml-2 text-xs text-amber-600">{l.check_state}</span>
            </div>
            <button
              onClick={() => recheck.mutate(l.id)}
              className="text-sm text-nest hover:underline"
            >
              重新检查
            </button>
          </div>
        ))}
        {stale.data?.length === 0 && <p className="text-gray-400 text-sm">暂无</p>}
      </section>
    </div>
  );
}
