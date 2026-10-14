import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './shared/components/navbar/navbar.component';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';
import { AuthService } from './core/services/auth.service';
import { NotificationService } from './core/services/notification.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, NavbarComponent, SidebarComponent],
  template: `
    <div class="soc-layout" *ngIf="authService.isAuthenticated(); else publicLayout">
      <app-navbar></app-navbar>

      <div class="soc-body">
        <app-sidebar></app-sidebar>

        <main class="soc-main-content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>

    <ng-template #publicLayout>
      <router-outlet></router-outlet>
    </ng-template>

    @if (notifications.notification(); as note) {
      <div class="toast" [class.error]="note.type === 'error'" role="status" aria-live="polite">
        <span class="material-icons-outlined">{{ note.type === 'error' ? 'error_outline' : 'check_circle' }}</span>
        <span class="toast-text">{{ note.text }}</span>
        <button type="button" (click)="notifications.dismiss()" aria-label="Dismiss">
          <span class="material-icons-outlined">close</span>
        </button>
      </div>
    }
  `,
  styles: [`
    .soc-layout {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      background-color: #0b0f19;
    }

    .soc-body {
      display: flex;
      flex: 1;
    }

    .soc-main-content {
      flex: 1;
      min-width: 0;
      padding: 1.75rem;
      overflow-y: auto;
      background-color: #0b0f19;
    }

    .toast {
      position: fixed;
      right: 1.5rem;
      bottom: 1.5rem;
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      max-width: 420px;
      padding: 0.8rem 1rem;
      border-radius: 10px;
      background: #0f2a22;
      border: 1px solid #10b981;
      color: #d1fae5;
      font-size: 0.85rem;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
    }

    .toast.error {
      background: #2a1215;
      border-color: #ef4444;
      color: #fee2e2;
    }

    .toast-text { flex: 1; }

    .toast button {
      background: none;
      border: none;
      color: inherit;
      cursor: pointer;
      display: flex;
      padding: 0;
    }
  `]
})
export class AppComponent {
  constructor(public authService: AuthService, public notifications: NotificationService) {}
}
