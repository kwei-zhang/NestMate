import { Link, Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./store/auth";
import AdminIngest from "./pages/AdminIngest";
import AuthCallback from "./pages/AuthCallback";
import CreatePost from "./pages/CreatePost";
import Favorites from "./pages/Favorites";
import Home from "./pages/Home";
import ListingDetail from "./pages/ListingDetail";
import Login from "./pages/Login";

function NavBar() {
  const { isAuthed, isAdmin, user, logout } = useAuth();
  return (
    <header className="bg-white border-b">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center gap-4">
        <Link to="/" className="font-bold text-nest text-lg">
          NestMate
        </Link>
        <span className="text-xs text-gray-400 hidden sm:inline">多伦多华人找室友</span>
        <nav className="ml-auto flex items-center gap-4 text-sm">
          <Link to="/" className="hover:text-nest">
            房源
          </Link>
          {isAuthed && (
            <>
              <Link to="/favorites" className="hover:text-nest">
                收藏
              </Link>
              <Link to="/post/new" className="hover:text-nest">
                发帖
              </Link>
            </>
          )}
          {isAdmin && (
            <Link to="/admin" className="hover:text-nest">
              后台
            </Link>
          )}
          {isAuthed ? (
            <button onClick={logout} className="text-gray-500 hover:text-nest">
              退出{user?.display_name ? `（${user.display_name}）` : ""}
            </button>
          ) : (
            <Link to="/login" className="px-3 py-1 rounded bg-nest text-white hover:bg-nest-dark">
              登录
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

function RequireAuth({ children }: { children: JSX.Element }) {
  const { isAuthed, loading } = useAuth();
  if (loading) return <div className="p-8 text-center text-gray-400">加载中…</div>;
  return isAuthed ? children : <Navigate to="/login" replace />;
}

function RequireAdmin({ children }: { children: JSX.Element }) {
  const { isAdmin, loading } = useAuth();
  if (loading) return <div className="p-8 text-center text-gray-400">加载中…</div>;
  return isAdmin ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/listing/:id" element={<ListingDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route
            path="/favorites"
            element={
              <RequireAuth>
                <Favorites />
              </RequireAuth>
            }
          />
          <Route
            path="/post/new"
            element={
              <RequireAuth>
                <CreatePost />
              </RequireAuth>
            }
          />
          <Route
            path="/admin"
            element={
              <RequireAdmin>
                <AdminIngest />
              </RequireAdmin>
            }
          />
        </Routes>
      </main>
    </div>
  );
}
