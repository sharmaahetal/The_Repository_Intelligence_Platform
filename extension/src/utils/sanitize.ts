/**
 * XSS prevention utilities for safely rendering untrusted text from backend responses or DOM.
 */
export function escapeHTML(str: string): string {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function sanitizeText(text: string): string {
  if (!text) return '';
  // Strip control characters and escape HTML entities
  return escapeHTML(text.replace(/[\x00-\x1F\x7F-\x9F]/g, ''));
}
