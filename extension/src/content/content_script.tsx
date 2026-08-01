import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { ForecastCard } from '../components/ForecastCard';
import { MessagingService } from '../messaging/service';
import { ForecastPayload } from '../messaging/types';
import { GitHubNavigationObserver, RepositoryContext } from './context';

console.log('[RIP Extension] Thin Content Script loaded.');

const messaging = new MessagingService();

interface ForecastContainerProps {
  context: RepositoryContext;
}

const ForecastContainer: React.FC<ForecastContainerProps> = ({ context }) => {
  const [payload, setPayload] = useState<ForecastPayload | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await messaging.sendMessage<{ owner: string; repo: string; horizon: number }, ForecastPayload>(
        'FETCH_FORECAST',
        { owner: context.owner, repo: context.repo, horizon: 180 }
      );
      setPayload(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch repository forecast');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [context.owner, context.repo]);

  return (
    <ForecastCard
      payload={payload}
      loading={loading}
      error={error}
      onRetry={fetchForecast}
    />
  );
};

let reactRoot: ReactDOM.Root | null = null;

function mountOverlay(context: RepositoryContext) {
  let rootElement = document.getElementById('rip-forecast-root');
  if (!rootElement) {
    rootElement = document.createElement('div');
    rootElement.id = 'rip-forecast-root';

    const sidebar = document.querySelector('.Layout-sidebar') || document.querySelector('#repository-details-container');
    if (sidebar) {
      sidebar.prepend(rootElement);
    } else {
      const main = document.querySelector('main');
      if (main) {
        main.prepend(rootElement);
      } else {
        document.body.appendChild(rootElement);
      }
    }
  }

  if (!reactRoot) {
    reactRoot = ReactDOM.createRoot(rootElement);
  }

  reactRoot.render(<ForecastContainer context={context} />);
}

const observer = new GitHubNavigationObserver((context) => {
  console.log('[RIP Extension] Navigation shift detected:', context);
  mountOverlay(context);
});

observer.start();
