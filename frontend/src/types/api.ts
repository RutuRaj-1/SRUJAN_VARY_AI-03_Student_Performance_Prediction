export interface SubsystemStatus {
  api: string;
  database: 'connected' | 'unconfigured' | 'disconnected';
  ai_engine: 'configured' | 'unconfigured';
  supabase_auth: 'configured' | 'unconfigured';
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  app_name: string;
  environment: string;
  version: string;
  timestamp: string;
  services: SubsystemStatus;
}

export interface DatabaseHealthResponse {
  status: 'connected' | 'unconfigured' | 'disconnected';
  configured: boolean;
  message: string;
  latency_ms: number | null;
  timestamp: string;
}

export interface RootInfoResponse {
  app: string;
  tagline: string;
  description: string;
  version: string;
  api_v1_docs: string;
  api_v1_health: string;
  api_v1_db_health: string;
}

export interface ApiError {
  status: 'error';
  error_type: string;
  detail: string | Record<string, unknown>[];
  status_code: number;
  path?: string;
}
