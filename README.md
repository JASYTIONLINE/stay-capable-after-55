# Stay Capable After 55

Curated collection for CMPA 4301 Project 01.

**Topic:** Strength and conditioning for athletes who remain active after 55.

Published with **[Quartz 5](https://quartz.jzhao.xyz)** so Obsidian Markdown becomes a public HTML site on GitHub Pages.

## Layout

| Piece | Role |
|-------|------|
| `content/` | Obsidian vault (edit here) |
| `content/index.md` | Site landing page |
| `quartz.config.yaml` | Site title, baseUrl, plugins, ignore patterns |
| `.github/workflows/deploy.yml` | Build Quartz → deploy to GitHub Pages |

## Edit in Obsidian

1. Obsidian → **Open folder as vault**
2. Select `stay-capable-after-55/content/` (not the course repo root)
3. Edit notes. Wikilinks and folders work in Quartz.

Do not put private course spine files in `content/`. Templates live in `content/_templates/` and are ignored by Quartz.

## Local preview (HTML)

From `stay-capable-after-55/`:

```bash
npm ci
npx quartz plugin install --from-config
npx quartz build --serve
```

Open http://localhost:8080

## Publish to GitHub Pages

1. Create a **public** GitHub repo (e.g. `stay-capable-after-55`). Do not add a README on GitHub.
2. Point this folder’s `origin` at that repo and push `main`.
3. In `quartz.config.yaml`, set `baseUrl` to `YOURUSER.github.io/stay-capable-after-55` (no `https://`).
4. Repo **Settings → Pages → Source: GitHub Actions**.
5. Push again (or run the Deploy workflow). Site URL: `https://YOURUSER.github.io/stay-capable-after-55/`
6. Test the URL in a private/incognito window (no login).

After content edits:

```bash
git add content
git commit -m "Update collection notes"
git push
```

GitHub Actions rebuilds the HTML site.

## Course note

Working bibliography, annotation bank, and checklists live in the parent course repo (`r-4301-online-management`). Only reader-facing notes belong under `content/`.
