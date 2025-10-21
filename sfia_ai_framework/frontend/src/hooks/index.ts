import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiService } from '../services/api';
import type {
  EmployeeAnalysisRequest,
  EmployeeAnalysisResponse,
  DepartmentAnalysisRequest,
  DepartmentAnalysisResponse,
  OrganizationInsightsResponse,
  EnterpriseInitRequest,
  EnterpriseSystem,
  HealthStatus,
} from '../services/api';
import toast from 'react-hot-toast';

// Health check hook
export const useHealthCheck = () => {
  return useQuery<HealthStatus[]>('health', async () => {
    const response = await apiService.healthCheck();
    if (!response.success) {
      throw new Error(response.error || 'Health check failed');
    }
    return response.data || [];
  }, {
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 3,
  });
};

// Employee analysis hooks
export const useEmployeeAnalysis = () => {
  const queryClient = useQueryClient();
  
  return useMutation<EmployeeAnalysisResponse, Error, EmployeeAnalysisRequest>(
    async (request) => {
      const response = await apiService.analyzeEmployee(request);
      if (!response.success) {
        throw new Error(response.error || 'Employee analysis failed');
      }
      return response.data!;
    },
    {
      onSuccess: (data) => {
        toast.success(`Analysis completed for employee ${data.employee_id}`);
        queryClient.invalidateQueries('employeeAnalyses');
      },
      onError: (error) => {
        toast.error(`Analysis failed: ${error.message}`);
      },
    }
  );
};

// Department analysis hooks
export const useDepartmentAnalysis = () => {
  const queryClient = useQueryClient();
  
  return useMutation<DepartmentAnalysisResponse, Error, DepartmentAnalysisRequest>(
    async (request) => {
      const response = await apiService.analyzeDepartment(request);
      if (!response.success) {
        throw new Error(response.error || 'Department analysis failed');
      }
      return response.data!;
    },
    {
      onSuccess: (data) => {
        toast.success(`Analysis completed for ${data.department} department`);
        queryClient.invalidateQueries('departmentAnalyses');
      },
      onError: (error) => {
        toast.error(`Analysis failed: ${error.message}`);
      },
    }
  );
};

// Organization insights hook
export const useOrganizationInsights = (timeRange?: string) => {
  return useQuery<OrganizationInsightsResponse>(
    ['organizationInsights', timeRange],
    async () => {
      const response = await apiService.getOrganizationInsights(timeRange);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch organization insights');
      }
      return response.data!;
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
    }
  );
};

// Enterprise integration hooks
export const useEnterpriseStatus = () => {
  return useQuery<{ initialized: boolean; systems: EnterpriseSystem[] }>(
    'enterpriseStatus',
    async () => {
      const response = await apiService.getEnterpriseStatus();
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch enterprise status');
      }
      return response.data!;
    },
    {
      refetchInterval: 10000, // Refetch every 10 seconds
      retry: 2,
    }
  );
};

export const useInitializeEnterprise = () => {
  const queryClient = useQueryClient();
  
  return useMutation<any, Error, EnterpriseInitRequest>(
    async (request) => {
      const response = await apiService.initializeEnterprise(request);
      if (!response.success) {
        throw new Error(response.error || 'Enterprise initialization failed');
      }
      return response.data;
    },
    {
      onSuccess: () => {
        toast.success('Enterprise integration initialized successfully');
        queryClient.invalidateQueries('enterpriseStatus');
      },
      onError: (error) => {
        toast.error(`Initialization failed: ${error.message}`);
      },
    }
  );
};

export const useConnectEnterpriseSystem = () => {
  const queryClient = useQueryClient();
  
  return useMutation<any, Error, Omit<EnterpriseSystem, 'status' | 'last_sync'>>(
    async (system) => {
      const response = await apiService.connectEnterpriseSystem(system);
      if (!response.success) {
        throw new Error(response.error || 'System connection failed');
      }
      return response.data;
    },
    {
      onSuccess: (_, variables) => {
        toast.success(`Connected to ${variables.name} successfully`);
        queryClient.invalidateQueries('enterpriseStatus');
      },
      onError: (error) => {
        toast.error(`Connection failed: ${error.message}`);
      },
    }
  );
};

export const useDisconnectEnterpriseSystem = () => {
  const queryClient = useQueryClient();
  
  return useMutation<any, Error, string>(
    async (systemName) => {
      const response = await apiService.disconnectEnterpriseSystem(systemName);
      if (!response.success) {
        throw new Error(response.error || 'System disconnection failed');
      }
      return response.data;
    },
    {
      onSuccess: (_, systemName) => {
        toast.success(`Disconnected from ${systemName} successfully`);
        queryClient.invalidateQueries('enterpriseStatus');
      },
      onError: (error) => {
        toast.error(`Disconnection failed: ${error.message}`);
      },
    }
  );
};

export const useEnterpriseHealth = () => {
  return useQuery<HealthStatus[]>(
    'enterpriseHealth',
    async () => {
      const response = await apiService.getEnterpriseHealth();
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch enterprise health');
      }
      return response.data || [];
    },
    {
      refetchInterval: 15000, // Refetch every 15 seconds
      retry: 2,
    }
  );
};

// Scenario hooks
export const useRunScenario = () => {
  return useMutation<any, Error, { scenarioType: string; params: Record<string, any> }>(
    async ({ scenarioType, params }) => {
      const response = await apiService.runScenario(scenarioType, params);
      if (!response.success) {
        throw new Error(response.error || 'Scenario execution failed');
      }
      return response.data;
    },
    {
      onSuccess: (_, variables) => {
        toast.success(`Scenario "${variables.scenarioType}" completed successfully`);
      },
      onError: (error) => {
        toast.error(`Scenario failed: ${error.message}`);
      },
    }
  );
};

// Multi-agent AI hooks
export const useAgentStatus = () => {
  return useQuery<Array<{
    name: string;
    status: 'ready' | 'busy' | 'error';
    specialization: string;
  }>>(
    'agentStatus',
    async () => {
      const response = await apiService.getAgentStatus();
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch agent status');
      }
      return response.data || [];
    },
    {
      refetchInterval: 5000, // Refetch every 5 seconds
      retry: 2,
    }
  );
};

export const useExecuteAgentTask = () => {
  const queryClient = useQueryClient();
  
  return useMutation<any, Error, { agentName: string; task: string; params?: Record<string, any> }>(
    async ({ agentName, task, params }) => {
      const response = await apiService.executeAgentTask(agentName, task, params);
      if (!response.success) {
        throw new Error(response.error || 'Agent task execution failed');
      }
      return response.data;
    },
    {
      onSuccess: (_, variables) => {
        toast.success(`Task executed by ${variables.agentName} successfully`);
        queryClient.invalidateQueries('agentStatus');
      },
      onError: (error) => {
        toast.error(`Task execution failed: ${error.message}`);
      },
    }
  );
};

// Knowledge graph hooks
export const useKnowledgeGraphData = (nodeType?: string, depth?: number) => {
  return useQuery(
    ['knowledgeGraph', nodeType, depth],
    async () => {
      const response = await apiService.getKnowledgeGraphData(nodeType, depth);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch knowledge graph data');
      }
      return response.data;
    },
    {
      enabled: !!nodeType || depth !== undefined,
      staleTime: 10 * 60 * 1000, // 10 minutes
      retry: 2,
    }
  );
};

export const useSearchKnowledgeGraph = () => {
  return useMutation<any, Error, string>(
    async (query) => {
      const response = await apiService.searchKnowledgeGraph(query);
      if (!response.success) {
        throw new Error(response.error || 'Knowledge graph search failed');
      }
      return response.data;
    },
    {
      onError: (error) => {
        toast.error(`Search failed: ${error.message}`);
      },
    }
  );
};

// Analytics hooks
export const useAnalytics = (type: string, params?: Record<string, any>) => {
  return useQuery(
    ['analytics', type, params],
    async () => {
      const response = await apiService.getAnalytics(type, params);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch analytics');
      }
      return response.data;
    },
    {
      enabled: !!type,
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
    }
  );
};

// Reports hooks
export const useGenerateReport = () => {
  return useMutation<{ reportId: string }, Error, { reportType: string; params: Record<string, any> }>(
    async ({ reportType, params }) => {
      const response = await apiService.generateReport(reportType, params);
      if (!response.success) {
        throw new Error(response.error || 'Report generation failed');
      }
      return response.data!;
    },
    {
      onSuccess: () => {
        toast.success('Report generation started');
      },
      onError: (error) => {
        toast.error(`Report generation failed: ${error.message}`);
      },
    }
  );
};

export const useReportStatus = (reportId?: string) => {
  return useQuery(
    ['reportStatus', reportId],
    async () => {
      const response = await apiService.getReportStatus(reportId!);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch report status');
      }
      return response.data!;
    },
    {
      enabled: !!reportId,
      refetchInterval: (data) => {
        // Stop polling when report is ready or failed
        return data?.status === 'completed' || data?.status === 'failed' ? false : 2000;
      },
      retry: 2,
    }
  );
};

// Settings hooks
export const useSettings = () => {
  return useQuery<Record<string, any>>(
    'settings',
    async () => {
      const response = await apiService.getSettings();
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch settings');
      }
      return response.data || {};
    },
    {
      staleTime: 30 * 60 * 1000, // 30 minutes
      retry: 2,
    }
  );
};

export const useUpdateSettings = () => {
  const queryClient = useQueryClient();
  
  return useMutation<any, Error, Record<string, any>>(
    async (settings) => {
      const response = await apiService.updateSettings(settings);
      if (!response.success) {
        throw new Error(response.error || 'Settings update failed');
      }
      return response.data;
    },
    {
      onSuccess: () => {
        toast.success('Settings updated successfully');
        queryClient.invalidateQueries('settings');
      },
      onError: (error) => {
        toast.error(`Settings update failed: ${error.message}`);
      },
    }
  );
};

// Custom hook for WebSocket connection
export const useWebSocket = (onMessage: (data: any) => void) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const ws = apiService.createWebSocketConnection(onMessage);
    if (ws) {
      setSocket(ws);
    }

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [onMessage]);

  return socket;
};

// Utility hook for local storage state
export const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue] as const;
};