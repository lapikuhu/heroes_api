import type {
  Hero,
  HeroCreatePayload,
  HeroUpdatePayload,
  Mission,
  MissionPayload,
  User,
  UserPayload,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type RequestOptions = RequestInit & {
  token?: string | null;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = `Request failed with ${response.status}`;
    try {
      const error = await response.json();
      detail = error.detail ?? detail;
    } catch {
      // Keep the status-based fallback.
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password });
  return request<{ access_token: string; token_type: string }>("/users/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
}

export const api = {
  me: (token: string) => request<User>("/users/me", { token }),
  listUsers: (token: string) => request<User[]>("/users/", { token }),
  createUser: (token: string, payload: UserPayload) =>
    request<{ ok: boolean; user: User }>("/users/register", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    }),
  updateUser: (token: string, id: number, payload: UserPayload) =>
    request<User>(`/users/${id}`, {
      method: "PATCH",
      token,
      body: JSON.stringify(payload),
    }),
  deleteUser: (token: string, id: number) =>
    request<void>(`/users/${id}`, {
      method: "DELETE",
      token,
    }),
  listHeroes: () => request<Hero[]>("/heroes/"),
  createHero: (token: string, payload: HeroCreatePayload) =>
    request<Hero>("/heroes/", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    }),
  updateHero: (token: string, id: number, payload: HeroUpdatePayload) =>
    request<Hero>(`/heroes/${id}`, {
      method: "PATCH",
      token,
      body: JSON.stringify(payload),
    }),
  deleteHero: (token: string, id: number) =>
    request<void>(`/heroes/${id}`, {
      method: "DELETE",
      token,
    }),
  listMissions: () => request<Mission[]>("/missions/"),
  createMission: (token: string, payload: MissionPayload) =>
    request<Mission>("/missions/", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    }),
  updateMission: (token: string, id: number, payload: Partial<MissionPayload>) =>
    request<Mission>(`/missions/${id}`, {
      method: "PATCH",
      token,
      body: JSON.stringify(payload),
    }),
  deleteMission: (token: string, id: number) =>
    request<void>(`/missions/${id}`, {
      method: "DELETE",
      token,
    }),
};
