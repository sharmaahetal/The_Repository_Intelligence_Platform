import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { ForecastCard } from '../features/prediction/ForecastCard';
import { useForecastStore } from '../state/useForecastStore';
import { GitHubNavigationObserver, RepositoryContext } from './context';
import '../styles/tokens.css';

console.log('[RIP Extension] Content Script initialized.');

interface ForecastContainerProps {
  context: RepositoryContext;
}

const ForecastContainer: React.FC<ForecastContainerProps> = ({ context }) => {
  const setRepo = useForecastStore((s) => s.setRepo);

  useEffect(() => {
    setRepo(context.owner, context.repo);
  }, [context.owner, context.repo, setRepo]);

  return <ForecastCard />;
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
