export interface Listing {
  id: number;
  source: "xhs" | "native";
  source_url: string | null;
  title: string | null;
  raw_text: string;
  status: string;
  intent: "offering" | "seeking" | null;
  has_room: boolean | null;
  mbti: string | null;
  has_pets: boolean | null;
  pets_note: string | null;
  budget_min: number | null;
  budget_max: number | null;
  area: string | null;
  move_in_date: string | null;
  gender_pref: string | null;
  contact_type: string | null;
  created_at: string;
  published_at: string | null;
}

export interface Contact {
  contact_type: string | null;
  contact_value: string | null;
}

export interface User {
  id: number;
  provider: string;
  email: string | null;
  display_name: string | null;
  avatar_url: string | null;
  role: "user" | "admin";
  created_at: string;
}

export interface Favorite {
  listing_id: number;
  personal_status: "saved" | "contacted" | "closed";
  note: string | null;
  created_at: string;
}

export interface ListingFilters {
  area?: string;
  budget_min?: number;
  budget_max?: number;
  has_room?: boolean;
  has_pets?: boolean;
  mbti?: string;
  intent?: string;
  gender_pref?: string;
  q?: string;
  sort?: string;
}
