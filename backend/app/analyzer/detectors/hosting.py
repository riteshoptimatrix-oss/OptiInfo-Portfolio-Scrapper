from typing import Dict, Any, Optional
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_hosting_provider(
    headers: Dict[str, str],
    dns_data: Dict[str, Any],
    cdn_info: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    cname_records = [c.lower() for c in dns_data.get("cname", [])]
    ns_records = [ns.lower() for ns in dns_data.get("nameservers", [])]

    # 1. DigitalOcean
    do_signals = []
    if any("digitalocean.com" in ns for ns in ns_records):
        do_signals.append((SignalWeight.STRONG, "DigitalOcean Authoritative Nameservers (ns1.digitalocean.com) detected"))
    if do_signals:
        conf, ev = calculate_confidence(do_signals)
        return {"name": "DigitalOcean", "confidence": conf, "evidence": ev, "status": "Detected"}

    # 2. Vercel
    vercel_signals = []
    if any("vercel-dns.com" in ns for ns in ns_records) or any("vercel.app" in cname for cname in cname_records):
        vercel_signals.append((SignalWeight.STRONG, "Vercel Authoritative DNS or CNAME alias (cname.vercel-dns.com) detected"))
    if "x-vercel-id" in {k.lower(): v for k, v in headers.items()}:
        vercel_signals.append((SignalWeight.STRONG, "Vercel Edge Platform HTTP response header present"))
    if vercel_signals:
        conf, ev = calculate_confidence(vercel_signals)
        return {"name": "Vercel Infrastructure", "confidence": conf, "evidence": ev, "status": "Detected"}

    # 3. Netlify
    netlify_signals = []
    if any("netlify.com" in ns for ns in ns_records) or any("netlify.app" in cname for cname in cname_records):
        netlify_signals.append((SignalWeight.STRONG, "Netlify DNS or CNAME alias detected"))
    if netlify_signals:
        conf, ev = calculate_confidence(netlify_signals)
        return {"name": "Netlify Infrastructure", "confidence": conf, "evidence": ev, "status": "Detected"}

    # 4. Hetzner
    hetzner_signals = []
    if any("hetzner" in ns for ns in ns_records) or any("your-server.de" in ns for ns in ns_records):
        hetzner_signals.append((SignalWeight.STRONG, "Hetzner Online DNS Infrastructure detected"))
    if hetzner_signals:
        conf, ev = calculate_confidence(hetzner_signals)
        return {"name": "Hetzner Online", "confidence": conf, "evidence": ev, "status": "Detected"}

    # 5. AWS
    aws_signals = []
    if any("awsdns" in ns for ns in ns_records) or any("amazonaws.com" in cname for cname in cname_records):
        aws_signals.append((SignalWeight.STRONG, "Amazon Route53 Authoritative DNS or AWS CNAME alias detected"))
    if aws_signals:
        conf, ev = calculate_confidence(aws_signals)
        return {"name": "Amazon Web Services (AWS)", "confidence": conf, "evidence": ev, "status": "Detected"}

    # 6. Hostinger
    hostinger_signals = []
    if any("hostinger" in ns for ns in ns_records):
        hostinger_signals.append((SignalWeight.STRONG, "Hostinger Authoritative Nameservers detected"))
    if hostinger_signals:
        conf, ev = calculate_confidence(hostinger_signals)
        return {"name": "Hostinger", "confidence": conf, "evidence": ev, "status": "Detected"}

    # 7. GoDaddy
    godaddy_signals = []
    if any("domaincontrol.com" in ns for ns in ns_records):
        godaddy_signals.append((SignalWeight.STRONG, "GoDaddy (domaincontrol.com) Authoritative Nameservers detected"))
    if godaddy_signals:
        conf, ev = calculate_confidence(godaddy_signals)
        return {"name": "GoDaddy Hosting / Infrastructure", "confidence": conf, "evidence": ev, "status": "Detected"}

    # 8. SiteGround
    sg_signals = []
    if any("siteground" in ns for ns in ns_records):
        sg_signals.append((SignalWeight.STRONG, "SiteGround Authoritative Nameservers detected"))
    if sg_signals:
        conf, ev = calculate_confidence(sg_signals)
        return {"name": "SiteGround", "confidence": conf, "evidence": ev, "status": "Detected"}

    # 9. Bluehost
    bh_signals = []
    if any("bluehost.com" in ns for ns in ns_records):
        bh_signals.append((SignalWeight.STRONG, "Bluehost Authoritative Nameservers detected"))
    if bh_signals:
        conf, ev = calculate_confidence(bh_signals)
        return {"name": "Bluehost", "confidence": conf, "evidence": ev, "status": "Detected"}

    # Default logic when behind CDN proxy or hidden origin
    if cdn_info and cdn_info.get("name"):
        cdn_name = cdn_info["name"]
        reason_msg = (
            "Website is behind Cloudflare CDN/Reverse Proxy which masks origin hosting provider."
            if "cloudflare" in cdn_name.lower()
            else f"Website is behind {cdn_name} which masks origin hosting provider."
        )
        return {
            "name": "Unknown",
            "confidence": 0,
            "evidence": [],
            "status": "Hidden behind CDN/Proxy",
            "reason": reason_msg
        }

    return {
        "name": "Unknown",
        "confidence": 0,
        "evidence": [],
        "status": "Not publicly detectable",
        "reason": "No public authoritative DNS or hosting header fingerprints were exposed."
    }
