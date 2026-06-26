import os
from pathlib import Path

# products.md goes first so price data is always within the truncation limit
_PRIORITY_FILES = ["products.md", "sales_script.md", "pricing.md", "objections.md", "company.md", "safety.md"]


def load_knowledge_base(directory: str = "knowledge_base") -> str:
    kb_path = Path(directory)
    if not kb_path.exists():
        return ""

    available = {f.name: f for f in kb_path.glob("*.md")}

    ordered = []
    for name in _PRIORITY_FILES:
        if name in available:
            ordered.append(available.pop(name))
    ordered.extend(sorted(available.values()))

    content_parts = []
    for md_file in ordered:
        content = md_file.read_text(encoding="utf-8")
        content_parts.append(f"## [{md_file.stem.upper()}]\n{content}")

    return "\n\n---\n\n".join(content_parts)


KNOWLEDGE_BASE = load_knowledge_base()
