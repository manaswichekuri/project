import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="analytics-page">
      <div class="page-header">
        <div>
          <h2>Threat Analytics & Visualizations</h2>
          <p>Statistical distribution metrics, anomaly trends, and alert severity analytics</p>
        </div>
      </div>

      <div class="charts-grid">
        <!-- Chart 1: Risk Distribution -->
        <div class="cyber-card chart-card">
          <h3>User Risk Distribution</h3>
          <p class="chart-sub">Breakdown of monitored users by risk tier</p>
          <div class="chart-wrapper">
            <canvas
              baseChart
              [data]="riskPieChartData"
              [type]="'doughnut'"
              [options]="chartOptions"
            ></canvas>
          </div>
        </div>

        <!-- Chart 2: Alert Severity -->
        <div class="cyber-card chart-card">
          <h3>Alert Severity Distribution</h3>
          <p class="chart-sub">Active threat tickets by severity level</p>
          <div class="chart-wrapper">
            <canvas
              baseChart
              [data]="severityBarChartData"
              [type]="'bar'"
              [options]="chartOptions"
            ></canvas>
          </div>
        </div>

        <!-- Chart 3: Activity Log Event Types -->
        <div class="cyber-card chart-card">
          <h3>Ingested Event Type Metrics</h3>
          <p class="chart-sub">Distribution of system activity event types</p>
          <div class="chart-wrapper">
            <canvas
              baseChart
              [data]="eventPieChartData"
              [type]="'pie'"
              [options]="chartOptions"
            ></canvas>
          </div>
        </div>

        <!-- Chart 4: Alert Resolution Status -->
        <div class="cyber-card chart-card">
          <h3>Alert Ticket Resolution Status</h3>
          <p class="chart-sub">Status breakdown of SOC alert investigations</p>
          <div class="chart-wrapper">
            <canvas
              baseChart
              [data]="statusDoughnutChartData"
              [type]="'doughnut'"
              [options]="chartOptions"
            ></canvas>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .analytics-page {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .page-header {
      h2 { font-size: 1.5rem; font-weight: 800; color: #ffffff; }
      p { font-size: 0.85rem; color: #9ca3af; }
    }

    .charts-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.25rem;

      @media (max-width: 900px) {
        grid-template-columns: 1fr;
      }
    }

    .chart-card {
      h3 { font-size: 1.05rem; font-weight: 700; color: #ffffff; }
      .chart-sub { font-size: 0.78rem; color: #9ca3af; margin-bottom: 1rem; }
    }

    .chart-wrapper {
      position: relative;
      height: 260px;
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  `]
})
export class AnalyticsComponent implements OnInit {
  public chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: '#9ca3af', font: { family: 'Inter', size: 11 } }
      }
    }
  };

  public riskPieChartData: ChartData<'doughnut'> = {
    labels: ['Critical Risk', 'High Risk', 'Medium Risk', 'Low Risk'],
    datasets: [{
      data: [0, 0, 0, 0],
      backgroundColor: ['#ef4444', '#f97316', '#f59e0b', '#10b981'],
      borderWidth: 0
    }]
  };

  public severityBarChartData: ChartData<'bar'> = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [{
      label: 'Alert Count',
      data: [0, 0, 0, 0],
      backgroundColor: ['#ef4444', '#f97316', '#f59e0b', '#10b981'],
      borderRadius: 6
    }]
  };

  public eventPieChartData: ChartData<'pie'> = {
    labels: ['File Download', 'File Upload', 'File Access', 'Login', 'App Usage'],
    datasets: [{
      data: [45, 20, 110, 85, 30],
      backgroundColor: ['#06b6d4', '#6366f1', '#8b5cf6', '#10b981', '#f59e0b'],
      borderWidth: 0
    }]
  };

  public statusDoughnutChartData: ChartData<'doughnut'> = {
    labels: ['Open', 'Investigating', 'Resolved'],
    datasets: [{
      data: [0, 0, 0],
      backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
      borderWidth: 0
    }]
  };

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadAnalytics();
    this.apiService.dataRefresh$.subscribe(() => {
      this.loadAnalytics();
    });
  }

  loadAnalytics(): void {
    this.apiService.getRiskSummary().subscribe(res => {
      if (res && res.risk_distribution) {
        this.riskPieChartData.datasets[0].data = [
          res.risk_distribution.Critical,
          res.risk_distribution.High,
          res.risk_distribution.Medium,
          res.risk_distribution.Low
        ];
        this.riskPieChartData = { ...this.riskPieChartData };
      }
    });

    this.apiService.getAlertStats().subscribe(res => {
      if (res) {
        this.severityBarChartData.datasets[0].data = [
          res.severity_breakdown.Critical,
          res.severity_breakdown.High,
          res.severity_breakdown.Medium,
          res.severity_breakdown.Low
        ];
        this.severityBarChartData = { ...this.severityBarChartData };

        this.statusDoughnutChartData.datasets[0].data = [
          res.status_breakdown.Open,
          res.status_breakdown.Investigating,
          res.status_breakdown.Resolved
        ];
        this.statusDoughnutChartData = { ...this.statusDoughnutChartData };
      }
    });
  }
}
