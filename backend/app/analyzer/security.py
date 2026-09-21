import ipaddress
import socket
from urllib.parse import urlparse

PRIVATE_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

def is_safe_url(url: str) -> tuple[bool, str]:
    """
    Validates URL safety to prevent SSRF vulnerabilities.
    Returns (is_safe, error_reason).
    """
    if not url or not isinstance(url, str):
        return False, "Invalid URL string provided."

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported scheme '{parsed.scheme}'. Only http and https are allowed."

    hostname = parsed.hostname
    if not hostname:
        return False, "Could not resolve hostname from URL."

    hostname_lower = hostname.lower()
    if hostname_lower in ("localhost", "localhost.localdomain", "loopback", "127.0.0.1", "0.0.0.0", "::1"):
        return False, "Requests to internal or localhost hosts are forbidden."

    # Try resolving hostname to IP and check against private subnets
    try:
        addresses = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addresses:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            # Normalize IPv4-mapped IPv6 address (e.g. ::ffff:127.0.0.1)
            if hasattr(ip_obj, 'ipv4_mapped') and ip_obj.ipv4_mapped:
                ip_obj = ip_obj.ipv4_mapped

            for net in PRIVATE_IP_NETWORKS:
                if ip_obj in net or ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
                    return False, f"Forbidden target IP address '{ip_str}' is within a private/reserved network."
    except socket.gaierror:
        # DNS resolution failure will be handled by HTTP pipeline, but URL scheme is safe
        pass
    except Exception as e:
        return False, f"Error validating hostname: {str(e)}"

    return True, ""
