import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-wrapper">
      <div class="cyber-card login-card">
        <div class="login-header">
          <span class="material-icons-outlined brand-icon">security</span>
          <h1>INSIDER THREAT DETECTOR</h1>
          <p>SOC Administrator Portal</p>
        </div>

        <div class="error-banner" *ngIf="errorMessage">
          <span class="material-icons-outlined">error_outline</span>
          <span>{{ errorMessage }}</span>
        </div>

        <form (ngSubmit)="onSubmit()" class="login-form">
          <div class="form-group">
            <label for="username">Username</label>
            <div class="input-container">
              <span class="material-icons-outlined field-icon">person</span>
              <input
                type="text"
                id="username"
                name="username"
                [(ngModel)]="username"
                placeholder="Enter admin username"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <div class="input-container">
              <span class="material-icons-outlined field-icon">lock</span>
              <input
                type="password"
                id="password"
                name="password"
                [(ngModel)]="password"
                placeholder="Enter admin password"
                required
              />
            </div>
          </div>

          <button type="submit" class="btn-cyber primary full-width" [disabled]="loading">
            <span class="material-icons-outlined">login</span>
            <span>{{ loading ? 'Authenticating...' : 'Sign In to SOC' }}</span>
          </button>
        </form>

        <div class="demo-credentials">
          <span>Demo Credentials:</span>
          <code>admin / Admin&#64;12345</code>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-wrapper {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: radial-gradient(circle at 50% 30%, #1e1b4b 0%, #0b0f19 70%);
      padding: 1.5rem;
    }

    .login-card {
      width: 100%;
      max-width: 420px;
      border: 1px solid rgba(6, 182, 212, 0.3);
      box-shadow: 0 0 30px rgba(6, 182, 212, 0.15);
      padding: 2.25rem;
    }

    .login-header {
      text-align: center;
      margin-bottom: 2rem;

      .brand-icon {
        font-size: 3rem;
        color: #06b6d4;
        margin-bottom: 0.5rem;
      }

      h1 {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        color: #ffffff;
      }

      p {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-top: 0.25rem;
      }
    }

    .error-banner {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(239, 68, 68, 0.4);
      color: #fca5a5;
      padding: 0.65rem 0.85rem;
      border-radius: 6px;
      font-size: 0.82rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1.25rem;
    }

    .login-form {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;

      label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #9ca3af;
      }

      .input-container {
        position: relative;
        display: flex;
        align-items: center;

        .field-icon {
          position: absolute;
          left: 0.75rem;
          color: #6b7280;
          font-size: 1.15rem;
        }

        input {
          width: 100%;
          background: #1f2937;
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding: 0.65rem 0.75rem 0.65rem 2.5rem;
          color: #ffffff;
          font-size: 0.9rem;

          &:focus {
            outline: none;
            border-color: #06b6d4;
            box-shadow: 0 0 8px rgba(6, 182, 212, 0.3);
          }
        }
      }
    }

    .full-width {
      width: 100%;
      justify-content: center;
      padding: 0.75rem;
      margin-top: 0.5rem;
    }

    .demo-credentials {
      margin-top: 1.75rem;
      padding-top: 1rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 0.75rem;
      color: #6b7280;
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;

      code {
        color: #06b6d4;
        font-family: 'JetBrains Mono', monospace;
      }
    }
  `]
})
export class LoginComponent implements OnInit {
  username = 'admin';
  password = 'Admin@12345';
  errorMessage = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
    }
  }

  onSubmit(): void {
    if (!this.username || !this.password) {
      this.errorMessage = 'Please enter both username and password';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.authService.login(this.username, this.password).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.error || 'Invalid administrator credentials';
      }
    });
  }
}
