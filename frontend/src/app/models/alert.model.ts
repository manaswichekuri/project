export interface SecurityAlert {
  alert_id: string;
  user_id: string;
  timestamp: string;
  event_type: string;
  risk_score: number;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  status: 'Open' | 'Investigating' | 'Resolved';
  reasons: string[];
  assigned_to?: string | null;
  admin_notes?: string;
  updated_at?: string;
}

export interface AlertListResponse {
  alerts: SecurityAlert[];
  total: number;
}

export interface AlertStats {
  total: number;
  status_breakdown: {
    Open: number;
    Investigating: number;
    Resolved: number;
  };
  severity_breakdown: {
    Critical: number;
    High: number;
    Medium: number;
    Low: number;
  };
}
