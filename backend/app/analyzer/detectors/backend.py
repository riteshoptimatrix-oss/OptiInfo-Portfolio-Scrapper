from typing import List, Dict, Any
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_backend_tech(
    html: str,
    headers: Dict[str, str],
    cookies: Dict[str, str],
    final_url: str,
    cms_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Probabilistically inspects observable public signals to detect backend language/framework.
    Adheres strictly to evidence-based detection rules without making unprovable claims.
    """
    html_lower = html.lower() if html else ""
    headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
    cookie_keys = [k.lower() for k in cookies.keys()]

    # 1. PHP & PHP Frameworks
    php_signals = []
    framework = None
    if "laravel_session" in cookie_keys or "xsrf-token" in cookie_keys:
        php_signals.append((SignalWeight.STRONG, "Laravel session / XSRF-TOKEN cookie pattern detected"))
        framework = "Laravel"
    if ".php" in final_url.lower():
        php_signals.append((SignalWeight.STRONG, "URL explicitly contains .php extension"))
    if "phpsessid" in cookie_keys:
        php_signals.append((SignalWeight.STRONG, "PHPSESSID session cookie detected"))
    if "x-powered-by" in headers_lower and "php" in headers_lower["x-powered-by"]:
        php_signals.append((SignalWeight.STRONG, f"X-Powered-By header explicitly reports '{headers['x-powered-by']}'"))
    if cms_info and cms_info.get("name") in ("WordPress", "WooCommerce", "Drupal", "Joomla", "PrestaShop", "Magento"):
        php_signals.append((SignalWeight.STRONG, f"CMS platform '{cms_info['name']}' requires PHP runtime execution"))

    if php_signals:
        conf, ev = calculate_confidence(php_signals)
        return {
            "language": "PHP",
            "framework": framework,
            "status": "Detected" if conf >= 85 else "Likely",
            "confidence": conf,
            "evidence": ev
        }

    # 2. ASP.NET
    asp_signals = []
    if ".aspx" in final_url.lower() or ".ashx" in final_url.lower():
        asp_signals.append((SignalWeight.STRONG, "URL contains .aspx / .ashx extension"))
    if "asp.net_sessionid" in cookie_keys or "aspnet" in cookie_keys:
        asp_signals.append((SignalWeight.STRONG, "ASP.NET_SessionId cookie detected"))
    if "__viewstate" in html_lower or "__eventvalidation" in html_lower:
        asp_signals.append((SignalWeight.STRONG, "ASP.NET __VIEWSTATE form input field detected in DOM"))
    if "x-powered-by" in headers_lower and "asp.net" in headers_lower["x-powered-by"]:
        asp_signals.append((SignalWeight.STRONG, f"X-Powered-By header explicitly reports '{headers['x-powered-by']}'"))

    if asp_signals:
        conf, ev = calculate_confidence(asp_signals)
        return {
            "language": "ASP.NET (C#)",
            "framework": ".NET Core / Framework",
            "status": "Detected" if conf >= 85 else "Likely",
            "confidence": conf,
            "evidence": ev
        }

    # 3. Python (Django / Flask / FastAPI)
    py_signals = []
    framework = None
    if "csrftoken" in cookie_keys:
        py_signals.append((SignalWeight.MEDIUM, "csrftoken cookie pattern (common in Django) detected"))
        framework = "Django"
    if "sessionid" in cookie_keys and ("django" in html_lower or "admin" in final_url.lower()):
        py_signals.append((SignalWeight.MEDIUM, "Django admin session cookie structure detected"))
        framework = "Django"
    if "server" in headers_lower and ("gunicorn" in headers_lower["server"] or "uvicorn" in headers_lower["server"] or "werkzeug" in headers_lower["server"]):
        py_signals.append((SignalWeight.STRONG, f"Python WSGI/ASGI Server header detected ('{headers['server']}')"))
        if "uvicorn" in headers_lower["server"]:
            framework = "FastAPI / Starlette"

    if py_signals:
        conf, ev = calculate_confidence(py_signals)
        return {
            "language": "Python",
            "framework": framework,
            "status": "Likely" if conf >= 75 else "Possible",
            "confidence": conf,
            "evidence": ev
        }

    # 4. Java (Spring / JSP)
    java_signals = []
    if "jsessionid" in cookie_keys:
        java_signals.append((SignalWeight.STRONG, "JSESSIONID cookie (Java Servlet container) detected"))
    if ".jsp" in final_url.lower() or ".do" in final_url.lower():
        java_signals.append((SignalWeight.STRONG, "URL contains .jsp / .do extension"))
    if "server" in headers_lower and ("tomcat" in headers_lower["server"] or "glassfish" in headers_lower["server"] or "wildfly" in headers_lower["server"]):
        java_signals.append((SignalWeight.STRONG, f"Java application server header detected ('{headers['server']}')"))

    if java_signals:
        conf, ev = calculate_confidence(java_signals)
        return {
            "language": "Java",
            "framework": "Spring / Java EE",
            "status": "Detected" if conf >= 85 else "Likely",
            "confidence": conf,
            "evidence": ev
        }

    # 5. Node.js (Express / NestJS)
    node_signals = []
    if "x-powered-by" in headers_lower and "express" in headers_lower["x-powered-by"]:
        node_signals.append((SignalWeight.STRONG, "X-Powered-By header explicitly reports 'Express'"))
    if "connect.sid" in cookie_keys:
        node_signals.append((SignalWeight.STRONG, "connect.sid (Express / Connect session cookie) detected"))

    if node_signals:
        conf, ev = calculate_confidence(node_signals)
        return {
            "language": "Node.js",
            "framework": "Express",
            "status": "Detected" if conf >= 80 else "Likely",
            "confidence": conf,
            "evidence": ev
        }

    # 6. Ruby (Ruby on Rails)
    ruby_signals = []
    if "_session_id" in cookie_keys and "phusion" in headers_lower.get("server", ""):
        ruby_signals.append((SignalWeight.STRONG, "Phusion Passenger server header and Rails session cookie detected"))
        
    if ruby_signals:
        conf, ev = calculate_confidence(ruby_signals)
        return {
            "language": "Ruby",
            "framework": "Ruby on Rails",
            "status": "Likely",
            "confidence": conf,
            "evidence": ev
        }

    # Default fallback: Unknown / Not publicly detectable
    return {
        "language": "Unknown",
        "framework": None,
        "status": "Not publicly detectable",
        "confidence": 0,
        "evidence": [
            "Server source code is hidden behind HTTP responses and no public server-side language header or cookie fingerprints were exposed."
        ]
    }
