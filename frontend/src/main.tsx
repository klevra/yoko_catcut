import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import Dashboard from "./pages/Dashboard";
import VideoEditor from "./pages/VideoEditor";
import AppFooter from "./components/AppFooter";
import { api, AuthSession, getAuthSession, setAuthSession } from "./api/client";
import "./style.css";

function App() {
  const [location, setLocation] = useState(window.location.href);
  const [session, setSession] = useState<AuthSession | null>(getAuthSession());

  useEffect(() => {
    const handleNavigation = () => setLocation(window.location.href);
    window.addEventListener("popstate", handleNavigation);
    return () => window.removeEventListener("popstate", handleNavigation);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, "", path);
    setLocation(window.location.href);
  };

  const url = new URL(location);
  const uploadId = url.searchParams.get("uploadId");

  const handleLogout = () => {
    setAuthSession(null);
    setSession(null);
    navigate("/");
  };

  if (!session) {
    return (
      <>
        <LoginPage onLogin={setSession} />
        <AppFooter />
      </>
    );
  }

  if (url.pathname === "/editor" && uploadId) {
    return (
      <>
        <VideoEditor uploadId={uploadId} onBack={() => navigate("/")} />
        <AppFooter />
      </>
    );
  }

  return (
    <>
      <Dashboard
        userId={session.user_id}
        usersFile={session.users_file}
        onLogout={handleLogout}
        onEditUpload={(id) =>
          navigate(`/editor?uploadId=${encodeURIComponent(id)}`)
        }
      />
      <AppFooter />
    </>
  );
}

function LoginPage({ onLogin }: { onLogin: (session: AuthSession) => void }) {
  const [userId, setUserId] = useState("default-user");
  const [password, setPassword] = useState("yoko1234");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const login = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const session = await api.login(userId, password);
      setAuthSession(session);
      onLogin(session);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-shell">
      <section className="login-panel">
        <h1>Yoko CatCut Login</h1>
        <p>파일 기반 계정으로 로그인합니다.</p>
        <form onSubmit={login}>
          <label>
            Account
            <input
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        {message && <p className="editor-error">{message}</p>}
        <p className="login-note">
          기본 계정은 <code>default-user</code>, 기본 비밀번호는{" "}
          <code>yoko1234</code>입니다. 계정 파일에서 비밀번호를 변경하세요.
        </p>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
