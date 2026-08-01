export interface RepositoryContext {
  owner: string;
  repo: string;
  branch?: string;
  pageType: 'overview' | 'issues' | 'pulls' | 'code' | 'other';
}

export type NavigationCallback = (context: RepositoryContext) => void;

export class GitHubNavigationObserver {
  private lastPath: string = '';

  constructor(private onRepoDetected: NavigationCallback) {}

  public start(): void {
    this.checkCurrentPath();

    // Listen to GitHub SPA navigation events
    document.addEventListener('turbo:load', () => this.checkCurrentPath());
    document.addEventListener('pjax:complete', () => this.checkCurrentPath());
    document.addEventListener('turbo:render', () => this.checkCurrentPath());

    const observer = new MutationObserver(() => {
      if (location.pathname !== this.lastPath) {
        this.checkCurrentPath();
      }
    });

    if (document.body) {
      observer.observe(document.body, { childList: true, subtree: true });
    }
  }

  private checkCurrentPath(): void {
    const currentPath = location.pathname;
    if (currentPath === this.lastPath) return;

    this.lastPath = currentPath;
    const context = this.parseRepositoryContext(currentPath);

    if (context) {
      this.onRepoDetected(context);
    }
  }

  public parseRepositoryContext(path: string): RepositoryContext | null {
    const segments = path.split('/').filter(Boolean);
    if (segments.length < 2) return null;

    const reserved = [
      'settings', 'orgs', 'notifications', 'explore', 'marketplace',
      'pulls', 'issues', 'discussions', 'search', 'features', 'topics',
    ];

    if (reserved.includes(segments[0])) return null;

    const owner = segments[0];
    const repo = segments[1];

    let pageType: RepositoryContext['pageType'] = 'overview';
    if (segments.length > 2) {
      const sub = segments[2];
      if (sub === 'issues') pageType = 'issues';
      else if (sub === 'pulls') pageType = 'pulls';
      else if (sub === 'tree' || sub === 'blob') pageType = 'code';
      else pageType = 'other';
    }

    return { owner, repo, pageType };
  }
}
