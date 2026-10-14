import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, Router } from '@angular/router';
import { NavbarComponent } from './shared/components/navbar/navbar.component';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';
import { AuthService } from './core/services/auth.service';
import { DashboardComponent } from './pages/dashboard/dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, NavbarComponent, SidebarComponent],
  template: `
    <div class="soc-layout" *ngIf="authService.isAuthenticated()">
      <app-navbar (actionTriggered)="onNavbarAction($event)"></app-navbar>

      <div class="soc-body">
        <app-sidebar></app-sidebar>

        <main class="soc-main-content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>

    <div *ngIf="!authService.isAuthenticated()">
      <router-outlet></router-outlet>
    </div>
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
      padding: 1.75rem;
      overflow-y: auto;
      background-color: #0b0f19;
    }
  `]
})
export class AppComponent {
  constructor(public authService: AuthService, private router: Router) {}

  onNavbarAction(action: string): void {
    if (action === 'DATA_GENERATED' || action === 'DETECTION_COMPLETED') {
      // Reload current route data
      const currentUrl = this.router.url;
      this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
        this.router.navigate([currentUrl]);
      });
    }
  }
}
