import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-metric-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="cyber-card metric-card" [ngClass]="variant">
      <div class="header">
        <span class="title">{{ title }}</span>
        <span class="material-icons-outlined icon">{{ icon }}</span>
      </div>
      <div class="value-container">
        <span class="value">{{ value }}</span>
        <span class="subtitle" *ngIf="subtitle">{{ subtitle }}</span>
      </div>
    </div>
  `,
  styles: [`
    .metric-card {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.75rem;

      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .title {
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #9ca3af;
        }

        .icon {
          font-size: 1.4rem;
          color: #06b6d4;
        }
      }

      .value-container {
        display: flex;
        align-items: baseline;
        gap: 0.5rem;

        .value {
          font-size: 1.85rem;
          font-weight: 800;
          color: #f9fafb;
          letter-spacing: -0.02em;
        }

        .subtitle {
          font-size: 0.75rem;
          color: #6b7280;
        }
      }

      &.danger {
        border-color: rgba(239, 68, 68, 0.3);
        .icon { color: #ef4444; }
        .value { color: #fca5a5; }
      }

      &.warning {
        border-color: rgba(245, 158, 11, 0.3);
        .icon { color: #f59e0b; }
        .value { color: #fde047; }
      }

      &.success {
        border-color: rgba(16, 185, 129, 0.3);
        .icon { color: #10b981; }
        .value { color: #6ee7b7; }
      }
    }
  `]
})
export class MetricCardComponent {
  @Input() title: string = '';
  @Input() value: string | number = 0;
  @Input() icon: string = 'analytics';
  @Input() subtitle?: string;
  @Input() variant: 'default' | 'danger' | 'warning' | 'success' = 'default';
}
