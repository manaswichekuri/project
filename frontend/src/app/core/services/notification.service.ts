import { Injectable, signal } from '@angular/core';

export interface Notification {
  type: 'error' | 'success';
  text: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  readonly notification = signal<Notification | null>(null);
  private timer?: ReturnType<typeof setTimeout>;

  error(text: string): void {
    this.show({ type: 'error', text });
  }

  success(text: string): void {
    this.show({ type: 'success', text });
  }

  dismiss(): void {
    this.notification.set(null);
  }

  private show(notification: Notification): void {
    this.notification.set(notification);
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.dismiss(), 6000);
  }
}
