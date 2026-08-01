import { getBrowserAPI } from '../utils/browser';
import { ExtensionMessage, MessageAction } from './types';

export class MessagingService {
  /**
   * Send a typed message to the background service worker.
   */
  public async sendMessage<RequestPayload, ResponsePayload>(
    action: MessageAction,
    payload?: RequestPayload
  ): Promise<ResponsePayload> {
    const api = getBrowserAPI();
    const message: ExtensionMessage<RequestPayload> = { action, payload };

    return new Promise((resolve, reject) => {
      api.runtime.sendMessage(message, (response: ExtensionMessage<ResponsePayload>) => {
        const lastError = api.runtime.lastError;
        if (lastError) {
          return reject(new Error(lastError.message));
        }
        if (response && response.error) {
          return reject(new Error(response.error));
        }
        if (response && response.payload !== undefined) {
          return resolve(response.payload);
        }
        reject(new Error('Empty response received from background service worker.'));
      });
    });
  }

  /**
   * Listen for incoming messages from content scripts or popup.
   */
  public onMessage<RequestPayload, ResponsePayload>(
    handler: (message: ExtensionMessage<RequestPayload>) => Promise<ResponsePayload>
  ): void {
    const api = getBrowserAPI();
    api.runtime.onMessage.addListener((message: ExtensionMessage<RequestPayload>, _sender, sendResponse) => {
      handler(message)
        .then((payload) => sendResponse({ action: message.action, payload }))
        .catch((err) => sendResponse({ action: 'ERROR_RESPONSE', error: err.message }));
      return true; // Keep channel open for async response
    });
  }
}
