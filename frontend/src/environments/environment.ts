// The API is always reached through a same-origin `/api` path:
// nginx proxies it in production (see nginx.conf), and `ng serve` proxies it in development (see proxy.conf.json).
export const environment = {
  apiBaseUrl: '/api/v1'
};
