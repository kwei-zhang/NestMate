import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAddFavorite, useContact } from "../api/hooks";
import { useAuth } from "../store/auth";

export default function ContactGate({ listingId }: { listingId: number }) {
  const { isAuthed } = useAuth();
  const navigate = useNavigate();
  const [reveal, setReveal] = useState(false);
  const { data, isLoading } = useContact(listingId, isAuthed && reveal);
  const addFavorite = useAddFavorite();

  if (!isAuthed) {
    return (
      <div className="bg-gray-50 border rounded-lg p-4 text-center">
        <p className="text-sm text-gray-500 mb-2">联系方式仅对登录用户可见</p>
        <button
          onClick={() => navigate("/login")}
          className="px-4 py-2 rounded bg-nest text-white hover:bg-nest-dark"
        >
          登录后查看联系方式
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 border rounded-lg p-4">
      {!reveal ? (
        <button
          onClick={() => setReveal(true)}
          className="px-4 py-2 rounded bg-nest text-white hover:bg-nest-dark"
        >
          查看联系方式
        </button>
      ) : isLoading ? (
        <span className="text-gray-400 text-sm">加载中…</span>
      ) : data?.contact_value ? (
        <div className="flex items-center justify-between gap-3">
          <div>
            <span className="text-xs text-gray-400 mr-2">{data.contact_type}</span>
            <span className="font-medium select-all">{data.contact_value}</span>
          </div>
          <button
            onClick={() => addFavorite.mutate(listingId)}
            className="text-sm text-nest hover:underline"
          >
            收藏
          </button>
        </div>
      ) : (
        <span className="text-gray-400 text-sm">暂无联系方式</span>
      )}
    </div>
  );
}
