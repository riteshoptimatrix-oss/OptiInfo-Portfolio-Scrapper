from typing import Dict, Any, Optional
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_deployment_platform(headers: Dict[str, str], dns_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    headers_lower = {k.lower(): v for k, v in headers.items()}
    cname_records = [c.lower() for c in dns_data.get("cname", [])]

    # 1. Vercel
    if "x-vercel-id" in headers_lower or any("vercel.app" in c for c in cname_records):
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "Vercel Platform header or CNAME alias detected")])
        return {"name": "Vercel", "confidence": conf, "evidence": ev}

    # 2. Netlify
    if "x-nf-request-id" in headers_lower or any("netlify.app" in c for c in cname_records):
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "Netlify Platform header or CNAME alias detected")])
        return {"name": "Netlify", "confidence": conf, "evidence": ev}

    # 3. Cloudflare Pages
    if any("pages.dev" in c for c in cname_records):
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "Cloudflare Pages CNAME alias (*.pages.dev) detected")])
        return {"name": "Cloudflare Pages", "confidence": conf, "evidence": ev}

    # 4. GitHub Pages
    if any("github.io" in c for c in cname_records):
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "GitHub Pages CNAME alias (*.github.io) detected")])
        return {"name": "GitHub Pages", "confidence": conf, "evidence": ev}

    return None
