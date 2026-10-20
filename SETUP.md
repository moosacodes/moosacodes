# Terminal profile setup

This profile uses the upstream [`github-readme-terminal`](https://github.com/x0rzavi/github-readme-terminal) engine and follows its BIOS, login, `fetch.sh`, and system-information animation. The terminal is intentionally taller than the upstream default so the final system-information frame is not clipped.

## Local generation

Install FFmpeg and the renderer, then run:

```powershell
python -m pip install git+https://github.com/x0rzavi/github-readme-terminal.git@main
python main.py
```

The script reads the `GITHUB_TOKEN` environment variable to fetch live profile statistics and writes `output.gif` and `README.md`.

## Automated updates

`.github/workflows/update-profile.yml` regenerates the animation daily using the repository's automatic `GITHUB_TOKEN`, then commits only changed output files.
