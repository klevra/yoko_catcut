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
  const [registerMode, setRegisterMode] = useState(false);
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

  const register = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const result = await api.register(userId, password);
      setMessage(
        `${result.user_id} 계정을 생성했습니다. 로그인 승인을 위해 ${result.lock_file} 파일을 삭제해주세요.`
      );
      setRegisterMode(false);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Register failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-shell">
      <section className="login-panel">
        <h1>{registerMode ? "Yoko CatCut Register" : "Yoko CatCut Login"}</h1>
        <p>
          {registerMode
            ? "계정 생성 후 lock.lck 파일 삭제 승인이 필요합니다."
            : "파일 기반 계정으로 로그인합니다."}
        </p>
        <form onSubmit={registerMode ? register : login}>
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
            {loading
              ? registerMode
                ? "Registering..."
                : "Logging in..."
              : registerMode
                ? "계정 생성"
                : "Login"}
          </button>
        </form>
        <button
          className="btn-secondary login-switch"
          onClick={() => {
            setRegisterMode((current) => !current);
            setMessage("");
            if (!registerMode) {
              setUserId("");
              setPassword("");
            } else {
              setUserId("default-user");
              setPassword("yoko1234");
            }
          }}
          disabled={loading}
        >
          {registerMode ? "로그인으로 돌아가기" : "계정 등록"}
        </button>
        {message && <p className="editor-error">{message}</p>}
        <p className="login-note">
          기본 계정은 <code>default-user</code>, 기본 비밀번호는{" "}
          <code>yoko1234</code>입니다. 새 계정은 계정 폴더의{" "}
          <code>lock.lck</code> 파일을 삭제해야 로그인됩니다.
        </p>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
