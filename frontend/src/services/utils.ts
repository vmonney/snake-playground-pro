const TOKEN_KEY = 'snake_auth_token';

/**
 * Get the authentication token from localStorage
 */
export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Convert HTTP URL to WebSocket URL
 * http://localhost:3000 -> ws://localhost:3000
 * https://api.example.com -> wss://api.example.com
 */
export function getWebSocketUrl(httpUrl: string): string {
  return httpUrl.replace(/^http/, 'ws');
}

/**
 * Parse ISO date string to Date object
 */
export function parseDate(dateString: string): Date {
  return new Date(dateString);
}

/**
 * Convert Date object to ISO string for API
 */
export function formatDateForApi(date: Date): string {
  return date.toISOString();
}
