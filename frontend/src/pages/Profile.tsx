import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../store/auth";

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function onLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="max-w-md mx-auto space-y-4">
      <div className="bg-white border rounded-lg p-6 flex items-center gap-4">
        {user?.avatar_url ? (
          <img src={user.avatar_url} alt="" className="w-14 h-14 rounded-full object-cover" />
        ) : (
          <div className="w-14 h-14 rounded-full bg-nest/10 text-nest flex items-center justify-center text-xl">
            {(user?.display_name ?? "U").slice(0, 1)}
          </div>
        )}
        <div className="min-w-0">
          <p className="font-semibold truncate">{user?.display_name ?? "用户"}</p>
          {user?.email && <p className="text-sm text-gray-400 truncate">{user.email}</p>}
          {user?.role === "admin" && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-nest/10 text-nest">管理员</span>
          )}
        </div>
      </div>

      <div className="bg-white border rounded-lg divide-y">
        <Link to="/my" className="flex items-center justify-between px-4 py-3 hover:bg-gray-50">
          <span>我的发布</span>
          <span className="text-gray-300">›</span>
        </Link>
        <Link to="/favorites" className="flex items-center justify-between px-4 py-3 hover:bg-gray-50">
          <span>我的收藏</span>
          <span className="text-gray-300">›</span>
        </Link>
      </div>

      <button
        onClick={onLogout}
        className="w-full bg-white border rounded-lg px-4 py-3 text-red-500 hover:bg-red-50"
      >
        退出登录
      </button>
    </div>
  );
}
