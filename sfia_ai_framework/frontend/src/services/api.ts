import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  summary?: T;
  status?: string;
  guidance?: T;
  statistics?: T;
  skills?: T;
  skill?: T;
}

export interface EmployeeAnalysisRequest {
  employee_id: string;
  analysis_type?: 'standard' | 'deep' | 'real_time';
}

export interface EmployeeAnalysisResponse {
  employee_id: string;
  analysis_timestamp: string;
  suggestions: SFIASuggestion[];
}

export interface SFIASuggestion {
  skill_name: string;
  skill_code: string;
  current_level?: number;
  suggested_level: number;
  confidence_score: number;
  reasoning: string;
  supporting_evidence?: string[];
  improvement_areas?: string[];
  timeline_estimate?: string;
}

export interface DepartmentAnalysisRequest {
  department: string;
  include_contractors?: boolean;
}

export interface DepartmentAnalysisResponse {
  department: string;
  analysis_timestamp: string;
  employees: Record<string, SFIASuggestion[]>;
}

export interface OrganizationInsightsResponse {
  analysis_timestamp: string;
  total_employees: number;
  departments: Record<string, {
    employee_count: number;
    avg_level: number;
    skills: string[];
  }>;
  skill_distribution: Record<string, {
    employees: number;
    avg_level: number;
  }>;
  level_distribution: Record<number, number>;
  high_performers: Array<{
    employee_id: string;
    skill: string;
    level: number;
    confidence: number;
  }>;
  improvement_opportunities: Array<{
    skill: string;
    employees_needing: number;
    priority: 'High' | 'Medium' | 'Low';
  }>;
}

export interface EnterpriseSystem {
  name: string;
  type: 'postgresql' | 'mysql' | 'sap' | 'powerbi' | 'mongodb' | 'kafka' | 'oracle';
  status: 'Connected' | 'Disconnected' | 'Error';
  last_sync: string;
  config?: Record<string, any>;
}

export interface EnterpriseInitRequest {
  redis_url: string;
  systems: EnterpriseSystem[];
}

export interface HealthStatus {
  service: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  message?: string;
  last_check: string;
}

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        } else if (error.response?.status >= 500) {
          toast.error('Server error. Please try again later.');
        } else if (error.message === 'Network Error') {
          toast.error('Network error. Please check your connection.');
        }
        return Promise.reject(error);
      }
    );
  }

  private async request<T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.api.request<ApiResponse<T>>(config);
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.message || error.message || 'An error occurred';
      return {
        success: false,
        error: message,
      };
    }
  }

  // HTTP Methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({
      method: 'GET',
      url,
      ...config,
    });
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({
      method: 'POST',
      url,
      data,
      ...config,
    });
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({
      method: 'PUT',
      url,
      data,
      ...config,
    });
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({
      method: 'DELETE',
      url,
      ...config,
    });
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<HealthStatus[]>> {
    return this.request({
      method: 'GET',
      url: '/health',
    });
  }

  // Employee Analysis
  async analyzeEmployee(request: EmployeeAnalysisRequest): Promise<ApiResponse<EmployeeAnalysisResponse>> {
    return this.request({
      method: 'POST',
      url: '/api/analyze/employee',
      data: request,
    });
  }

  // Department Analysis
  async analyzeDepartment(request: DepartmentAnalysisRequest): Promise<ApiResponse<DepartmentAnalysisResponse>> {
    return this.request({
      method: 'POST',
      url: '/api/analyze/department',
      data: request,
    });
  }

  // Organization Insights
  async getOrganizationInsights(timeRange?: string): Promise<ApiResponse<OrganizationInsightsResponse>> {
    return this.request({
      method: 'GET',
      url: '/api/insights/organization',
      params: { time_range: timeRange },
    });
  }

  // Enterprise Integration
  async initializeEnterprise(request: EnterpriseInitRequest): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: '/api/enterprise/initialize',
      data: request,
    });
  }

  async getEnterpriseStatus(): Promise<ApiResponse<{ initialized: boolean; systems: EnterpriseSystem[] }>> {
    return this.request({
      method: 'GET',
      url: '/api/enterprise/status',
    });
  }

  async connectEnterpriseSystem(system: Omit<EnterpriseSystem, 'status' | 'last_sync'>): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: '/api/enterprise/systems',
      data: system,
    });
  }

  async disconnectEnterpriseSystem(systemName: string): Promise<ApiResponse<any>> {
    return this.request({
      method: 'DELETE',
      url: `/api/enterprise/systems/${systemName}`,
    });
  }

  async getEnterpriseHealth(): Promise<ApiResponse<HealthStatus[]>> {
    return this.request({
      method: 'GET',
      url: '/api/enterprise/health',
    });
  }

  // Scenarios
  async runScenario(scenarioType: string, params: Record<string, any>): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: `/api/scenarios/${scenarioType}`,
      data: params,
    });
  }

  // Multi-Agent AI
  async getAgentStatus(): Promise<ApiResponse<Array<{
    name: string;
    status: 'ready' | 'busy' | 'error';
    specialization: string;
  }>>> {
    return this.request({
      method: 'GET',
      url: '/api/agents/status',
    });
  }

  async executeAgentTask(agentName: string, task: string, params?: Record<string, any>): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: `/api/agents/${agentName}/execute`,
      data: { task, params },
    });
  }

  // Knowledge Graph
  async getKnowledgeGraphData(nodeType?: string, depth?: number): Promise<ApiResponse<any>> {
    return this.request({
      method: 'GET',
      url: '/api/knowledge-graph',
      params: { node_type: nodeType, depth },
    });
  }

  async searchKnowledgeGraph(query: string): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: '/api/knowledge-graph/search',
      data: { query },
    });
  }

  // Analytics
  async getAnalytics(type: string, params?: Record<string, any>): Promise<ApiResponse<any>> {
    return this.request({
      method: 'GET',
      url: `/api/analytics/${type}`,
      params,
    });
  }

  // Reports
  async generateReport(reportType: string, params: Record<string, any>): Promise<ApiResponse<{ reportId: string }>> {
    return this.request({
      method: 'POST',
      url: '/api/reports/generate',
      data: { type: reportType, params },
    });
  }

  async getReportStatus(reportId: string): Promise<ApiResponse<{ status: string; downloadUrl?: string }>> {
    return this.request({
      method: 'GET',
      url: `/api/reports/${reportId}/status`,
    });
  }

  async downloadReport(reportId: string): Promise<Blob> {
    const response = await this.api.get(`/api/reports/${reportId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Settings
  async getSettings(): Promise<ApiResponse<Record<string, any>>> {
    return this.request({
      method: 'GET',
      url: '/api/settings',
    });
  }

  async updateSettings(settings: Record<string, any>): Promise<ApiResponse<any>> {
    return this.request({
      method: 'PUT',
      url: '/api/settings',
      data: settings,
    });
  }

  // Portfolio Assessment (IoC Methodology)
  async assessPortfolio(request: {
    portfolio_entries: any[];
    supervisor_comments: any[];
    student_info: any;
    assessor_info: any;
    suggested_skill?: string;
    suggested_level?: number;
  }): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: '/api/portfolio/assess',
      data: request,
    });
  }

  async getPortfolioGuidance(request: {
    activities_description: string;
    student_level: string;
  }): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: '/api/portfolio/guidance',
      data: request,
    });
  }

  async validatePortfolioEvidence(request: {
    portfolio_entries: any[];
    skill_code: string;
    skill_level: number;
  }): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: '/api/portfolio/validate',
      data: request,
    });
  }

  async generatePortfolioTemplate(request: {
    skill_code: string;
    skill_level: number;
    placement_context?: string;
  }): Promise<ApiResponse<any>> {
    return this.request({
      method: 'POST',
      url: '/api/portfolio/template',
      data: request,
    });
  }

  async getPortfolioMethodologyInfo(): Promise<ApiResponse<any>> {
    return this.request({
      method: 'GET',
      url: '/api/portfolio/ioc-methodology',
    });
  }

  // Real-time updates via WebSocket (placeholder for future implementation)
  createWebSocketConnection(onMessage: (data: any) => void): WebSocket | null {
    try {
      const wsUrl = this.baseURL.replace('http', 'ws') + '/ws';
      const ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Real-time connection error');
      };

      return ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      return null;
    }
  }
}

export const apiService = new ApiService();
export default apiService;