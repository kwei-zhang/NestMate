import { Link, Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./store/auth";
import AdminIngest from "./pages/AdminIngest";
import AdminListings from "./pages/AdminListings";
import AuthCallback from "./pages/AuthCallback";
import CreatePost from "./pages/CreatePost";
import EditPost from "./pages/EditPost";
import Favorites from "./pages/Favorites";
import Home from "./pages/Home";
import ListingDetail from "./pages/ListingDetail";
import Login from "./pages/Login";
import MyPosts from "./pages/MyPosts";
import Profile from "./pages/Profile";

function NavBar() {
  const { isAuthed, isAdmin, user } = useAuth();
  return (
    <header className="bg-white border-b">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center gap-4">
        <Link to="/" className="font-bold text-nest text-lg">
          NestMate
        </Link>
        <span className="text-xs text-gray-400 hidden sm:inline">多伦多华人找室友</span>
        <nav className="ml-auto flex items-center gap-3 text-sm">
          <Link
            to="/"
            className="px-3 py-1 rounded border border-gray-200 hover:border-nest hover:text-nest"
          >
            房源
          </Link>
          {isAuthed && (
            <Link
              to="/favorites"
              className="px-3 py-1 rounded border border-gray-200 hover:border-nest hover:text-nest"
            >
              收藏
            </Link>
          )}
          {isAdmin && (
            <>
              <Link to="/admin" className="hover:text-nest">
                录入
              </Link>
              <Link to="/admin/all" className="hover:text-nest">
                全部帖子
              </Link>
            </>
          )}
          {isAuthed ? (
            <Link to="/profile" className="flex items-center gap-2 hover:text-nest">
              {user?.avatar_url ? (
                <img src={user.avatar_url} alt="" className="w-7 h-7 rounded-full object-cover" />
              ) : (
                <span className="w-7 h-7 rounded-full bg-nest/10 text-nest flex items-center justify-center text-xs">
                  {(user?.display_name ?? "U").slice(0, 1)}
                </span>
              )}
              <span className="hidden sm:inline">{user?.display_name ?? "我"}</span>
            </Link>
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

function PostFab() {
  const { isAuthed } = useAuth();
  if (!isAuthed) return null;
  return (
    <Link
      to="/post/new"
      title="发帖"
      aria-label="发帖"
      className="fixed bottom-6 right-6 z-20 w-14 h-14 rounded-full bg-nest text-white shadow-lg
        flex items-center justify-center text-3xl leading-none hover:bg-nest-dark"
    >
      +
    </Link>
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
          <Route
            path="/listing/:id/edit"
            element={
              <RequireAuth>
                <EditPost />
              </RequireAuth>
            }
          />
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
            path="/my"
            element={
              <RequireAuth>
                <MyPosts />
              </RequireAuth>
            }
          />
          <Route
            path="/profile"
            element={
              <RequireAuth>
                <Profile />
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
          <Route
            path="/admin/all"
            element={
              <RequireAdmin>
                <AdminListings />
              </RequireAdmin>
            }
          />
        </Routes>
      </main>
      <PostFab />
    </div>
  );
}
