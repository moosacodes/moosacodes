# Setup

1. Upload the **contents** of this folder into `moosacodes/moosacodes` (not a nested folder). Keep `.github/workflows/update-profile.yml` exactly where it is.
2. Under **Settings → Actions → General → Workflow permissions**, enable **Read and write permissions** if your repository permits it, then save. The workflow needs permission to commit generated images.
3. Visit **Actions → Refresh avatar and profile → Run workflow**. Check the run logs for success.
4. The workflow checks the GitHub avatar every day and regenerates both themes. Changing your profile picture on GitHub is enough; no manual image upload to this repo.

Note: Scheduled Actions may run late. GitHub's rendered image cache can take additional time to refresh. SVG animations can behave differently across clients; reduced-motion settings disable animation. No external SVG generator hosting or personal access token is required for public profile data.

To adjust ASCII resolution, characters, colors, or text, modify `scripts/render.py` and push. That push regenerates the assets automatically.

This design draws inspiration from Andrew6rant's text-based SVG layout; all generator code and UI layout here are newly written.
