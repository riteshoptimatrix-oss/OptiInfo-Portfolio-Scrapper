import ssl
import socket
from urllib.parse import urlparse
from typing import Dict, Any

def analyze_ssl_certificate(url: str, timeout_sec: int = 5) -> Dict[str, Any]:
    """
    Inspects SSL/TLS certificate configuration using Python standard ssl library.
    """
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        return {
            "enabled": False,
            "reason": "Target site uses non-secure HTTP scheme."
        }

    domain = parsed.hostname
    port = parsed.port or 443

    if not domain:
        return {"enabled": False, "reason": "Invalid domain."}

    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    try:
        with socket.create_connection((domain, port), timeout=timeout_sec) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()

                # Extract Issuer & Subject
                subject_dict = dict(x[0] for x in cert.get("subject", []))
                issuer_dict = dict(x[0] for x in cert.get("issuer", []))

                return {
                    "enabled": True,
                    "version": version,
                    "cipher": cipher[0] if cipher else "Unknown",
                    "subject": subject_dict.get("commonName", domain),
                    "issuer": issuer_dict.get("organizationName") or issuer_dict.get("commonName", "Unknown"),
                    "not_before": cert.get("notBefore"),
                    "not_after": cert.get("notAfter"),
                    "san": [alt[1] for alt in cert.get("subjectAltName", []) if alt[0] == "DNS"]
                }
    except Exception as e:
        return {
            "enabled": False,
            "error": str(e),
            "reason": "Could not establish TLS connection or verify certificate."
        }
