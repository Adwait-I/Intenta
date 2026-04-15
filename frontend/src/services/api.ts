/**
 * INTENTA — API Service
 * HTTP client for the FastAPI backend.
 */

import { getAuthHeaders } from './localAuth';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export interface GenerateRequest {
  input: string;
}

export interface IntentData {
  goal: string;
  users: string;
  scale: string;
  compliance: string[];
  integrations: string[];
  constraints: string[];
  domain: string;
  raw_input: string;
}

export interface ArchitectureData {
  pattern: string;
  services: string[];
  rationale: string;
  diagram_hint: string;
  trade_offs: string[];
}

export interface TechStackData {
  frontend: string[];
  backend: string[];
  database: string[];
  messaging: string[];
  infrastructure: string[];
  rationale: string;
  deployment_plan?: string;
  monitoring_observability?: string[];
}

export interface ServiceBlueprint {
  name: string;
  responsibility: string;
  endpoints: string[];
  dependencies: string[];
}

export interface CodeBlueprintData {
  services: ServiceBlueprint[];
  folder_structure: Record<string, unknown>;
  api_gateway: string;
  communication_style: string;
  data_model?: string;
  api_specifications?: string[];
}

export interface ValidationData {
  unit_tests: string[];
  integration_tests: string[];
  e2e_tests: string[];
  performance_benchmarks: string[];
  recommended_tools: string[];
}

export interface ComplianceRule {
  regulation: string;
  requirement: string;
  implementation: string;
  priority: string;
}

export interface ComplianceData {
  applicable_regulations: string[];
  rules: ComplianceRule[];
  data_classification: Record<string, string>;
  encryption_requirements: string[];
  audit_log_events: string[];
  security_framework?: string;
  overview_text?: string;
}

export interface RBACRole {
  role: string;
  permissions: string[];
  description: string;
  mfa_required: boolean;
}

export interface ApprovalWorkflow {
  name: string;
  steps: string[];
  sla_hours: number;
  auto_approved: boolean;
}

export interface GovernanceData {
  rbac_roles: RBACRole[];
  approval_workflows: ApprovalWorkflow[];
  data_owners: string[];
  change_management: string;
  development_roadmap?: string | string[];
  documentation_plan?: string;
}

export interface DecisionEntry {
  decision: string;
  rationale: string;
  alternatives: string[];
  trade_offs: string[];
  risk_level: string;
}

export interface ExplainabilityData {
  decisions: DecisionEntry[];
  overall_risk_summary: string;
  confidence_score: number;
  cost_estimation?: string;
}

export interface GenerateResponse {
  session_id: string;
  intent: IntentData;
  architecture: ArchitectureData;
  tech_stack: TechStackData;
  code_blueprint: CodeBlueprintData;
  validation: ValidationData;
  compliance: ComplianceData;
  governance: GovernanceData;
  explainability: ExplainabilityData;
  processing_time_ms: number;
  integrations_triggered: string[];
}

class APIError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function generateDesign(
  intentText: string,
  userEmail: string | null = null
): Promise<GenerateResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 600000); // 10-minute timeout

  try {
    const response = await fetch(`${API_BASE_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ input: intentText }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errBody = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new APIError(response.status, errBody.detail || `HTTP ${response.status}`);
    }

    return (await response.json()) as GenerateResponse;
  } catch (err) {
    if (err instanceof APIError) throw err;
    if ((err as Error).name === 'AbortError') {
      throw new APIError(408, 'Request timed out — LLM is processing, please retry');
    }
    throw new APIError(0, `Network error: ${(err as Error).message}`);
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function checkHealth(): Promise<{ status: string; llm_available: boolean }> {
  try {
    const r = await fetch(`${API_BASE_URL}/health`, { method: 'GET' });
    return await r.json();
  } catch {
    return { status: 'unreachable', llm_available: false };
  }
}

export async function trackLogin(email: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({ email }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function fetchSessions(): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/sessions`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return [];
    const data = await response.json();
    return data.sessions || [];
  } catch {
    return [];
  }
}

export async function fetchSessionById(sessionId: string): Promise<GenerateResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.session.data as GenerateResponse; // The backend wrapper contains "session.data" for the full GenerateResponse object
  } catch {
    return null;
  }
}

export async function deleteSession(sessionId: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
      },
    });
    return response.ok;
  } catch {
    return false;
  }
}
