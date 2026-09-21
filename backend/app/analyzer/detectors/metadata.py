from typing import Dict, Any, List
from urllib.parse import urljoin

def extract_website_metadata(
    html: str,
    title: str,
    final_url: str,
    meta_tags: List[Dict[str, str]],
    scripts: List[str],
    stylesheets: List[str],
    images: List[str],
    iframes: List[str]
) -> Dict[str, Any]:
    meta_dict = {}
    og_dict = {}
    twitter_dict = {}
    canonical_url = None
    language = None
    favicon = None

    for meta in meta_tags:
        name = meta.get("name", "").lower()
        prop = meta.get("property", "").lower()
        content = meta.get("content", "")

        if name:
            meta_dict[name] = content
        if prop.startswith("og:"):
            og_dict[prop[3:]] = content
        if name.startswith("twitter:"):
            twitter_dict[name[8:]] = content

    # Favicon resolution
    if "shortcut icon" in meta_dict or "icon" in meta_dict:
        favicon = meta_dict.get("icon") or meta_dict.get("shortcut icon")
        if favicon and not favicon.startswith(("http://", "https://")):
            favicon = urljoin(final_url, favicon)

    return {
        "title": title or meta_dict.get("title", ""),
        "description": meta_dict.get("description", og_dict.get("description", "")),
        "keywords": meta_dict.get("keywords", ""),
        "viewport": meta_dict.get("viewport", ""),
        "generator": meta_dict.get("generator", ""),
        "author": meta_dict.get("author", ""),
        "canonical_url": meta_dict.get("canonical", final_url),
        "open_graph": og_dict,
        "twitter_card": twitter_dict,
        "favicon": favicon or urljoin(final_url, "/favicon.ico"),
        "element_counts": {
            "script_tags": len(scripts),
            "stylesheet_tags": len(stylesheets),
            "images": len(images),
            "iframes": len(iframes)
        }
    }
