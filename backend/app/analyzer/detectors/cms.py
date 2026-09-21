from typing import List, Dict, Any, Optional
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_cms(html: str, scripts: List[str], stylesheets: List[str], headers: Dict[str, str], cookies: Dict[str, str], meta_tags: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    html_lower = html.lower() if html else ""
    scripts_str = " ".join(scripts).lower()
    styles_str = " ".join(stylesheets).lower()

    # Generator Meta Inspection
    generator_val = ""
    for meta in meta_tags:
        if meta.get("name", "").lower() == "generator":
            generator_val = meta.get("content", "").lower()

    # 1. WordPress
    wp_signals = []
    cookie_str = " ".join(cookies.keys()).lower()
    if "/wp-content/" in html_lower or "/wp-content/" in styles_str or "/wp-content/" in scripts_str:
        wp_signals.append((SignalWeight.STRONG, "Path pattern /wp-content/ detected in asset URLs"))
    if "/wp-includes/" in html_lower or "/wp-includes/" in styles_str or "/wp-includes/" in scripts_str:
        wp_signals.append((SignalWeight.STRONG, "Path pattern /wp-includes/ detected in asset URLs"))
    if "wp-json" in html_lower or "wp-embed.min.js" in scripts_str or "wp-embed" in scripts_str:
        wp_signals.append((SignalWeight.STRONG, "WordPress REST API (wp-json) endpoint / embed script detected"))
    if "wordpress" in generator_val:
        wp_signals.append((SignalWeight.STRONG, f"Generator meta tag explicitly identifies WordPress ('{generator_val}')"))
    if "wordpress_test_cookie" in cookie_str or "wordpress_logged_in" in cookie_str:
        wp_signals.append((SignalWeight.STRONG, "WordPress cookie pattern detected"))
    if "wp-block-" in html_lower or "wp-custom-css" in html_lower or "wpadminbar" in html_lower:
        wp_signals.append((SignalWeight.MEDIUM, "WordPress DOM class marker (wp-block / wp-custom-css) detected"))

    if wp_signals:
        conf, ev = calculate_confidence(wp_signals)
        return {"name": "WordPress", "category": "CMS", "confidence": conf, "evidence": ev}

    # 2. Shopify
    shopify_signals = []
    if "cdn.shopify.com" in html_lower or "cdn.shopify.com" in scripts_str:
        shopify_signals.append((SignalWeight.STRONG, "Shopify CDN asset domain (cdn.shopify.com) detected"))
    if "shopify" in generator_val:
        shopify_signals.append((SignalWeight.STRONG, "Generator meta tag identifies Shopify"))
    if "shopify.theme" in html_lower or "shopify-digital-wallet" in html_lower:
        shopify_signals.append((SignalWeight.STRONG, "Shopify JS theme global window object detected"))
    if shopify_signals:
        conf, ev = calculate_confidence(shopify_signals)
        return {"name": "Shopify", "category": "E-commerce CMS", "confidence": conf, "evidence": ev}

    # 3. Webflow
    webflow_signals = []
    if "webflow.com" in html_lower or "assets.website-files.com" in html_lower or "assets.website-files.com" in scripts_str:
        webflow_signals.append((SignalWeight.STRONG, "Webflow asset domain (assets.website-files.com) detected"))
    if "webflow" in generator_val:
        webflow_signals.append((SignalWeight.STRONG, "Generator meta tag identifies Webflow"))
    if "w-nav" in html_lower or "w-slider" in html_lower or "w-dropdown" in html_lower:
        webflow_signals.append((SignalWeight.MEDIUM, "Webflow component class prefix (w-nav/w-slider) detected"))
    if webflow_signals:
        conf, ev = calculate_confidence(webflow_signals)
        return {"name": "Webflow", "category": "CMS / Site Builder", "confidence": conf, "evidence": ev}

    # 4. Wix
    wix_signals = []
    if "wix.com" in html_lower or "wixstatic.com" in html_lower or "parastorage.com" in html_lower:
        wix_signals.append((SignalWeight.STRONG, "Wix CDN domain (static.wixstatic.com / parastorage.com) detected"))
    if "wix.com" in generator_val or "wix code" in generator_val:
        wix_signals.append((SignalWeight.STRONG, "Generator meta tag identifies Wix"))
    if wix_signals:
        conf, ev = calculate_confidence(wix_signals)
        return {"name": "Wix", "category": "Website Builder", "confidence": conf, "evidence": ev}

    # 5. Squarespace
    sq_signals = []
    if "static1.squarespace.com" in html_lower or "squarespace-cdn.com" in html_lower:
        sq_signals.append((SignalWeight.STRONG, "Squarespace CDN asset domain detected"))
    if "squarespace" in generator_val:
        sq_signals.append((SignalWeight.STRONG, "Generator meta tag identifies Squarespace"))
    if sq_signals:
        conf, ev = calculate_confidence(sq_signals)
        return {"name": "Squarespace", "category": "CMS / Site Builder", "confidence": conf, "evidence": ev}

    # 6. Drupal
    drupal_signals = []
    if "drupal" in generator_val or "drupal" in html_lower:
        drupal_signals.append((SignalWeight.STRONG, "Drupal generator tag or DOM marker detected"))
    if "sites/default/files" in html_lower or "drupal.js" in scripts_str:
        drupal_signals.append((SignalWeight.STRONG, "Drupal asset path structure (sites/default/files) detected"))
    if drupal_signals:
        conf, ev = calculate_confidence(drupal_signals)
        return {"name": "Drupal", "category": "CMS", "confidence": conf, "evidence": ev}

    # 7. Joomla
    joomla_signals = []
    if "joomla" in generator_val or "/components/com_" in html_lower or "/media/system/js/" in html_lower:
        joomla_signals.append((SignalWeight.STRONG, "Joomla generator tag or URL component path (/components/com_) detected"))
    if joomla_signals:
        conf, ev = calculate_confidence(joomla_signals)
        return {"name": "Joomla", "category": "CMS", "confidence": conf, "evidence": ev}

    # 8. Ghost
    ghost_signals = []
    if "ghost" in generator_val or "ghost-search" in scripts_str:
        ghost_signals.append((SignalWeight.STRONG, "Ghost publishing platform generator meta tag / asset detected"))
    if ghost_signals:
        conf, ev = calculate_confidence(ghost_signals)
        return {"name": "Ghost", "category": "Blogging CMS", "confidence": conf, "evidence": ev}

    return None
