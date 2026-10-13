# Shayara — Collected Writings

A quiet reading room for nine poems and reflections by Shayara (Kalyani Dhusia), hosted on GitHub Pages.

## Current content status

- The full text of **Do Neem (The Split)** is already in `data/do-neem.json` from the supplied HTML.
- The other eight articles load from the original WordPress public API when internet access and cross-origin policy allow. They are **not yet locally copied** in this download, because the current execution environment could not retrieve their full source bodies.
- For full independence, run `python3 scripts/snapshot.py` on your internet-connected laptop. It creates all nine `data/*.json` files. Inspect them, then commit the `data` directory.

## Publish under `https://kalyanidhusia.github.io/`

Option 1: publish this folder as `/writings/` inside the repository `kalyanidhusia/kalyanidhusia.github.io`. The site appears at `https://kalyanidhusia.github.io/writings/`. Copy the `index.html`, `posts.json`, `data`, `scripts`, and optional `media` folder into `writings/`.

Option 2: make these files the root of your `kalyanidhusia.github.io` repository if you want the writings to replace the entire homepage. Take a backup first.

Then go to repository Settings → Pages and ensure Pages deploys from your intended branch/folder (or your existing deployment workflow).

## Local preview

From this folder run:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000`. Opening the HTML with a `file://` URL will not work because it loads local JSON via `fetch`.

## Music and images

Original image, audio, and video elements embedded in a WordPress post are carried into each article's body when snapshotting. The page deliberately does **not** autoplay music. If you want local music tracks, place properly licensed audio in `media/` and add a user-operated HTML audio player. Existing embedded images may still point to WordPress; download images and update URLs if you want full media independence.

## Maintenance

`posts.json` controls the tabs. Each entry points to its original WordPress URL. The fallback loader uses WordPress APIs if the corresponding `data/{id}.json` is missing. Avoid changing the `id` for a published post, since it also determines permanent direct links (`#id`).
