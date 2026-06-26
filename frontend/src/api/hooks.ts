import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./client";
import type { Contact, Favorite, Listing, ListingFilters, User } from "./types";

export function useListings(filters: ListingFilters) {
  return useQuery({
    queryKey: ["listings", filters],
    queryFn: async () => {
      const params = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== undefined && v !== ""),
      );
      const { data } = await api.get<Listing[]>("/listings", { params });
      return data;
    },
  });
}

export function useListing(id: number) {
  return useQuery({
    queryKey: ["listing", id],
    queryFn: async () => (await api.get<Listing>(`/listings/${id}`)).data,
  });
}

export function useContact(id: number, enabled: boolean) {
  return useQuery({
    queryKey: ["contact", id],
    enabled,
    queryFn: async () => (await api.get<Contact>(`/listings/${id}/contact`)).data,
  });
}

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    retry: false,
    queryFn: async () => (await api.get<User>("/auth/me")).data,
  });
}

export function useFavorites() {
  return useQuery({
    queryKey: ["favorites"],
    queryFn: async () => (await api.get<Favorite[]>("/favorites")).data,
  });
}

export function useAddFavorite() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (listingId: number) => api.post(`/favorites/${listingId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["favorites"] }),
  });
}

export function useUpdateFavorite() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { listingId: number; personal_status?: string; note?: string }) =>
      api.patch(`/favorites/${vars.listingId}`, {
        personal_status: vars.personal_status,
        note: vars.note,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["favorites"] }),
  });
}

export function useRemoveFavorite() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (listingId: number) => api.delete(`/favorites/${listingId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["favorites"] }),
  });
}

export function useCreatePost() {
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => api.post("/listings", body),
  });
}
