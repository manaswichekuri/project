export interface RiskScore {
  user_id: string;
  evaluated_at: string;
  raw_anomaly_score: number;
  normalized_risk_score: number;
  risk_category: 'Low' | 'Medium' | 'High' | 'Critical';
  contributing_reasons: string[];
  feature_metrics: Record<string, any>;
}

export interface RiskDistribution {
  Low: number;
  Medium: number;
  High: number;
  Critical: number;
}

export interface RiskSummary {
  total_users: number;
  total_activities: number;
  risk_distribution: RiskDistribution;
  high_risk_users_count: number;
  active_alerts_count: number;
}
