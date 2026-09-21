from typing import List, Dict, Any
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_analytics(html: str, scripts: List[str]) -> List[Dict[str, Any]]:
    results = []
    html_lower = html.lower() if html else ""
    scripts_str = " ".join(scripts).lower()

    # 1. Google Analytics (GA4 / Universal)
    ga_signals = []
    if "google-analytics.com/analytics.js" in scripts_str or "googletagmanager.com/gtag/js" in scripts_str or "gtag(" in html_lower:
        ga_signals.append((SignalWeight.STRONG, "Google Analytics gtag.js / analytics.js script tag reference detected"))
    if "ua-" in html_lower or "g-" in html_lower:
        if "gtag('config'" in html_lower or "ga('create'" in html_lower:
            ga_signals.append((SignalWeight.STRONG, "Google Analytics Tracking Measurement ID snippet found in DOM"))
    if ga_signals:
        conf, ev = calculate_confidence(ga_signals)
        results.append({"name": "Google Analytics", "category": "Analytics", "confidence": conf, "evidence": ev})

    # 2. Google Tag Manager (GTM)
    gtm_signals = []
    if "googletagmanager.com/gtm.js" in scripts_str or "gtm-" in html_lower:
        if "gtm.start" in html_lower or "gtm.js" in html_lower:
            gtm_signals.append((SignalWeight.STRONG, "Google Tag Manager gtm.js container script snippet detected"))
    if gtm_signals:
        conf, ev = calculate_confidence(gtm_signals)
        results.append({"name": "Google Tag Manager", "category": "Tag Management", "confidence": conf, "evidence": ev})

    # 3. Meta / Facebook Pixel
    fb_signals = []
    if "connect.facebook.net" in scripts_str or "fbq(" in html_lower or "facebook-domain-verification" in html_lower:
        fb_signals.append((SignalWeight.STRONG, "Meta Pixel fbevents.js script / fbq() snippet detected"))
    if fb_signals:
        conf, ev = calculate_confidence(fb_signals)
        results.append({"name": "Meta Pixel (Facebook)", "category": "Ad Tracking", "confidence": conf, "evidence": ev})

    # 4. Microsoft Clarity
    clarity_signals = []
    if "clarity.ms/tag" in scripts_str or "clarity(" in html_lower:
        clarity_signals.append((SignalWeight.STRONG, "Microsoft Clarity tracking tag snippet detected"))
    if clarity_signals:
        conf, ev = calculate_confidence(clarity_signals)
        results.append({"name": "Microsoft Clarity", "category": "Session Recording", "confidence": conf, "evidence": ev})

    # 5. Hotjar
    hj_signals = []
    if "static.hotjar.com" in scripts_str or "hj(" in html_lower or "_hjsettings" in html_lower:
        hj_signals.append((SignalWeight.STRONG, "Hotjar heatmaps & recording script snippet detected"))
    if hj_signals:
        conf, ev = calculate_confidence(hj_signals)
        results.append({"name": "Hotjar", "category": "Heatmap & Recording", "confidence": conf, "evidence": ev})

    return results
