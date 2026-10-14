import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

const TOKEN_KEY = 'soc_token';
const USER_KEY = 'soc_user';

export interface AdminUser {
  username: string;
  name: string;
  role: string;
  email: string;
}

interface LoginResponse {
  message: string;
  token: string;
  user: AdminUser;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl = `${environment.apiBaseUrl}/auth`;
  private currentUserSubject = new BehaviorSubject<AdminUser | null>(this.getStoredUser());
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/login`, { username, password }).pipe(
      tap(res => {
        if (res && res.token) {
          localStorage.setItem(TOKEN_KEY, res.token);
          localStorage.setItem(USER_KEY, JSON.stringify(res.user));
          this.currentUserSubject.next(res.user);
        }
      })
    );
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.currentUserSubject.next(null);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;
    const exp = this.getTokenExpiry(token);
    return exp === null || exp * 1000 > Date.now();
  }

  getCurrentUser(): AdminUser | null {
    return this.currentUserSubject.value;
  }

  /** Reads the `exp` claim (seconds since epoch) from a JWT without verifying it. */
  private getTokenExpiry(token: string): number | null {
    try {
      const payload = token.split('.')[1];
      const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
      const exp = JSON.parse(json)['exp'];
      return typeof exp === 'number' ? exp : null;
    } catch {
      // Not a decodable JWT (e.g. a token from an older build): treat as expired
      return 0;
    }
  }

  private getStoredUser(): AdminUser | null {
    const userStr = localStorage.getItem(USER_KEY);
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  }
}
