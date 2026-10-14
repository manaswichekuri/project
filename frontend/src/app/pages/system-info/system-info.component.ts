import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-system-info',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="system-info-page">
      <div class="page-header">
        <div>
          <h2>ML Engine & System Diagnostics</h2>
          <p>Technical parameters of the Isolation Forest anomaly detector and database status</p>
        </div>
      </div>

      <div class="info-grid">
        <!-- ML Pipeline Architecture -->
        <div class="cyber-card card-item">
          <h3>Machine Learning Model Architecture</h3>
          <div class="tech-badge">Isolation Forest (scikit-learn)</div>
          <p class="desc">
            An unsupervised anomaly detection algorithm that isolates observation instances by randomly selecting a feature and splitting value. Outliers require significantly fewer splits to isolate than normal observations.
          </p>
          <div class="params-list" *ngIf="modelInfo">
            <div class="param-row">
              <span class="param-name">Algorithm</span>
              <span class="param-val"><code>{{ modelInfo.algorithm }}</code></span>
            </div>
            <div class="param-row">
              <span class="param-name">Contamination Rate</span>
              <span class="param-val"><code>{{ modelInfo.contamination }} (10%)</code></span>
            </div>
            <div class="param-row">
              <span class="param-name">Risk Threshold (High)</span>
              <span class="param-val"><code>{{ modelInfo.risk_thresholds?.High }} / 100</code></span>
            </div>
            <div class="param-row">
              <span class="param-name">Risk Threshold (Critical)</span>
              <span class="param-val"><code>{{ modelInfo.risk_thresholds?.Critical }} / 100</code></span>
            </div>
          </div>
        </div>

        <!-- Engineered Behavioral Features -->
        <div class="cyber-card card-item">
          <h3>Engineered Behavioral Features</h3>
          <ul class="feature-list" *ngIf="modelInfo">
            <li *ngFor="let feat of modelInfo.features_engineered">
              <span class="material-icons-outlined feat-icon">check_circle</span>
              <code>{{ feat }}</code>
            </li>
          </ul>
        </div>

        <!-- Database & Service Status -->
        <div class="cyber-card card-item full-width" *ngIf="systemStatus">
          <h3>System & Persistent Database Status</h3>
          <div class="status-grid">
            <div class="status-box">
              <span class="box-title">Database Mode</span>
              <span class="box-val">{{ systemStatus.database?.is_mock ? 'In-Memory Mongomock' : 'Physical MongoDB' }}</span>
            </div>
            <div class="status-box">
              <span class="box-title">Total Users</span>
              <span class="box-val">{{ systemStatus.database?.collections?.users }}</span>
            </div>
            <div class="status-box">
              <span class="box-title">Total Activities</span>
              <span class="box-val">{{ systemStatus.database?.collections?.activities }}</span>
            </div>
            <div class="status-box">
              <span class="box-title">Total Alerts</span>
              <span class="box-val">{{ systemStatus.database?.collections?.alerts }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .system-info-page {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .page-header {
      h2 { font-size: 1.5rem; font-weight: 800; color: #ffffff; }
      p { font-size: 0.85rem; color: #9ca3af; }
    }

    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.25rem;

      @media (max-width: 900px) { grid-template-columns: 1fr; }
    }

    .full-width { grid-column: 1 / -1; }

    .card-item {
      h3 { font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem; }
      .desc { font-size: 0.85rem; color: #9ca3af; margin-top: 0.5rem; line-height: 1.5; }
    }

    .tech-badge {
      display: inline-block;
      background: rgba(6, 182, 212, 0.15);
      color: #06b6d4;
      border: 1px solid rgba(6, 182, 212, 0.3);
      padding: 0.25rem 0.65rem;
      border-radius: 9999px;
      font-size: 0.78rem;
      font-weight: 600;
    }

    .params-list {
      margin-top: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;

      .param-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);

        .param-name { color: #9ca3af; }
        .param-val { color: #ffffff; }
      }
    }

    .feature-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      margin-top: 1rem;

      li {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.88rem;
        color: #f9fafb;

        .feat-icon { color: #10b981; font-size: 1.1rem; }
      }
    }

    .status-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-top: 1rem;

      .status-box {
        background: #1f2937;
        padding: 1rem;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        gap: 0.35rem;

        .box-title { font-size: 0.75rem; color: #9ca3af; font-weight: 600; }
        .box-val { font-size: 1.15rem; font-weight: 800; color: #06b6d4; }
      }
    }
  `]
})
export class SystemInfoComponent implements OnInit {
  modelInfo: any = null;
  systemStatus: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.apiService.getModelInfo().subscribe(data => this.modelInfo = data);
    this.apiService.getSystemStatus().subscribe(data => this.systemStatus = data);
  }
}
