import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { User } from '../../models/user.model';
import { RiskBadgeComponent } from '../../shared/components/risk-badge/risk-badge.component';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, RiskBadgeComponent],
  template: `
    <div class="users-page">
      <div class="page-header">
        <div>
          <h2>Monitored Employee Profiles</h2>
          <p>Inspect employee baseline metrics, risk levels, and behavioral status</p>
        </div>
      </div>

      <!-- Filters Row -->
      <div class="cyber-card filters-card">
        <div class="filter-group search-group">
          <label>Search User</label>
          <div class="input-container">
            <span class="material-icons-outlined search-icon">search</span>
            <input
              type="text"
              [(ngModel)]="searchQuery"
              (ngModelChange)="onFilterChange()"
              placeholder="Search by name, ID, or role..."
            />
          </div>
        </div>

        <div class="filter-group">
          <label>Department</label>
          <select [(ngModel)]="selectedDepartment" (change)="onFilterChange()">
            <option value="All">All Departments</option>
            <option value="Finance">Finance</option>
            <option value="Engineering">Engineering</option>
            <option value="Human Resources">Human Resources</option>
            <option value="Sales">Sales</option>
            <option value="IT Support">IT Support</option>
            <option value="Executive">Executive</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Risk Level</label>
          <select [(ngModel)]="selectedRiskCategory" (change)="onFilterChange()">
            <option value="All">All Risk Levels</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </div>

      <!-- Users Table -->
      <div class="cyber-card table-card">
        <div class="cyber-table-container">
          <table class="cyber-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Employee Name</th>
                <th>Department</th>
                <th>Role</th>
                <th>Baseline Location</th>
                <th>Risk Score</th>
                <th>Risk Category</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let user of users">
                <td><code>{{ user.user_id }}</code></td>
                <td><strong>{{ user.name }}</strong></td>
                <td>{{ user.department }}</td>
                <td>{{ user.role }}</td>
                <td>{{ user.baseline_location }}</td>
                <td>
                  <span class="score-num" [ngClass]="user.risk_category?.toLowerCase() || 'low'">
                    {{ user.current_risk_score }}
                  </span>
                </td>
                <td>
                  <app-risk-badge [category]="user.risk_category || 'Low'"></app-risk-badge>
                </td>
                <td>
                  <a [routerLink]="['/users', user.user_id]" class="btn-cyber primary btn-sm">
                    View Profile
                  </a>
                </td>
              </tr>
              <tr *ngIf="users.length === 0">
                <td colspan="8" class="empty-cell">No monitored users match the selected filters.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .users-page {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .page-header {
      h2 {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
      }
      p {
        font-size: 0.85rem;
        color: #9ca3af;
      }
    }

    .filters-card {
      display: flex;
      gap: 1.25rem;
      align-items: flex-end;
      flex-wrap: wrap;

      .filter-group {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;

        label {
          font-size: 0.78rem;
          font-weight: 600;
          color: #9ca3af;
        }

        select {
          background: #1f2937;
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #ffffff;
          padding: 0.55rem 0.85rem;
          border-radius: 8px;
          font-size: 0.85rem;
          min-width: 160px;
          outline: none;

          &:focus { border-color: #06b6d4; }
        }
      }

      .search-group {
        flex: 1;
        min-width: 240px;

        .input-container {
          position: relative;
          display: flex;
          align-items: center;

          .search-icon {
            position: absolute;
            left: 0.75rem;
            color: #6b7280;
            font-size: 1.1rem;
          }

          input {
            width: 100%;
            background: #1f2937;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 0.55rem 0.85rem 0.55rem 2.4rem;
            color: #ffffff;
            font-size: 0.85rem;

            &:focus { outline: none; border-color: #06b6d4; }
          }
        }
      }
    }

    .score-num {
      font-weight: 800;
      font-size: 0.95rem;

      &.critical { color: #ef4444; }
      &.high { color: #f97316; }
      &.medium { color: #f59e0b; }
      &.low { color: #10b981; }
    }

    .btn-sm {
      padding: 0.3rem 0.65rem;
      font-size: 0.75rem;
    }

    .empty-cell {
      text-align: center;
      color: #6b7280;
      padding: 2rem;
    }
  `]
})
export class UsersComponent implements OnInit {
  users: User[] = [];
  searchQuery = '';
  selectedDepartment = 'All';
  selectedRiskCategory = 'All';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.fetchUsers();
    this.apiService.dataRefresh$.subscribe(() => {
      this.fetchUsers();
    });
  }

  fetchUsers(): void {
    this.apiService.getUsers(this.searchQuery, this.selectedDepartment, this.selectedRiskCategory)
      .subscribe(res => this.users = res.users);
  }

  onFilterChange(): void {
    this.fetchUsers();
  }
}
