import { apiClient } from '@/lib/api-client';
import { HealthResponse, DatabaseHealthResponse } from '@/types/api';

export const healthService = {
  checkAppHealth: async (): Promise<HealthResponse> => {
    return apiClient.get<HealthResponse>('/health');
  },

  checkDatabaseHealth: async (): Promise<DatabaseHealthResponse> => {
    return apiClient.get<DatabaseHealthResponse>('/health/database');
  },
};
