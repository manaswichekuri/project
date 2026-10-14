import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <aside class="soc-sidebar">
      <nav class="nav-list">
        <a routerLink="/dashboard" routerLinkActive="active" class="nav-item">
          <span class="material-icons-outlined">dashboard</span>
          <span class="label">Dashboard</span>
        </a>

        <a routerLink="/users" routerLinkActive="active" class="nav-item">
          <span class="material-icons-outlined">people</span>
          <span class="label">Monitored Users</span>
        </a>

        <a routerLink="/activity-logs" routerLinkActive="active" class="nav-item">
          <span class="material-icons-outlined">list_alt</span>
          <span class="label">Activity Logs</span>
        </a>

        <a routerLink="/alerts" routerLinkActive="active" class="nav-item">
          <span class="material-icons-outlined">notifications_active</span>
          <span class="label">Security Alerts</span>
        </a>

        <a routerLink="/analytics" routerLinkActive="active" class="nav-item">
          <span class="material-icons-outlined">insights</span>
          <span class="label">Threat Analytics</span>
        </a>

        <a routerLink="/system-info" routerLinkActive="active" class="nav-item">
          <span class="material-icons-outlined">memory</span>
          <span class="label">ML Diagnostics</span>
        </a>
      </nav>

      <div class="sidebar-footer">
        <div class="status-indicator">
          <span class="dot"></span>
          <span>Engine Active</span>
        </div>
      </div>
    </aside>
  `,
  styles: [`
    .soc-sidebar {
      width: 240px;
      background: #0d1322;
      border-right: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 1.5rem 0.75rem;
      min-height: calc(100vh - 70px);
    }

    .nav-list {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 0.85rem;
      padding: 0.75rem 1rem;
      border-radius: 8px;
      color: #9ca3af;
      text-decoration: none;
      font-size: 0.875rem;
      font-weight: 500;
      transition: all 0.15s ease;

      .material-icons-outlined {
        font-size: 1.25rem;
      }

      &:hover {
        color: #ffffff;
        background: rgba(255, 255, 255, 0.05);
      }

      &.active {
        color: #06b6d4;
        background: rgba(6, 182, 212, 0.12);
        border: 1px solid rgba(6, 182, 212, 0.25);
        font-weight: 600;
      }
    }

    .sidebar-footer {
      padding: 0.85rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);

      .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        color: #10b981;

        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #10b981;
          box-shadow: 0 0 8px #10b981;
        }
      }
    }
  `]
})
export class SidebarComponent {}
