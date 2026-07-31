import { GitHubObserver, RepoContext } from './observer';

console.log('[RIP Extension] Content script injected on github.com');

function mountExtensionPanel(context: RepoContext) {
  let rootElement = document.getElementById('rip-forecast-root');
  if (!rootElement) {
    rootElement = document.createElement('div');
    rootElement.id = 'rip-forecast-root';
    
    // Attempt insertion in GitHub sidebar or main container
    const sidebar = document.querySelector('.Layout-sidebar') || document.querySelector('#repository-details-container');
    if (sidebar) {
      sidebar.prepend(rootElement);
    } else {
      document.body.appendChild(rootElement);
    }
  }

  rootElement.innerHTML = `
    <div style="background: rgba(13, 17, 23, 0.95); border: 1px solid rgba(48, 54, 61, 0.8); border-radius: 12px; padding: 16px; margin-bottom: 16px; color: #c9d1d9; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 600; color: #58a6ff; font-size: 14px;">⚡ Repository Intelligence Forecast</span>
        <span style="background: #238636; color: #fff; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 500;">Growing</span>
      </div>
      <div style="font-size: 13px; line-height: 1.5; color: #8b949e;">
        Analysing <strong style="color: #f0f6fc;">${context.owner}/${context.repo}</strong> over a <span style="color: #58a6ff;">180-day forecast horizon</span>.
      </div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 12px; text-align: center;">
        <div style="background: #161b22; padding: 8px; border-radius: 6px; border: 1px solid #21262d;">
          <div style="font-size: 10px; color: #8b949e;">Health Index</div>
          <div style="font-size: 16px; font-weight: 700; color: #3fb950;">88 / 100</div>
        </div>
        <div style="background: #161b22; padding: 8px; border-radius: 6px; border: 1px solid #21262d;">
          <div style="font-size: 10px; color: #8b949e;">Growth Prob</div>
          <div style="font-size: 16px; font-weight: 700; color: #58a6ff;">84%</div>
        </div>
        <div style="background: #161b22; padding: 8px; border-radius: 6px; border: 1px solid #21262d;">
          <div style="font-size: 10px; color: #8b949e;">Abandon Risk</div>
          <div style="font-size: 16px; font-weight: 700; color: #f85149;">6%</div>
        </div>
      </div>
    </div>
  `;
}

const observer = new GitHubObserver((context) => {
  console.log('[RIP Extension] Route shift detected:', context);
  mountExtensionPanel(context);
});

observer.start();
