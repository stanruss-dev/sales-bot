import os
from pathlib import Path


def load_knowledge_base(directory: str = "knowledge_base") -> str:
    """Load all markdown files from knowledge_base directory."""
    kb_path = Path(directory)
    if not kb_path.exists():
        return ""

    content_parts = []
    for md_file in sorted(kb_path.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        content_parts.append(f"## [{md_file.stem.upper()}]\n{content}")

    return "\n\n---\n\n".join(content_parts)


# Load once at import
KNOWLEDGE_BASE = load_knowledge_base()
