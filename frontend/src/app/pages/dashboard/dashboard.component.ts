import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { MetricCardComponent } from '../../shared/components/metric-card/metric-card.component';
import { RiskBadgeComponent } from '../../shared/components/risk-badge/risk-badge.component';
import { RiskSummary } from '../../models/risk.model';
import { SecurityAlert } from '../../models/alert.model';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, MetricCardComponent, RiskBadgeComponent],
  template: `
    <div class="dashboard-page">
      <div class="page-header">
        <div>
          <h2>SOC Threat Overview</h2>
          <p>Real-time machine learning behavioral anomaly detection & risk scoring</p>
        </div>
        <div class="header-badge">
          <span class="pulse-dot"></span>
          <span>Live Analysis Active</span>
        </div>
      </div>

      <!-- KPI Metrics Grid -->
      <div class="metrics-grid">
        <app-metric-card
          title="Monitored Users"
          [value]="summary?.total_users || 0"
          icon="groups"
          subtitle="Monitored profiles"
        ></app-metric-card>

        <app-metric-card
          title="Activity Logs"
          [value]="summary?.total_activities || 0"
          icon="history"
          subtitle="Total ingested events"
        ></app-metric-card>

        <app-metric-card
          title="High Risk Users"
          [value]="summary?.high_risk_users_count || 0"
          icon="warning"
          variant="danger"
          subtitle="Require SOC review"
        ></app-metric-card>

        <app-metric-card
          title="Active Security Alerts"
          [value]="summary?.active_alerts_count || 0"
          icon="notifications_active"
          variant="warning"
          subtitle="Open investigation tickets"
        ></app-metric-card>
      </div>

      <!-- Risk Distribution & Quick Diagnostics -->
      <div class="summary-row">
        <div class="cyber-card risk-distribution-card">
          <h3>Organizational Risk Breakdown</h3>
          <div class="distribution-bars" *ngIf="summary">
            <div class="dist-item">
              <div class="label-row">
                <span>Critical Risk (85-100)</span>
                <span class="count critical">{{ summary.risk_distribution.Critical }} Users</span>
              </div>
              <div class="progress-bg">
                <div class="progress-fill critical" [style.width.%]="getPercentage(summary.risk_distribution.Critical)"></div>
              </div>
            </div>

            <div class="dist-item">
              <div class="label-row">
                <span>High Risk (60-84)</span>
                <span class="count high">{{ summary.risk_distribution.High }} Users</span>
              </div>
              <div class="progress-bg">
                <div class="progress-fill high" [style.width.%]="getPercentage(summary.risk_distribution.High)"></div>
              </div>
            </div>

            <div class="dist-item">
              <div class="label-row">
                <span>Medium Risk (30-59)</span>
                <span class="count medium">{{ summary.risk_distribution.Medium }} Users</span>
              </div>
              <div class="progress-bg">
                <div class="progress-fill medium" [style.width.%]="getPercentage(summary.risk_distribution.Medium)"></div>
              </div>
            </div>

            <div class="dist-item">
              <div class="label-row">
                <span>Low Risk (0-29)</span>
                <span class="count low">{{ summary.risk_distribution.Low }} Users</span>
              </div>
              <div class="progress-bg">
                <div class="progress-fill low" [style.width.%]="getPercentage(summary.risk_distribution.Low)"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- High Risk Users Table & Recent Security Alerts -->
      <div class="tables-grid">
        <div class="cyber-card table-card">
          <div class="card-header">
            <h3>High & Critical Risk Profiles</h3>
            <a routerLink="/users" class="view-link">View All Users &rarr;</a>
          </div>
          <div class="cyber-table-container">
            <table class="cyber-table">
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Risk Score</th>
                  <th>Category</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let u of highRiskUsers">
                  <td><code>{{ u.user_id }}</code></td>
                  <td>{{ u.name }}</td>
                  <td>{{ u.department }}</td>
                  <td><strong>{{ u.current_risk_score }}</strong></td>
                  <td>
                    <app-risk-badge [category]="u.risk_category || 'Low'"></app-risk-badge>
                  </td>
                  <td>
                    <a [routerLink]="['/users', u.user_id]" class="btn-cyber secondary btn-sm">Profile</a>
                  </td>
                </tr>
                <tr *ngIf="highRiskUsers.length === 0">
                  <td colspan="6" class="empty-cell">No high or critical risk users detected.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="cyber-card table-card">
          <div class="card-header">
            <h3>Recent Active Security Alerts</h3>
            <a routerLink="/alerts" class="view-link">Manage Alerts &rarr;</a>
          </div>
          <div class="cyber-table-container">
            <table class="cyber-table">
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>User</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let a of recentAlerts">
                  <td><code>{{ a.alert_id }}</code></td>
                  <td>{{ a.user_id }}</td>
                  <td>
                    <app-risk-badge [category]="a.severity"></app-risk-badge>
                  </td>
                  <td>
                    <span class="status-pill" [ngClass]="a.status.toLowerCase()">{{ a.status }}</span>
                  </td>
                  <td>
                    <a [routerLink]="['/alerts']" class="btn-cyber secondary btn-sm">Investigate</a>
                  </td>
                </tr>
                <tr *ngIf="recentAlerts.length === 0">
                  <td colspan="5" class="empty-cell">No active alerts available.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-page {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h2 {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
      }

      p {
        font-size: 0.85rem;
        color: #9ca3af;
      }

      .header-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
        padding: 0.4rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;

        .pulse-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #10b981;
          box-shadow: 0 0 8px #10b981;
        }
      }
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
    }

    .summary-row {
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.25rem;
    }

    .risk-distribution-card {
      h3 {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1.25rem;
      }
    }

    .distribution-bars {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .dist-item {
      .label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        margin-bottom: 0.35rem;
        color: #9ca3af;

        .count {
          font-weight: 700;
          &.critical { color: #ef4444; }
          &.high { color: #f97316; }
          &.medium { color: #f59e0b; }
          &.low { color: #10b981; }
        }
      }

      .progress-bg {
        height: 8px;
        background: #1f2937;
        border-radius: 4px;
        overflow: hidden;

        .progress-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.4s ease;

          &.critical { background: #ef4444; }
          &.high { background: #f97316; }
          &.medium { background: #f59e0b; }
          &.low { background: #10b981; }
        }
      }
    }

    .tables-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.25rem;

      @media (max-width: 1024px) {
        grid-template-columns: 1fr;
      }
    }

    .table-card {
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;

        h3 {
          font-size: 1.05rem;
          font-weight: 700;
          color: #ffffff;
        }

        .view-link {
          font-size: 0.8rem;
          color: #06b6d4;
          text-decoration: none;
          &:hover { text-decoration: underline; }
        }
      }
    }

    .btn-sm {
      padding: 0.3rem 0.65rem;
      font-size: 0.75rem;
    }

    .empty-cell {
      text-align: center;
      color: #6b7280;
      padding: 1.5rem;
    }
  `]
})
export class DashboardComponent implements OnInit {
  summary: RiskSummary | null = null;
  highRiskUsers: User[] = [];
  recentAlerts: SecurityAlert[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadDashboardData();
    this.apiService.dataRefresh$.subscribe(() => {
      this.loadDashboardData();
    });
  }

  loadDashboardData(): void {
    this.apiService.getRiskSummary().subscribe(res => this.summary = res);

    this.apiService.getUsers().subscribe(res => {
      this.highRiskUsers = res.users.filter(u => u.risk_category === 'High' || u.risk_category === 'Critical');
    });

    this.apiService.getAlerts().subscribe(res => {
      this.recentAlerts = res.alerts.slice(0, 5);
    });
  }

  getPercentage(count: number): number {
    if (!this.summary || this.summary.total_users === 0) return 0;
    return Math.round((count / this.summary.total_users) * 100);
  }
}
