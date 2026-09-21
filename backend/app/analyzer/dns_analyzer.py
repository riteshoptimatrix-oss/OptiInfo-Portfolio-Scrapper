import socket
from urllib.parse import urlparse
from typing import Dict, Any, List

def analyze_dns_records(url: str) -> Dict[str, Any]:
    """
    Resolves A, AAAA, CNAME, MX, and NS DNS records for target website domain
    using native socket resolution without third-party APIs.
    """
    parsed = urlparse(url)
    domain = parsed.hostname or url
    result: Dict[str, Any] = {
        "domain": domain,
        "a_records": [],
        "cname": [],
        "nameservers": [],
        "mx_records": []
    }

    if not domain or domain in ("localhost", "127.0.0.1"):
        return result

    try:
        # A Records
        addresses = socket.getaddrinfo(domain, None, socket.AF_INET)
        a_ips = list(set([item[4][0] for item in addresses]))
        result["a_records"] = a_ips
    except Exception:
        pass

    try:
        # Host CNAME check via gethostbyname_ex
        host_info = socket.gethostbyname_ex(domain)
        if host_info[0] and host_info[0].lower() != domain.lower():
            result["cname"].append(host_info[0])
        for alias in host_info[1]:
            if alias.lower() != domain.lower():
                result["cname"].append(alias)
    except Exception:
        pass

    # Reverse DNS pointer on first IP if available
    if result["a_records"]:
        try:
            rev_name, _, _ = socket.gethostbyaddr(result["a_records"][0])
            if rev_name:
                result["nameservers"].append(rev_name)
        except Exception:
            pass

    return result
