import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { RiskBadgeComponent } from '../../shared/components/risk-badge/risk-badge.component';
import { ActivityLog } from '../../models/activity.model';
import { SecurityAlert } from '../../models/alert.model';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-user-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, RiskBadgeComponent],
  template: `
    <div class="user-detail-page" *ngIf="profileData">
      <!-- Top Navigation -->
      <div class="back-nav">
        <a routerLink="/users" class="btn-back">
          <span class="material-icons-outlined">arrow_back</span>
          <span>Back to Monitored Users</span>
        </a>
      </div>

      <!-- User Header Card -->
      <div class="cyber-card user-header-card">
        <div class="user-info">
          <div class="avatar-large">
            <span class="material-icons-outlined">person</span>
          </div>
          <div>
            <h2>{{ profileData.user.name }}</h2>
            <div class="meta-row">
              <code>{{ profileData.user.user_id }}</code>
              <span>&bull;</span>
              <span>{{ profileData.user.role }}</span>
              <span>&bull;</span>
              <span>{{ profileData.user.department }}</span>
            </div>
          </div>
        </div>

        <div class="risk-score-box">
          <div class="score-meta">
            <span class="score-label">CURRENT RISK SCORE</span>
            <app-risk-badge [category]="profileData.user.risk_category || 'Low'"></app-risk-badge>
          </div>
          <div class="score-display" [ngClass]="profileData.user.risk_category?.toLowerCase() || 'low'">
            {{ profileData.user.current_risk_score }} <span class="max-score">/ 100</span>
          </div>
        </div>
      </div>

      <!-- Details & Explainability Grid -->
      <div class="profile-grid">
        <!-- Baseline Profile Parameters -->
        <div class="cyber-card details-card">
          <h3>Baseline Parameters</h3>
          <div class="info-list">
            <div class="info-item">
              <span class="label">Email Address</span>
              <span class="val">{{ profileData.user.email }}</span>
            </div>
            <div class="info-item">
              <span class="label">Primary Department</span>
              <span class="val">{{ profileData.user.department }}</span>
            </div>
            <div class="info-item">
              <span class="label">Baseline Office Location</span>
              <span class="val">{{ profileData.user.baseline_location }}</span>
            </div>
            <div class="info-item">
              <span class="label">Registered Baseline Device</span>
              <span class="val"><code>{{ profileData.user.baseline_device }}</code></span>
            </div>
            <div class="info-item">
              <span class="label">Last Evaluated</span>
              <span class="val">{{ profileData.user.last_evaluated_at | date:'medium' }}</span>
            </div>
          </div>
        </div>

        <!-- Explainability Reasons -->
        <div class="cyber-card explainability-card">
          <h3>Risk Explanation & Behavioral Findings</h3>
          <p class="subtitle">Interpretable AI reasons contributing to current score</p>
          <div class="reasons-list">
            <div class="reason-item" *ngFor="let reason of profileData.user.reasons">
              <span class="material-icons-outlined reason-icon">report_problem</span>
              <span>{{ reason }}</span>
            </div>
            <div class="no-reasons" *ngIf="!profileData.user.reasons || profileData.user.reasons.length === 0">
              <span class="material-icons-outlined">verified</span>
              <span>No anomalous behavior detected for this user baseline.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Timeline -->
      <div class="cyber-card timeline-card">
        <h3>User Activity Timeline</h3>
        <div class="cyber-table-container">
          <table class="cyber-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event Type</th>
                <th>IP & Location</th>
                <th>Device ID</th>
                <th>File / Application Details</th>
                <th>After-Hours</th>
                <th>Failed Logins</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let act of profileData.recent_activities">
                <td>{{ act.timestamp | date:'short' }}</td>
                <td>
                  <span class="event-type-badge">{{ act.event_type }}</span>
                </td>
                <td>{{ act.location_name }} ({{ act.location_ip }})</td>
                <td><code>{{ act.device_id }}</code></td>
                <td>
                  <div *ngIf="act.file_details?.filename">
                    <strong>{{ act.file_details.filename }}</strong>
                    <div class="sub-detail">
                      {{ act.file_details.download_size_mb }} MB DL | {{ act.file_details.upload_size_mb }} MB UL
                    </div>
                  </div>
                  <div *ngIf="!act.file_details?.filename">{{ act.app_used }}</div>
                </td>
                <td>
                  <span class="pill" [class.yes]="act.after_hours">{{ act.after_hours ? 'YES' : 'NO' }}</span>
                </td>
                <td>
                  <span [class.alert-text]="act.failed_logins > 0">{{ act.failed_logins }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .user-detail-page {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .btn-back {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      color: #06b6d4;
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 600;
      &:hover { text-decoration: underline; }
    }

    .user-header-card {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .user-info {
        display: flex;
        align-items: center;
        gap: 1.25rem;

        .avatar-large {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          background: rgba(6, 182, 212, 0.15);
          color: #06b6d4;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 1px solid rgba(6, 182, 212, 0.4);
          .material-icons-outlined { font-size: 2rem; }
        }

        h2 { font-size: 1.4rem; font-weight: 800; color: #ffffff; }
        .meta-row {
          display: flex;
          gap: 0.5rem;
          color: #9ca3af;
          font-size: 0.85rem;
          align-items: center;
          margin-top: 0.2rem;
        }
      }

      .risk-score-box {
        display: flex;
        flex-direction: column;
        align-items: flex-end;

        .score-meta {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.35rem;

          .score-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #6b7280;
          }
        }

        .score-display {
          font-size: 2.25rem;
          font-weight: 900;

          .max-score { font-size: 1rem; color: #6b7280; font-weight: 500; }

          &.critical { color: #ef4444; }
          &.high { color: #f97316; }
          &.medium { color: #f59e0b; }
          &.low { color: #10b981; }
        }
      }
    }

    .profile-grid {
      display: grid;
      grid-template-columns: 1fr 1.25fr;
      gap: 1.25rem;

      @media (max-width: 900px) { grid-template-columns: 1fr; }
    }

    .details-card, .explainability-card {
      h3 { font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 0.25rem; }
      .subtitle { font-size: 0.78rem; color: #9ca3af; margin-bottom: 1rem; }
    }

    .info-list {
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      margin-top: 1rem;

      .info-item {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 0.5rem;

        .label { color: #9ca3af; }
        .val { color: #ffffff; font-weight: 500; }
      }
    }

    .reasons-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;

      .reason-item {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.25);
        color: #fca5a5;
        padding: 0.75rem 0.85rem;
        border-radius: 8px;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.65rem;

        .reason-icon { font-size: 1.15rem; color: #f97316; }
      }

      .no-reasons {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #10b981;
        font-size: 0.85rem;
        padding: 1rem;
        background: rgba(16, 185, 129, 0.1);
        border-radius: 8px;
      }
    }

    .event-type-badge {
      background: #1f2937;
      color: #06b6d4;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .sub-detail { font-size: 0.72rem; color: #9ca3af; }
    .pill {
      font-size: 0.72rem;
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      background: #1f2937;
      color: #9ca3af;
      &.yes { background: rgba(239, 68, 68, 0.2); color: #fca5a5; }
    }
    .alert-text { color: #ef4444; font-weight: 700; }
  `]
})
export class UserDetailComponent implements OnInit {
  profileData: any = null;

  constructor(
    private route: ActivatedRoute,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    const userId = this.route.snapshot.paramMap.get('id');
    if (userId) {
      this.apiService.getUserRiskProfile(userId).subscribe(data => this.profileData = data);
    }
  }
}
