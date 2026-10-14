import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import { SecurityAlert } from '../../models/alert.model';
import { RiskBadgeComponent } from '../../shared/components/risk-badge/risk-badge.component';

@Component({
  selector: 'app-alerts',
  standalone: true,
  imports: [CommonModule, FormsModule, RiskBadgeComponent],
  template: `
    <div class="alerts-page">
      <div class="page-header">
        <div>
          <h2>Security Alert Center</h2>
          <p>Investigate and resolve behavioral threat alerts triggered by ML anomaly detection</p>
        </div>
      </div>

      <!-- Filter Controls -->
      <div class="cyber-card filters-card">
        <div class="filter-group">
          <label>Status</label>
          <select [(ngModel)]="selectedStatus" (change)="fetchAlerts()">
            <option value="All">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Investigating">Investigating</option>
            <option value="Resolved">Resolved</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Severity</label>
          <select [(ngModel)]="selectedSeverity" (change)="fetchAlerts()">
            <option value="All">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
          </select>
        </div>
      </div>

      <!-- Alerts List -->
      <div class="alerts-list">
        <div class="cyber-card alert-item-card" *ngFor="let alert of alerts">
          <div class="alert-top">
            <div class="alert-title">
              <span class="material-icons-outlined alert-icon" [ngClass]="alert.severity.toLowerCase()">
                warning
              </span>
              <div>
                <h4>{{ alert.alert_id }} - {{ alert.event_type }}</h4>
                <div class="meta">
                  <span>User: <code>{{ alert.user_id }}</code></span>
                  <span>&bull;</span>
                  <span>Triggered: {{ alert.timestamp | date:'medium' }}</span>
                </div>
              </div>
            </div>

            <div class="alert-badges">
              <app-risk-badge [category]="alert.severity" [score]="alert.risk_score"></app-risk-badge>
              <span class="status-pill" [ngClass]="alert.status.toLowerCase()">{{ alert.status }}</span>
            </div>
          </div>

          <!-- Alert Reasons -->
          <div class="alert-reasons">
            <span class="reasons-heading">Trigger Reasons:</span>
            <ul>
              <li *ngFor="let r of alert.reasons">{{ r }}</li>
            </ul>
          </div>

          <!-- Status Action Controls -->
          <div class="alert-footer">
            <span class="status-label">Update Status:</span>
            <div class="action-buttons">
              <button
                class="btn-cyber danger btn-sm"
                [disabled]="alert.status === 'Open'"
                (click)="updateStatus(alert.alert_id, 'Open')"
              >
                Mark Open
              </button>
              <button
                class="btn-cyber secondary btn-sm"
                [disabled]="alert.status === 'Investigating'"
                (click)="updateStatus(alert.alert_id, 'Investigating')"
              >
                Set Investigating
              </button>
              <button
                class="btn-cyber primary btn-sm"
                [disabled]="alert.status === 'Resolved'"
                (click)="updateStatus(alert.alert_id, 'Resolved')"
              >
                Resolve Ticket
              </button>
            </div>
          </div>
        </div>

        <div class="cyber-card empty-card" *ngIf="alerts.length === 0">
          <span class="material-icons-outlined">check_circle</span>
          <p>No security alerts found matching the current filters.</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .alerts-page {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .page-header {
      h2 { font-size: 1.5rem; font-weight: 800; color: #ffffff; }
      p { font-size: 0.85rem; color: #9ca3af; }
    }

    .filters-card {
      display: flex;
      gap: 1.25rem;

      .filter-group {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;

        label { font-size: 0.78rem; font-weight: 600; color: #9ca3af; }

        select {
          background: #1f2937;
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #ffffff;
          padding: 0.55rem 0.85rem;
          border-radius: 8px;
          font-size: 0.85rem;
          outline: none;
          min-width: 160px;
          &:focus { border-color: #06b6d4; }
        }
      }
    }

    .alerts-list {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .alert-item-card {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      border-left: 4px solid #06b6d4;
    }

    .alert-top {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .alert-title {
        display: flex;
        align-items: center;
        gap: 0.85rem;

        .alert-icon {
          font-size: 2rem;
          &.critical { color: #ef4444; }
          &.high { color: #f97316; }
          &.medium { color: #f59e0b; }
        }

        h4 { font-size: 1.05rem; font-weight: 700; color: #ffffff; }
        .meta { display: flex; gap: 0.5rem; font-size: 0.8rem; color: #9ca3af; margin-top: 0.15rem; }
      }

      .alert-badges {
        display: flex;
        align-items: center;
        gap: 0.75rem;
      }
    }

    .alert-reasons {
      background: #1f2937;
      padding: 0.85rem 1rem;
      border-radius: 8px;

      .reasons-heading { font-size: 0.78rem; font-weight: 700; color: #9ca3af; text-transform: uppercase; }

      ul {
        margin-top: 0.35rem;
        padding-left: 1.2rem;
        font-size: 0.85rem;
        color: #fca5a5;

        li { margin-bottom: 0.2rem; }
      }
    }

    .alert-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 0.75rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);

      .status-label { font-size: 0.8rem; color: #9ca3af; }
      .action-buttons { display: flex; gap: 0.5rem; }
    }

    .btn-sm { padding: 0.35rem 0.75rem; font-size: 0.78rem; }

    .empty-card {
      text-align: center;
      padding: 3rem;
      color: #6b7280;
      .material-icons-outlined { font-size: 3rem; color: #10b981; margin-bottom: 0.5rem; }
    }
  `]
})
export class AlertsComponent implements OnInit {
  alerts: SecurityAlert[] = [];
  selectedStatus = 'All';
  selectedSeverity = 'All';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.fetchAlerts();
    this.apiService.dataRefresh$.subscribe(() => {
      this.fetchAlerts();
    });
  }

  fetchAlerts(): void {
    this.apiService.getAlerts(this.selectedStatus, this.selectedSeverity).subscribe(res => {
      this.alerts = res.alerts;
    });
  }

  updateStatus(alertId: string, newStatus: string): void {
    this.apiService.updateAlertStatus(alertId, newStatus).subscribe(() => {
      this.fetchAlerts();
    });
  }
}
