import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AdminUser, AuthService } from '../../../core/services/auth.service';
import { NotificationService } from '../../../core/services/notification.service';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header class="soc-navbar">
      <div class="brand-container">
        <div class="cyber-logo">
          <span class="material-icons-outlined logo-icon">shield</span>
          <div class="logo-text">
            <span class="title">INSIDER THREAT SOC</span>
            <span class="subtitle">AI Behavioral Detection System</span>
          </div>
        </div>
      </div>

      <div class="actions-container">
        <button class="btn-cyber secondary" (click)="onGenerateData()" [disabled]="isProcessing">
          <span class="material-icons-outlined">extension</span>
          <span>Generate Demo Data</span>
        </button>

        <button class="btn-cyber primary" (click)="onRunDetection()" [disabled]="isProcessing">
          <span class="material-icons-outlined">psychology</span>
          <span>{{ isProcessing ? 'Processing ML...' : 'Run ML Detection' }}</span>
        </button>

        <div class="user-profile" *ngIf="currentUser">
          <div class="avatar">
            <span class="material-icons-outlined">admin_panel_settings</span>
          </div>
          <div class="info">
            <span class="name">{{ currentUser.name }}</span>
            <span class="role">{{ currentUser.role }}</span>
          </div>
          <button class="btn-logout" (click)="logout()" title="Logout">
            <span class="material-icons-outlined">logout</span>
          </button>
        </div>
      </div>
    </header>
  `,
  styles: [`
    .soc-navbar {
      height: 70px;
      background: rgba(17, 24, 39, 0.95);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(12px);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1.5rem;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .brand-container {
      display: flex;
      align-items: center;
    }

    .cyber-logo {
      display: flex;
      align-items: center;
      gap: 0.75rem;

      .logo-icon {
        font-size: 2.2rem;
        color: #06b6d4;
        filter: drop-shadow(0 0 8px rgba(6, 182, 212, 0.5));
      }

      .logo-text {
        display: flex;
        flex-direction: column;

        .title {
          font-weight: 800;
          font-size: 1.05rem;
          letter-spacing: 0.08em;
          background: linear-gradient(135deg, #ffffff, #06b6d4);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .subtitle {
          font-size: 0.72rem;
          color: #9ca3af;
          letter-spacing: 0.04em;
        }
      }
    }

    .actions-container {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .user-profile {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding-left: 1rem;
      border-left: 1px solid rgba(255, 255, 255, 0.1);

      .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(99, 102, 241, 0.2);
        color: #6366f1;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(99, 102, 241, 0.4);
      }

      .info {
        display: flex;
        flex-direction: column;

        .name {
          font-size: 0.85rem;
          font-weight: 600;
          color: #f9fafb;
        }

        .role {
          font-size: 0.7rem;
          color: #9ca3af;
        }
      }

      .btn-logout {
        background: transparent;
        border: none;
        color: #9ca3af;
        cursor: pointer;
        padding: 0.3rem;
        border-radius: 4px;

        &:hover {
          color: #ef4444;
          background: rgba(239, 68, 68, 0.1);
        }
      }
    }
  `]
})
export class NavbarComponent {
  isProcessing = false;
  currentUser: AdminUser | null;

  constructor(
    private authService: AuthService,
    private apiService: ApiService,
    private notifications: NotificationService,
    private router: Router
  ) {
    this.currentUser = this.authService.getCurrentUser();
  }

  onGenerateData(): void {
    this.isProcessing = true;
    this.apiService.generateSyntheticData(7, true).subscribe({
      next: (res) => {
        this.isProcessing = false;
        this.notifications.success(res.message || 'Synthetic dataset generated.');
        this.apiService.notifyDataChanged();
      },
      error: () => this.isProcessing = false
    });
  }

  onRunDetection(): void {
    this.isProcessing = true;
    this.apiService.runMlDetection().subscribe({
      next: (res) => {
        this.isProcessing = false;
        this.notifications.success(`${res.message} ${res.alerts_generated ?? 0} new alert(s).`);
        this.apiService.notifyDataChanged();
      },
      error: () => this.isProcessing = false
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
