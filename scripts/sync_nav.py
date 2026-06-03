from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MKDOCS_YML = ROOT / "mkdocs.yml"

SECTION_ORDER = [
    "1.入门部分",
    "2.基础开发",
    "3.高阶开发",
    "4.战斗场景开发",
    "5.Overworld开发",
    "6.翻译与本地化",
    "Lua教程速通",
    "打包与发布",
    "报错处理",
]

SECTION_LABELS = {
    "zh": {
        "1.入门部分": "入门部分",
        "2.基础开发": "基础开发",
        "3.高阶开发": "高阶开发",
        "4.战斗场景开发": "战斗场景开发",
        "5.Overworld开发": "Overworld开发",
        "6.翻译与本地化": "翻译与本地化",
        "Lua教程速通": "Lua教程速通",
        "打包与发布": "打包与发布",
        "报错处理": "报错处理",
    },
    "en": {
        "1.入门部分": "Getting Started",
        "2.基础开发": "Basic Development",
        "3.高阶开发": "Advanced Development",
        "4.战斗场景开发": "Battle Scene Development",
        "5.Overworld开发": "Overworld Development",
        "6.翻译与本地化": "Translation and Localization",
        "Lua教程速通": "Lua Quick Start",
        "打包与发布": "Packaging and Release",
        "报错处理": "Error Handling",
    },
}


def read_h1(path: Path) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return path.stem


def build_nav_for_language(locale: str) -> list[dict[str, object]]:
    docs_root = ROOT / "docs" / locale
    nav: list[dict[str, object]] = [{"首页": "index.md"}]

    for section in SECTION_ORDER:
        section_dir = docs_root / section
        if not section_dir.exists():
            continue

        items: list[dict[str, str]] = []
        for md_path in sorted(section_dir.glob("*.md"), key=lambda p: p.name):
            items.append({read_h1(md_path): f"{section}/{md_path.name}"})

        section_label = SECTION_LABELS.get(locale, {}).get(section, section)
        nav.append({section_label: items})

    return nav


def main() -> None:
    data = yaml.safe_load(MKDOCS_YML.read_text(encoding="utf-8"))
    plugin = next(item for item in data["plugins"] if "i18n" in item)["i18n"]
    for lang_cfg in plugin["languages"]:
        locale = lang_cfg["locale"]
        lang_cfg["nav"] = build_nav_for_language(locale)
    MKDOCS_YML.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
