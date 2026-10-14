import { Component, DestroyRef, OnInit, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, Subscription, debounceTime, distinctUntilChanged } from 'rxjs';
import { ApiService } from '../../core/services/api.service';
import { ActivityLog } from '../../models/activity.model';

@Component({
  selector: 'app-activity-logs',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="activities-page">
      <div class="page-header">
        <div>
          <h2>Ingested Activity Logs</h2>
          <p>Audit user login events, file transfers, and system usage patterns</p>
        </div>
      </div>

      <!-- Filters Card -->
      <div class="cyber-card filters-card">
        <div class="filter-group">
          <label>Filter User ID</label>
          <input
            type="text"
            [(ngModel)]="filterUserId"
            (ngModelChange)="userIdInput$.next($event)"
            placeholder="e.g. EMP-1013"
          />
        </div>

        <div class="filter-group">
          <label>Event Type</label>
          <select [(ngModel)]="filterEventType" (change)="onFilterChange()">
            <option value="All">All Event Types</option>
            <option value="LOGIN">LOGIN</option>
            <option value="LOGOUT">LOGOUT</option>
            <option value="FILE_ACCESS">FILE_ACCESS</option>
            <option value="FILE_DOWNLOAD">FILE_DOWNLOAD</option>
            <option value="FILE_UPLOAD">FILE_UPLOAD</option>
            <option value="APP_USAGE">APP_USAGE</option>
          </select>
        </div>

        <div class="filter-group checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" [(ngModel)]="filterAfterHours" (change)="onFilterChange()" />
            <span>After-Hours Only</span>
          </label>
        </div>
      </div>

      <!-- Table Card -->
      <div class="cyber-card table-card">
        <div class="cyber-table-container">
          <table class="cyber-table">
            <thead>
              <tr>
                <th>Activity ID</th>
                <th>Timestamp</th>
                <th>User ID</th>
                <th>Event Type</th>
                <th>Location / IP</th>
                <th>Device ID</th>
                <th>File / Download Metrics</th>
                <th>After Hours</th>
                <th>Failed Logins</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let act of activities">
                <td><code>{{ act.activity_id }}</code></td>
                <td>{{ act.timestamp | date:'medium' }}</td>
                <td><code>{{ act.user_id }}</code></td>
                <td><span class="event-badge">{{ act.event_type }}</span></td>
                <td>{{ act.location_name }} ({{ act.location_ip }})</td>
                <td><code>{{ act.device_id }}</code></td>
                <td>
                  <div *ngIf="act.file_details?.filename">
                    <strong>{{ act.file_details.filename }}</strong>
                    <div class="sub-detail">
                      {{ act.file_details.download_size_mb }} MB DL / {{ act.file_details.upload_size_mb }} MB UL
                    </div>
                  </div>
                  <div *ngIf="!act.file_details?.filename">{{ act.app_used }}</div>
                </td>
                <td>
                  <span class="pill" [class.yes]="act.after_hours">{{ act.after_hours ? 'YES' : 'NO' }}</span>
                </td>
                <td>
                  <span [class.alert-text]="act.failed_logins > 0">{{ act.failed_logins }}</span>
                </td>
              </tr>
              <tr *ngIf="activities.length === 0">
                <td colspan="9" class="empty-cell">No activity logs found.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Controls -->
        <div class="pagination-bar" *ngIf="total > 0">
          <span class="page-info">Showing page {{ currentPage }} of {{ totalPages }} ({{ total }} total logs)</span>
          <div class="btn-group">
            <button class="btn-cyber secondary btn-sm" [disabled]="currentPage === 1" (click)="changePage(-1)">Previous</button>
            <button class="btn-cyber secondary btn-sm" [disabled]="currentPage >= totalPages" (click)="changePage(1)">Next</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .activities-page {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .page-header {
      h2 { font-size: 1.5rem; font-weight: 800; color: #ffffff; }
      p { font-size: 0.85rem; color: #9ca3af; }
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

        label { font-size: 0.78rem; font-weight: 600; color: #9ca3af; }

        input, select {
          background: #1f2937;
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #ffffff;
          padding: 0.55rem 0.85rem;
          border-radius: 8px;
          font-size: 0.85rem;
          outline: none;
          &:focus { border-color: #06b6d4; }
        }
      }

      .checkbox-group {
        justify-content: center;

        .checkbox-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: #f9fafb;
          cursor: pointer;
        }
      }
    }

    .event-badge {
      background: rgba(6, 182, 212, 0.12);
      color: #06b6d4;
      border: 1px solid rgba(6, 182, 212, 0.3);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .sub-detail { font-size: 0.72rem; color: #9ca3af; }

    .pill {
      font-size: 0.72rem;
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      background: #1f2937;
      color: #9ca3af;
      &.yes { background: rgba(239, 68, 68, 0.2); color: #fca5a5; }
    }

    .alert-text { color: #ef4444; font-weight: 700; }

    .pagination-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 1rem;
      padding-top: 1rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);

      .page-info { font-size: 0.8rem; color: #9ca3af; }
      .btn-group { display: flex; gap: 0.5rem; }
    }

    .btn-sm { padding: 0.3rem 0.65rem; font-size: 0.75rem; }
    .empty-cell { text-align: center; color: #6b7280; padding: 2rem; }
  `]
})
export class ActivityLogsComponent implements OnInit {
  private destroyRef = inject(DestroyRef);
  userIdInput$ = new Subject<string>();
  private fetchSub?: Subscription;
  activities: ActivityLog[] = [];
  filterUserId = '';
  filterEventType = 'All';
  filterAfterHours = false;

  currentPage = 1;
  pageSize = 50;
  total = 0;
  totalPages = 1;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.fetchLogs();
    this.userIdInput$
      .pipe(debounceTime(350), distinctUntilChanged(), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.onFilterChange());
    this.apiService.dataRefresh$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => this.fetchLogs());
  }

  fetchLogs(): void {
    this.fetchSub?.unsubscribe();
    this.fetchSub = this.apiService.getActivities(
      this.filterUserId.trim(),
      this.filterEventType,
      this.filterAfterHours,
      this.currentPage,
      this.pageSize
    ).subscribe(res => {
      this.activities = res.activities;
      this.total = res.total;
      this.totalPages = Math.max(1, res.pages);
    });
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.fetchLogs();
  }

  changePage(delta: number): void {
    const next = this.currentPage + delta;
    if (next < 1 || next > this.totalPages) return;
    this.currentPage = next;
    this.fetchLogs();
  }
}
