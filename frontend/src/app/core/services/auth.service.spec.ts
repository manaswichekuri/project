import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth.service';

function fakeJwt(exp: number): string {
  const b64 = (o: object) => btoa(JSON.stringify(o)).replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');
  return `${b64({ alg: 'HS256', typ: 'JWT' })}.${b64({ sub: 'admin', exp })}.signature`;
}

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(AuthService);
  });

  afterEach(() => localStorage.clear());

  it('is not authenticated without a token', () => {
    expect(service.isAuthenticated()).toBeFalse();
  });

  it('accepts an unexpired JWT', () => {
    localStorage.setItem('soc_token', fakeJwt(Math.floor(Date.now() / 1000) + 3600));
    expect(service.isAuthenticated()).toBeTrue();
  });

  it('rejects an expired JWT', () => {
    localStorage.setItem('soc_token', fakeJwt(Math.floor(Date.now() / 1000) - 10));
    expect(service.isAuthenticated()).toBeFalse();
  });

  it('rejects a legacy non-JWT demo token', () => {
    localStorage.setItem('soc_token', 'demo-jwt-token-for-admin');
    expect(service.isAuthenticated()).toBeFalse();
  });
});
