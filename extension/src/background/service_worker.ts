import { RepositoryForecastApi } from '../api/client';
import { MessagingService } from '../messaging/service';
import { ForecastPayload } from '../messaging/types';
import { RepositoryNarrativeEngine } from '../services/narrative';
import { StorageService } from '../storage/service';

console.log('[RIP Extension] Background Service Worker initialized.');

const api = new RepositoryForecastApi();
const storage = new StorageService(15); // 15 min TTL
const narrativeEngine = new RepositoryNarrativeEngine();
const messaging = new MessagingService();

messaging.onMessage(async (message) => {
  if (message.action === 'FETCH_FORECAST') {
    const payload = (message.payload || {}) as { owner?: string; repo?: string; horizon?: number };
    const { owner, repo, horizon } = payload;
    if (!owner || !repo) {
      throw new Error('Invalid request payload: owner and repo are required.');
    }

    const h = horizon || 180;

    // 1. Check local storage cache
    const cachedData = await storage.getCachedForecast<ForecastPayload>(owner, repo, h);
    if (cachedData) {
      return { ...cachedData, cached: true };
    }

    // 2. Fetch from backend API
    const liveData = await api.getForecast(owner, repo, h);

    // 3. Enrich with narrative summary if missing
    if (!liveData.narrative_summary) {
      liveData.narrative_summary = narrativeEngine.generateNarrative(liveData);
    }

    // 4. Store in cache
    await storage.setCachedForecast(owner, repo, h, liveData);

    return liveData;
  }

  if (message.action === 'CLEAR_CACHE') {
    await storage.clearCache();
    return { success: true };
  }

  throw new Error(`Unknown message action: ${message.action}`);
});
