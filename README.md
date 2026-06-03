# SoulEngine Documentation

This repository uses Markdown as the source of truth.

- Edit documentation in `docs/`
- Keep the site output out of normal edits
- Open a PR for doc changes
- GitHub Actions builds the site and publishes it to GitHub Pages

## Local build

```bash
pip install -r requirements.txt
mkdocs serve
```

## Publish flow

1. Make changes in `docs/`
2. Open a pull request
3. Merge to the default branch
4. GitHub Actions deploys the static site to GitHub Pages
