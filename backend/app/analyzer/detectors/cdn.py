from typing import Dict, Any, Optional, List
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_cdn(headers: Dict[str, str], cookies: Dict[str, str], dns_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    headers_lower = {k.lower(): v for k, v in headers.items()}
    cname_records = [c.lower() for c in dns_data.get("cname", [])]
    ns_records = [ns.lower() for ns in dns_data.get("nameservers", [])]

    # 1. Cloudflare
    cf_signals = []
    if "cf-ray" in headers_lower or "cf-cache-status" in headers_lower:
        cf_signals.append((SignalWeight.STRONG, "Cloudflare HTTP response header (cf-ray / cf-cache-status) present"))
    if headers_lower.get("server", "").lower() == "cloudflare":
        cf_signals.append((SignalWeight.STRONG, "Server response header explicitly identifies 'cloudflare'"))
    if any("cloudflare.com" in ns for ns in ns_records) or any("cloudflare" in cname for cname in cname_records):
        cf_signals.append((SignalWeight.STRONG, "Cloudflare DNS CNAME or Authoritative Nameservers detected"))
    if cf_signals:
        conf, ev = calculate_confidence(cf_signals)
        return {"name": "Cloudflare CDN / Proxy", "confidence": conf, "evidence": ev}

    # 2. AWS CloudFront
    cfn_signals = []
    if "via" in headers_lower and "cloudfront" in headers_lower["via"].lower():
        cfn_signals.append((SignalWeight.STRONG, "Via response header contains 'cloudfront.net'"))
    if "x-amz-cf-id" in headers_lower or "x-amz-cf-pop" in headers_lower:
        cfn_signals.append((SignalWeight.STRONG, "Amazon CloudFront tracking header (x-amz-cf-id) present"))
    if any("cloudfront.net" in cname for cname in cname_records):
        cfn_signals.append((SignalWeight.STRONG, "CloudFront CNAME alias domain (*.cloudfront.net) detected"))
    if cfn_signals:
        conf, ev = calculate_confidence(cfn_signals)
        return {"name": "AWS CloudFront", "confidence": conf, "evidence": ev}

    # 3. Fastly
    fastly_signals = []
    if "x-fastly-request-id" in headers_lower or "fastly-restarts" in headers_lower:
        fastly_signals.append((SignalWeight.STRONG, "Fastly HTTP response tracking header detected"))
    if any("fastly.net" in cname for cname in cname_records):
        fastly_signals.append((SignalWeight.STRONG, "Fastly CNAME alias (*.fastly.net) detected"))
    if fastly_signals:
        conf, ev = calculate_confidence(fastly_signals)
        return {"name": "Fastly CDN", "confidence": conf, "evidence": ev}

    # 4. Akamai
    akamai_signals = []
    if "x-akamai-transformed" in headers_lower or "akamai-origin-hop" in headers_lower:
        akamai_signals.append((SignalWeight.STRONG, "Akamai HTTP header signature detected"))
    if any("akamai" in cname or "edgekey.net" in cname for cname in cname_records):
        akamai_signals.append((SignalWeight.STRONG, "Akamai Edge CNAME domain (*.edgekey.net) detected"))
    if akamai_signals:
        conf, ev = calculate_confidence(akamai_signals)
        return {"name": "Akamai CDN", "confidence": conf, "evidence": ev}

    # 5. Bunny CDN
    bunny_signals = []
    if "b-cdn.net" in headers_lower.get("server", "").lower() or "b-cdn" in str(cname_records):
        bunny_signals.append((SignalWeight.STRONG, "Bunny CDN asset header / CNAME reference detected"))
    if bunny_signals:
        conf, ev = calculate_confidence(bunny_signals)
        return {"name": "Bunny CDN", "confidence": conf, "evidence": ev}

    # 6. Vercel Edge
    vercel_signals = []
    if "x-vercel-id" in headers_lower or "x-vercel-cache" in headers_lower:
        vercel_signals.append((SignalWeight.STRONG, "Vercel Edge Network HTTP response header (x-vercel-id) present"))
    if vercel_signals:
        conf, ev = calculate_confidence(vercel_signals)
        return {"name": "Vercel Edge Network", "confidence": conf, "evidence": ev}

    # 7. Netlify
    netlify_signals = []
    if "x-nf-request-id" in headers_lower or headers_lower.get("server", "").lower() == "netlify":
        netlify_signals.append((SignalWeight.STRONG, "Netlify Edge CDN response header (x-nf-request-id) present"))
    if netlify_signals:
        conf, ev = calculate_confidence(netlify_signals)
        return {"name": "Netlify Edge CDN", "confidence": conf, "evidence": ev}

    return None
