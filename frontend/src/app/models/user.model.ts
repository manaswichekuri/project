export interface User {
  user_id: string;
  name: string;
  email: string;
  department: string;
  role: string;
  baseline_location: string;
  baseline_device: string;
  current_risk_score?: number;
  risk_category?: 'Low' | 'Medium' | 'High' | 'Critical';
  last_evaluated_at?: string;
  reasons?: string[];
  is_demo_synthetic?: boolean;
}

export interface UserListResponse {
  users: User[];
  total: number;
}
