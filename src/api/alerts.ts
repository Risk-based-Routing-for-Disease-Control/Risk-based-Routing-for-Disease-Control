const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

export interface OutbreakCase {
  farmId: string | null;
  farmName: string | null;
  disease: string | null;
  region: string | null;
  confirmedAt: string | null;
  isTest: boolean;
}

export interface OutbreakAlertsResponse {
  ok: boolean;
  date: string;
  count: number;
  cases: OutbreakCase[];
}

export async function fetchOutbreakAlerts(): Promise<OutbreakAlertsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/alerts/outbreaks`);
  if (!response.ok) throw new Error(`outbreak alerts fetch failed: ${response.status}`);
  return (await response.json()) as OutbreakAlertsResponse;
}
