from typing import Dict, Any, Optional
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_web_server(headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    headers_lower = {k.lower(): v for k, v in headers.items()}
    server_header = headers_lower.get("server", "")
    server_lower = server_header.lower()

    if not server_header:
        return {
            "name": "Unknown",
            "confidence": 0,
            "evidence": ["Server HTTP response header was omitted or stripped by proxy."]
        }

    signals = []
    # 1. Nginx
    if "nginx" in server_lower:
        signals.append((SignalWeight.STRONG, f"Server header explicitly reports Nginx ('{server_header}')"))
        conf, ev = calculate_confidence(signals)
        return {"name": "Nginx", "confidence": conf, "evidence": ev}

    # 2. Apache
    if "apache" in server_lower:
        signals.append((SignalWeight.STRONG, f"Server header explicitly reports Apache ('{server_header}')"))
        conf, ev = calculate_confidence(signals)
        return {"name": "Apache HTTP Server", "confidence": conf, "evidence": ev}

    # 3. LiteSpeed
    if "litespeed" in server_lower:
        signals.append((SignalWeight.STRONG, f"Server header explicitly reports LiteSpeed ('{server_header}')"))
        conf, ev = calculate_confidence(signals)
        return {"name": "LiteSpeed Web Server", "confidence": conf, "evidence": ev}

    # 4. IIS
    if "iis" in server_lower or "microsoft-iis" in server_lower:
        signals.append((SignalWeight.STRONG, f"Server header explicitly reports Microsoft-IIS ('{server_header}')"))
        conf, ev = calculate_confidence(signals)
        return {"name": "Microsoft IIS", "confidence": conf, "evidence": ev}

    # 5. Caddy
    if "caddy" in server_lower:
        signals.append((SignalWeight.STRONG, f"Server header explicitly reports Caddy ('{server_header}')"))
        conf, ev = calculate_confidence(signals)
        return {"name": "Caddy Server", "confidence": conf, "evidence": ev}

    # 6. Cloudflare (when server header is cloudflare)
    if "cloudflare" in server_lower:
        signals.append((SignalWeight.STRONG, "Server response header reports Cloudflare proxy edge server"))
        conf, ev = calculate_confidence(signals)
        return {"name": "Cloudflare Edge Server", "confidence": conf, "evidence": ev}

    # Other detectable servers
    signals.append((SignalWeight.STRONG, f"Server HTTP header value: '{server_header}'"))
    conf, ev = calculate_confidence(signals)
    return {"name": server_header, "confidence": conf, "evidence": ev}
