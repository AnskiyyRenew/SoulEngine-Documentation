# SoulEngine Documentation

Bilingual (English / Simplified Chinese) docs site built with **MkDocs + Material for MkDocs**.

## Current state (read this first)

**`zh_CN` is the authored, complete copy and remains the source of truth.** `en` is now
**fully translated** — all 12 section `index.md` landing pages and 56 subpages have been
mirrored from `zh_CN` under the same relative paths. The i18n plugin is configured so the
site builds for both languages.

```
docs/
├─ zh_CN/                  # 简体中文 —— the authored, complete copy
│  ├─ index.md
│  ├─ 000_before/          # .pages + index.md + 000_download.md / 010_getready.md / 020_lua.md
│  ├─ 010_quick_start/     # .pages + index.md + 000_conf.md / 010_scene.md / 020_sprites.md
│  ├─ 020_basic/
│  ├─ 030_battle_system/
│  ├─ 040_overworld/
│  ├─ 050_intermediate/
│  ├─ 060_with_love/
│  ├─ 070_develop/
│  ├─ 080_l10n/
│  ├─ 090_network/
│  ├─ 100_export/
│  └─ img/                 # page screenshots
├─ en/                     # English —— full mirror of zh_CN (12 index.md + 56 subpages)
│  ├─ index.md
│  ├─ 000_before/ … 100_export/   # same 11 section folders (+ .pages + subpages)
│  └─ img/
├─ background/             # shared background images (light / dark)
└─ css/custom.css
```

Rules:

- Every section folder under `docs/zh_CN/` carries its own `.pages` (display name) and
  `index.md` (section landing page). `docs/en/` mirrors the same layout — every section
  folder carries its own `.pages` and `index.md`, plus the translated subpages.
- **No `nav:` in [`mkdocs.yml`](mkdocs.yml)** — the sidebar is auto-detected from the
  directory structure of each language.
- `docs/zh_CN/` is the source of truth. When a page is added, add it there first.

## Defining folder display names

The sidebar section title is **not** the folder name. It comes from a `.pages` file
inside each section folder (handled by the `awesome-pages` plugin) — one line, `title:`:

```yaml
# docs/zh_CN/010_quick_start/.pages
title: 快速上手
```

```yaml
# docs/zh_CN/030_battle_system/.pages
title: 战斗系统
```

**Naming convention:**

- Folder names are language-neutral slugs with an ordering prefix: `NNN_english_slug`
  (`000_before`, `010_quick_start`, `020_basic`, … `100_export`). The prefix controls the
  sidebar order (natural filename sort) and is never displayed — only the `.pages` `title` is.
- Page files use the same idea: `NNN_slug.md` inside a section.
- Each folder also has an `index.md` (section landing page). Material's
  `navigation.indexes` makes the whole section clickable to that page.
- Adding a language later is just a matter of adding a `locale` block in
  [`mkdocs.yml`](mkdocs.yml) and creating the matching folder.

## How i18n works

- **`mkdocs-static-i18n`** (`docs_structure: folder`) rebuilds the site once per language
  and writes each language under its own URL prefix.
- **`theme.language: zh`** override for the `zh_CN` locale: Material has no `zh_CN`
  translation key (it ships `zh`, `zh-Hant`, `zh-TW`), so the folder is `zh_CN` but the
  Material UI language is set to `zh` for Chinese UI strings.
- **Search** is configured with `search.lang: [zh, en]` so Chinese text is tokenized
  correctly (jieba is loaded at build time).
- **`hooks.py`** removes the redundant top-level language wrapper (e.g. `zh CN`) that
  leaks into the auto nav for underscore locales like `zh_CN`. It reads the language list
  from the `i18n` plugin config, so no manual maintenance is needed.

## 写文档要求（导航自动适配）

只要按下面规则新建/修改文件，侧边栏会在下次 `mkdocs serve` / `mkdocs build` 时自动更新，**无需**改任何配置文件。

### 1. 位置
- **中文写在 `docs/zh_CN/` 下**，是 source of truth（英文与其它语言均从这里镜像）。
- 英文侧 `docs/en/` 已**完整翻译**，与 `docs/zh_CN/` 同相对路径（ `docs/zh_CN/foo/bar.md` ↔ `docs/en/foo/bar.md` ）。
- 现在想加英文页面也可以，但请**先加中文**，否则中英会不一致。

### 2. 章节文件夹
- 文件夹名用 `NNN_english_slug`（如 `000_before`、`010_quick_start`、`030_battle_system`）：数字控制侧边栏顺序，文件夹名本身**不会**显示。
- 每个章节文件夹必须包含：
  - `.pages` —— 定义侧边栏显示名（**只有一行**，注意别少写冒号后的空格）：
    ```yaml
    title: 快速上手
    ```
  - `index.md` —— 章节落地页（标题即章节页标题）。
  - 其他 `.md` —— 子页面，同样带 `NNN_` 前缀（按文件名自然排序）。

### 3. 页面显示名
- 页面标题取 markdown 的第一个 `# H1`；想自定义就用 front matter：
  ```markdown
  ---
  title: 我的页面名
  ---
  # 正文大标题
  ```

### 4. 顶层页面与首页
- 不在任何章节文件夹里的 `.md`（如 `docs/en/xxx.md`）会成为顶层导航项。
- 首页固定为 `docs/{lang}/index.md`。

### 5. 禁止事项
- 不要在 `docs/` 根目录放 `index.md`（会与 `en/index.md` 冲突导致构建报错）。
- 不要改 `mkdocs.yml` 里的导航（本来就没有 `nav:`，也没有可改的）。
- 新建章节文件夹务必带上 `.pages`，否则会显示难看的原始文件夹名（如 `030 battle system`）。

### 6. 新增语言
- 在 `mkdocs.yml` 的 `i18n.languages` 加一行（`locale` / `name` / `build`），并创建同名文件夹即可，导航与 `hooks.py` 会自动适配。

## Commands

```bash
mkdocs serve     # live preview
mkdocs build     # build to ./site
```
