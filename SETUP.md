# Moosa's terminal README

Animated terminal inspired by [x0rzavi/github-readme-terminal](https://github.com/x0rzavi/github-readme-terminal). This package recreates the visual idea in a self-contained Pillow renderer, rather than copying the original gifos source or requiring external image hosting.

## Install

1. Extract the ZIP into the **root** of your `moosacodes/moosacodes` GitHub profile repository. Preserve the folder structure.
2. Replace the existing `.github/workflows/update-profile.yml` with the included file, so it no longer regenerates the previous avatar-based SVG output.
3. Commit `README.md`, `assets/terminal.gif`, `scripts/terminal.py`, and `.github/workflows/update-profile.yml`.
4. Visit your GitHub profile. The included GIF displays immediately, without waiting for Actions.

## Update it

Edit `BIO` in `scripts/terminal.py` and push; the workflow automatically regenerates the GIF. You can also run `python -m pip install Pillow` then `python scripts/terminal.py` locally.

The old `assets/dark.svg`, `assets/light.svg`, `assets/portrait.txt`, and `scripts/render.py` can be removed *after* confirming the replacement displays, but deleting them is optional; the new README does not reference them.

This animation presents a curated profile, **not real-time contribution statistics**. There are no secrets or personal access tokens required.
