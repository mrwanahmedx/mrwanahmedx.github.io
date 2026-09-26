from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
HTML_FILES = sorted(ROOT.glob("*.html"))

class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.empty_targets: list[tuple[str, str]] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id")
        if element_id:
            self.ids.append(element_id)

        for key in ("href", "src"):
            if key not in attrs:
                continue
            value = attrs.get(key)
            if value is None or not value.strip():
                self.empty_targets.append((tag, key))
            else:
                self.links.append((key, value))

def local_target(source: Path, raw: str) -> Path | None:
    if raw.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "#")):
        return None
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return source
    if path.startswith("/"):
        return ROOT / path.lstrip("/")
    return (source.parent / path).resolve()

errors: list[str] = []

for html in HTML_FILES:
    parser = LinkParser()
    parser.feed(html.read_text(encoding="utf-8"))

    for tag, kind in parser.empty_targets:
        errors.append(f"{html.name}: empty {kind} on <{tag}>")

    seen: set[str] = set()
    duplicates: set[str] = set()
    for element_id in parser.ids:
        if element_id in seen:
            duplicates.add(element_id)
        seen.add(element_id)
    for element_id in sorted(duplicates):
        errors.append(f"{html.name}: duplicate id: {element_id}")

    for kind, raw in parser.links:
        target = local_target(html, raw)
        if target is None:
            continue
        try:
            target.relative_to(ROOT)
        except ValueError:
            errors.append(f"{html.name}: {kind} escapes repository: {raw}")
            continue
        if not target.exists():
            errors.append(f"{html.name}: missing local {kind}: {raw}")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)

print(
    f"Validated {len(HTML_FILES)} HTML files with no missing/empty local "
    "href/src targets and no duplicate IDs."
)
