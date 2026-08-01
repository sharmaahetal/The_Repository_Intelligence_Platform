declare const browser: any;

/**
 * Cross-browser extension API adapter supporting Chrome, Firefox (browser.*), and Edge.
 */
export interface BrowserAPI {
  runtime: typeof chrome.runtime;
  storage: typeof chrome.storage;
}

export function getBrowserAPI(): BrowserAPI {
  if (typeof chrome !== 'undefined' && chrome.runtime) {
    return {
      runtime: chrome.runtime,
      storage: chrome.storage,
    };
  }
  if (typeof browser !== 'undefined' && browser.runtime) {
    return {
      runtime: browser.runtime,
      storage: browser.storage,
    };
  }
  throw new Error('No compatible WebExtension API runtime environment found.');
}
