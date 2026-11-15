# the-trip-now-www

The website for **The Trip Now**, a travel community brand: https://thetripnow.com/

## What it is

A single static links page (`index.html`, no JavaScript, no build step). It points to:
- the poster store, https://shop.88eggs.com/store/the-trip-now;
- Instagram, [@thetripnow](https://www.instagram.com/thetripnow/);
- PTK Studio.

## How it is served

GitHub Pages serves the `main` branch from the repo root on the custom domain in `CNAME`. **A merge to `main` is a production deploy.** Pages runs Jekyll here, and `_config.yml` excludes internal files (`mochi-agent/proposals/`, this README) from the published site. Anything new that should stay internal must be added to that `exclude` list.

To run it locally: `python3 -m http.server 8777`, then open http://localhost:8777/.

## Internal

- `mochi-agent/proposals/{pending,approved,rejected,completed}/`: plans for Thomas to decide on (see the ptk-studio handbook, "Proposals"). Not published.
- Project status and roles: `projects/thetripnow/` in `ptk-studio/ptk-studio`.
