import re


def slugify_name(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "item"


async def build_unique_slug(base_slug: str, exists) -> str:
    candidate = base_slug
    suffix = 2
    while await exists(candidate):
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
    return candidate
