export type User = {
  id: number;
  username: string;
  is_admin: boolean;
  roles: string[];
};

export type Hero = {
  id: number;
  name: string;
  power: string;
  age: number | null;
  mission_ids: number[];
};

export type Mission = {
  id: number;
  name: string;
  difficulty: number;
  completed: boolean;
  hero_id: number | null;
};

export type UserPayload = {
  username: string;
  password: string;
  is_admin: boolean;
  roles: string[];
};

export type HeroCreatePayload = {
  name: string;
  power: string;
  age: number | null;
};

export type HeroUpdatePayload = {
  name?: string;
  power?: string;
  age?: number | null;
};

export type MissionPayload = {
  name: string;
  difficulty: number;
  completed: boolean;
  hero_id: number | null;
};
