import {
  CheckCircle2,
  Gauge,
  LogOut,
  Menu,
  Shield,
  Sparkles,
  Swords,
  Users,
  X,
} from "lucide-react";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { FormEvent, ReactNode } from "react";
import { NavLink, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { api, login as loginRequest } from "./api";
import type { Hero, Mission, User } from "./types";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const tokenKey = "heroes_api_token";
const roleOptions = ["admin", "editor", "viewer"];

function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return value;
}

function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(tokenKey));
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(Boolean(token));

  async function refreshUser() {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const currentUser = await api.me(token);
      setUser(currentUser);
    } catch {
      localStorage.removeItem(tokenKey);
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshUser();
  }, [token]);

  async function login(username: string, password: string) {
    const response = await loginRequest(username, password);
    localStorage.setItem(tokenKey, response.access_token);
    setToken(response.access_token);
  }

  function logout() {
    localStorage.removeItem(tokenKey);
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({ token, user, loading, login, logout, refreshUser }),
    [token, user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { token, loading } = useAuth();

  if (loading) {
    return <FullPageStatus label="Loading your console..." />;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function LoginPage() {
  const { token, login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(username, password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-copy">
        <div className="brand-mark">
          <Sparkles size={22} />
          <span>Heroes Console</span>
        </div>
        <h1>Command the roster with clarity.</h1>
        <p>
          Manage heroes, missions, and users from a bright workspace tuned for fast,
          confident admin work.
        </p>
        <div className="login-art" aria-hidden="true">
          <div className="art-tile teal" />
          <div className="art-tile yellow" />
          <div className="art-tile blue" />
          <Swords size={78} />
        </div>
      </section>
      <section className="login-panel" aria-label="Login form">
        <h2>Log in</h2>
        <form onSubmit={handleSubmit} className="stack">
          <label>
            Username
            <input
              value={username}
              minLength={3}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              minLength={3}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}

function AppShell() {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: Gauge, adminOnly: false },
    { to: "/heroes", label: "Heroes", icon: Swords, adminOnly: false },
    { to: "/missions", label: "Missions", icon: CheckCircle2, adminOnly: false },
    { to: "/users", label: "Users", icon: Users, adminOnly: true },
  ].filter((item) => !item.adminOnly || user?.is_admin);

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <div className="brand-mark compact">
            <Sparkles size={20} />
            <span>Heroes</span>
          </div>
          <button className="icon-button mobile-only" onClick={() => setSidebarOpen(false)} aria-label="Close sidebar">
            <X size={18} />
          </button>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="shell-main">
        <header className="topbar">
          <button className="icon-button mobile-only" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar">
            <Menu size={20} />
          </button>
          <div>
            <p className="eyebrow">Signed in</p>
            <strong>{user?.username}</strong>
          </div>
          <div className="topbar-actions">
            {user?.is_admin && (
              <span className="badge">
                <Shield size={14} />
                Admin
              </span>
            )}
            <button className="ghost-button" onClick={logout}>
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </header>
        <main className="content">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/heroes" element={<HeroesPage />} />
            <Route path="/missions" element={<MissionsPage />} />
            <Route path="/users" element={user?.is_admin ? <UsersPage /> : <Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function Dashboard() {
  const { token, user } = useAuth();
  const [heroes, setHeroes] = useState<Hero[]>([]);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    void Promise.all([
      api.listHeroes().then(setHeroes),
      api.listMissions().then(setMissions),
      user?.is_admin && token ? api.listUsers(token).then(setUsers) : Promise.resolve(),
    ]);
  }, [token, user?.is_admin]);

  const completed = missions.filter((mission) => mission.completed).length;

  return (
    <Page title="Dashboard" subtitle="A quick read on the people and work in motion.">
      <div className="metrics-grid">
        <Metric label="Heroes" value={heroes.length} />
        <Metric label="Missions" value={missions.length} />
        <Metric label="Completed" value={completed} />
        <Metric label={user?.is_admin ? "Users" : "Role"} value={user?.is_admin ? users.length : "Member"} />
      </div>
      <section className="panel">
        <h2>Mission pulse</h2>
        <div className="progress-row">
          <div className="progress-track">
            <span style={{ width: `${missions.length ? (completed / missions.length) * 100 : 0}%` }} />
          </div>
          <strong>
            {completed}/{missions.length} complete
          </strong>
        </div>
      </section>
    </Page>
  );
}

function HeroesPage() {
  const { token, user } = useAuth();
  const [heroes, setHeroes] = useState<Hero[]>([]);
  const [form, setForm] = useState({ name: "", power: "", age: "" });
  const [editing, setEditing] = useState<Record<number, { name: string; age: string }>>({});
  const [error, setError] = useState("");

  async function loadHeroes() {
    setHeroes(await api.listHeroes());
  }

  useEffect(() => {
    void loadHeroes();
  }, []);

  async function createHero(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setError("");
    try {
      await api.createHero(token, {
        name: form.name,
        power: form.power,
        age: form.age ? Number(form.age) : null,
      });
      setForm({ name: "", power: "", age: "" });
      await loadHeroes();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create hero");
    }
  }

  async function updateHero(hero: Hero) {
    if (!token) return;
    const next = editing[hero.id];
    await api.updateHero(token, hero.id, {
      name: next.name,
      age: next.age ? Number(next.age) : null,
    });
    await loadHeroes();
  }

  async function deleteHero(id: number) {
    if (!token) return;
    await api.deleteHero(token, id);
    await loadHeroes();
  }

  return (
    <Page title="Heroes" subtitle="Create and maintain the roster.">
      <form className="panel form-grid" onSubmit={createHero}>
        <input placeholder="Hero name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required minLength={3} />
        <input placeholder="Power" value={form.power} onChange={(event) => setForm({ ...form, power: event.target.value })} required minLength={3} />
        <input placeholder="Age" type="number" value={form.age} onChange={(event) => setForm({ ...form, age: event.target.value })} />
        <button className="primary-button" type="submit">Create hero</button>
        {error && <p className="form-error wide">{error}</p>}
      </form>
      <div className="resource-grid">
        {heroes.map((hero) => {
          const draft = editing[hero.id] ?? { name: hero.name, age: hero.age?.toString() ?? "" };
          return (
            <article className="resource-card" key={hero.id}>
              <div>
                <p className="eyebrow">#{hero.id}</p>
                <h2>{hero.name}</h2>
                <p>{hero.power}</p>
              </div>
              <div className="inline-fields">
                <input value={draft.name} onChange={(event) => setEditing({ ...editing, [hero.id]: { ...draft, name: event.target.value } })} />
                <input type="number" placeholder="Age" value={draft.age} onChange={(event) => setEditing({ ...editing, [hero.id]: { ...draft, age: event.target.value } })} />
              </div>
              <p className="muted">Missions: {hero.mission_ids.length ? hero.mission_ids.join(", ") : "None"}</p>
              <div className="card-actions">
                <button className="outline-button" onClick={() => updateHero(hero)}>Save</button>
                {user?.is_admin && <button className="danger-button" onClick={() => deleteHero(hero.id)}>Delete</button>}
              </div>
            </article>
          );
        })}
      </div>
    </Page>
  );
}

function MissionsPage() {
  const { token, user } = useAuth();
  const [heroes, setHeroes] = useState<Hero[]>([]);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [form, setForm] = useState({ name: "", difficulty: "5", hero_id: "", completed: false });
  const [error, setError] = useState("");

  async function loadData() {
    const [nextHeroes, nextMissions] = await Promise.all([api.listHeroes(), api.listMissions()]);
    setHeroes(nextHeroes);
    setMissions(nextMissions);
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function createMission(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setError("");
    try {
      await api.createMission(token, {
        name: form.name,
        difficulty: Number(form.difficulty),
        completed: form.completed,
        hero_id: form.hero_id ? Number(form.hero_id) : null,
      });
      setForm({ name: "", difficulty: "5", hero_id: "", completed: false });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create mission");
    }
  }

  async function patchMission(id: number, payload: Partial<Mission>) {
    if (!token) return;
    await api.updateMission(token, id, payload);
    await loadData();
  }

  async function deleteMission(id: number) {
    if (!token) return;
    await api.deleteMission(token, id);
    await loadData();
  }

  return (
    <Page title="Missions" subtitle="Assign work, tune difficulty, and track completion.">
      <form className="panel form-grid" onSubmit={createMission}>
        <input placeholder="Mission name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required minLength={5} />
        <input type="number" min={1} max={10} value={form.difficulty} onChange={(event) => setForm({ ...form, difficulty: event.target.value })} />
        <select value={form.hero_id} onChange={(event) => setForm({ ...form, hero_id: event.target.value })}>
          <option value="">Unassigned</option>
          {heroes.map((hero) => <option key={hero.id} value={hero.id}>{hero.name}</option>)}
        </select>
        <label className="check-label">
          <input type="checkbox" checked={form.completed} onChange={(event) => setForm({ ...form, completed: event.target.checked })} />
          Complete
        </label>
        <button className="primary-button" type="submit">Create mission</button>
        {error && <p className="form-error wide">{error}</p>}
      </form>
      <div className="table-panel">
        {missions.map((mission) => (
          <div className="table-row" key={mission.id}>
            <div>
              <strong>{mission.name}</strong>
              <p className="muted">Difficulty {mission.difficulty} · Hero {mission.hero_id ?? "unassigned"}</p>
            </div>
            <label className="check-label">
              <input
                type="checkbox"
                checked={mission.completed}
                onChange={(event) => patchMission(mission.id, { completed: event.target.checked })}
              />
              Complete
            </label>
            <select value={mission.hero_id ?? ""} onChange={(event) => patchMission(mission.id, { hero_id: event.target.value ? Number(event.target.value) : null })}>
              <option value="">Unassigned</option>
              {heroes.map((hero) => <option key={hero.id} value={hero.id}>{hero.name}</option>)}
            </select>
            {user?.is_admin && <button className="danger-button" onClick={() => deleteMission(mission.id)}>Delete</button>}
          </div>
        ))}
      </div>
    </Page>
  );
}

function UsersPage() {
  const { token, user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [form, setForm] = useState({ username: "", password: "", is_admin: false, roles: ["viewer"] });
  const [editing, setEditing] = useState<Record<number, { username: string; password: string; is_admin: boolean; role: string }>>({});
  const [error, setError] = useState("");

  async function loadUsers() {
    if (!token) return;
    setUsers(await api.listUsers(token));
  }

  useEffect(() => {
    void loadUsers();
  }, [token]);

  async function createUser(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setError("");
    try {
      await api.createUser(token, form);
      setForm({ username: "", password: "", is_admin: false, roles: ["viewer"] });
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create user");
    }
  }

  async function deleteUser(id: number) {
    if (!token || id === user?.id) return;
    await api.deleteUser(token, id);
    await loadUsers();
  }

  async function updateUser(account: User) {
    if (!token) return;
    const draft = editing[account.id];
    if (!draft?.password) {
      setError("Password is required when updating a user.");
      return;
    }
    setError("");
    await api.updateUser(token, account.id, {
      username: draft.username,
      password: draft.password,
      is_admin: draft.is_admin,
      roles: [draft.role],
    });
    setEditing({ ...editing, [account.id]: { ...draft, password: "" } });
    await loadUsers();
  }

  return (
    <Page title="Users" subtitle="Admin-only account creation and cleanup.">
      <form className="panel form-grid" onSubmit={createUser}>
        <input placeholder="Username" value={form.username} minLength={3} onChange={(event) => setForm({ ...form, username: event.target.value })} required />
        <input placeholder="Password" type="password" value={form.password} minLength={3} onChange={(event) => setForm({ ...form, password: event.target.value })} required />
        <label className="check-label">
          <input type="checkbox" checked={form.is_admin} onChange={(event) => setForm({ ...form, is_admin: event.target.checked })} />
          Admin
        </label>
        <select value={form.roles[0] ?? "viewer"} onChange={(event) => setForm({ ...form, roles: [event.target.value] })}>
          {roleOptions.map((role) => <option key={role} value={role}>{role}</option>)}
        </select>
        <button className="primary-button" type="submit">Create user</button>
        {error && <p className="form-error wide">{error}</p>}
      </form>
      <div className="table-panel">
        {users.map((account) => {
          const draft = editing[account.id] ?? {
            username: account.username,
            password: "",
            is_admin: account.is_admin,
            role: account.roles[0] ?? "viewer",
          };

          return (
            <div className="table-row user-row" key={account.id}>
              <div>
                <strong>{account.username}</strong>
                <p className="muted">{account.roles.length ? account.roles.join(", ") : "No roles"}</p>
              </div>
              <input
                value={draft.username}
                onChange={(event) => setEditing({ ...editing, [account.id]: { ...draft, username: event.target.value } })}
              />
              <input
                type="password"
                placeholder="New password"
                value={draft.password}
                onChange={(event) => setEditing({ ...editing, [account.id]: { ...draft, password: event.target.value } })}
              />
              <select value={draft.role} onChange={(event) => setEditing({ ...editing, [account.id]: { ...draft, role: event.target.value } })}>
                {roleOptions.map((role) => <option key={role} value={role}>{role}</option>)}
              </select>
              <label className="check-label">
                <input
                  type="checkbox"
                  checked={draft.is_admin}
                  onChange={(event) => setEditing({ ...editing, [account.id]: { ...draft, is_admin: event.target.checked } })}
                />
                Admin
              </label>
              <button className="outline-button" onClick={() => updateUser(account)}>Save</button>
              <button className="danger-button" disabled={account.id === user?.id} onClick={() => deleteUser(account.id)}>
                Delete
              </button>
            </div>
          );
        })}
      </div>
    </Page>
  );
}

function Page({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Heroes API</p>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
      </header>
      {children}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: number | string }) {
  return (
    <article className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}

function FullPageStatus({ label }: { label: string }) {
  return (
    <main className="status-page">
      <Sparkles size={24} />
      <p>{label}</p>
    </main>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<ProtectedRoute><AppShell /></ProtectedRoute>} />
      </Routes>
    </AuthProvider>
  );
}
