import type { DispatchDisinfectionHub } from '../types/dispatch';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

export async function fetchFacilities(): Promise<DispatchDisinfectionHub[]> {
  const res = await fetch(`${API_BASE_URL}/api/facilities`);
  if (!res.ok) throw new Error(`facilities fetch failed: ${res.status}`);
  return res.json() as Promise<DispatchDisinfectionHub[]>;
}
