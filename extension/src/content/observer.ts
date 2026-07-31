export interface RepoContext {
  owner: string;
  repo: string;
}

export type NavigationCallback = (context: RepoContext) => void;

export class GitHubObserver {
  private lastPath: string = '';

  constructor(private onRepoDetected: NavigationCallback) {}

  public start(): void {
    this.checkCurrentPath();

    // Observe SPA navigation events on github.com (pjax, turbo, soft-nav)
    document.addEventListener('turbo:load', () => this.checkCurrentPath());
    document.addEventListener('pjax:complete', () => this.checkCurrentPath());

    const observer = new MutationObserver(() => {
      if (location.pathname !== this.lastPath) {
        this.checkCurrentPath();
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  private checkCurrentPath(): void {
    const currentPath = location.pathname;
    if (currentPath === this.lastPath) return;

    this.lastPath = currentPath;
    const repoContext = this.parseGitHubRepo(currentPath);

    if (repoContext) {
      this.onRepoDetected(repoContext);
    }
  }

  private parseGitHubRepo(path: string): RepoContext | null {
    const segments = path.split('/').filter(Boolean);
    if (segments.length >= 2) {
      const reservedPrefixes = ['settings', 'orgs', 'notifications', 'explore', 'marketplace', 'pulls', 'issues'];
      if (!reservedPrefixes.includes(segments[0])) {
        return { owner: segments[0], repo: segments[1] };
      }
    }
    return null;
  }
}
