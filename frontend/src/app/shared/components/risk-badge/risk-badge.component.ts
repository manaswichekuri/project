import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-risk-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="risk-badge" [ngClass]="category?.toLowerCase() || 'low'">
      <span class="material-icons-outlined badge-icon" *ngIf="showIcon">{{ getIcon() }}</span>
      <span>{{ category || 'Low' }}</span>
      <span *ngIf="score !== undefined">({{ score }})</span>
    </span>
  `,
  styles: [`
    .badge-icon {
      font-size: 0.85rem !important;
    }
  `]
})
export class RiskBadgeComponent {
  @Input() category: 'Low' | 'Medium' | 'High' | 'Critical' | string = 'Low';
  @Input() score?: number;
  @Input() showIcon: boolean = true;

  getIcon(): string {
    switch (this.category?.toLowerCase()) {
      case 'critical': return 'gpp_maybe';
      case 'high': return 'warning';
      case 'medium': return 'report_problem';
      default: return 'verified_user';
    }
  }
}
