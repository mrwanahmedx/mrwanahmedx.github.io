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

    def handle_starttag(self, tag: str, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            value = attrs.get(key)
            if value:
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

print(f"Validated {len(HTML_FILES)} HTML files with no missing local href/src targets.")
