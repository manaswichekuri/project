import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';
import { environment } from '../../../environments/environment';

/** Attaches the JWT to API calls, logs out on 401 and surfaces other API errors as a toast. */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const notifications = inject(NotificationService);
  const router = inject(Router);

  const isApiCall = req.url.startsWith(environment.apiBaseUrl);
  const isLogin = req.url.endsWith('/auth/login');
  const token = authService.getToken();

  if (isApiCall && token && !isLogin) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }

  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      if (isApiCall && !isLogin) {
        if (err.status === 401) {
          authService.logout();
          notifications.error('Your session has expired. Please sign in again.');
          router.navigate(['/login']);
        } else if (err.status === 0) {
          notifications.error('Cannot reach the API server. Check that the backend is running.');
        } else {
          notifications.error(err.error?.error || `Request failed (${err.status})`);
        }
      }
      return throwError(() => err);
    })
  );
};
