import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { User, UserListResponse } from '../../models/user.model';
import { ActivityListResponse, ActivityStats } from '../../models/activity.model';
import { RiskSummary } from '../../models/risk.model';
import { AlertListResponse, AlertStats, SecurityAlert } from '../../models/alert.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiBaseUrl;
  private dataRefreshSource = new Subject<void>();
  public dataRefresh$ = this.dataRefreshSource.asObservable();

  constructor(private http: HttpClient) {}

  notifyDataChanged(): void {
    this.dataRefreshSource.next();
  }

  // System Diagnostics
  getSystemStatus(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/system/status`);
  }

  // Monitored Users
  getUsers(search?: string, department?: string, riskCategory?: string): Observable<UserListResponse> {
    let params = new HttpParams();
    if (search) params = params.set('search', search);
    if (department) params = params.set('department', department);
    if (riskCategory) params = params.set('risk_category', riskCategory);
    return this.http.get<UserListResponse>(`${this.baseUrl}/users`, { params });
  }

  getUserById(userId: string): Observable<{ user: User }> {
    return this.http.get<{ user: User }>(`${this.baseUrl}/users/${encodeURIComponent(userId)}`);
  }

  getUserRiskProfile(userId: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/users/${encodeURIComponent(userId)}/risk-profile`);
  }

  // Activity Logs
  getActivities(userId?: string, eventType?: string, afterHours?: boolean, page: number = 1, limit: number = 50): Observable<ActivityListResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());
    if (userId) params = params.set('user_id', userId);
    if (eventType) params = params.set('event_type', eventType);
    if (afterHours) params = params.set('after_hours', 'true');
    return this.http.get<ActivityListResponse>(`${this.baseUrl}/activities`, { params });
  }

  getActivityStats(): Observable<ActivityStats> {
    return this.http.get<ActivityStats>(`${this.baseUrl}/activities/stats`);
  }

  generateSyntheticData(days: number = 7, reset: boolean = true): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/activities/synthetic/generate`, { days, reset });
  }

  // ML & Detection
  runMlDetection(): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/ml/run-detection`, {});
  }

  getModelInfo(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/ml/model-info`);
  }

  // Risk Scores
  getRiskSummary(): Observable<RiskSummary> {
    return this.http.get<RiskSummary>(`${this.baseUrl}/risk/summary`);
  }

  // Security Alerts
  getAlerts(status?: string, severity?: string, userId?: string): Observable<AlertListResponse> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    if (severity) params = params.set('severity', severity);
    if (userId) params = params.set('user_id', userId);
    return this.http.get<AlertListResponse>(`${this.baseUrl}/alerts`, { params });
  }

  updateAlertStatus(alertId: string, status: string, notes?: string): Observable<{ message: string; alert: SecurityAlert }> {
    return this.http.patch<{ message: string; alert: SecurityAlert }>(`${this.baseUrl}/alerts/${encodeURIComponent(alertId)}`, { status, notes });
  }

  getAlertStats(): Observable<AlertStats> {
    return this.http.get<AlertStats>(`${this.baseUrl}/alerts/stats`);
  }
}
