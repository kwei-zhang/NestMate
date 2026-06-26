import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { consumeTokensFromHash, useAuth } from "../store/auth";

export default function AuthCallback() {
  const navigate = useNavigate();
  const { refresh } = useAuth();

  useEffect(() => {
    const ok = consumeTokensFromHash(window.location.hash);
    void (async () => {
      if (ok) await refresh();
      navigate("/", { replace: true });
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <div className="p-8 text-center text-gray-400">登录中…</div>;
}
