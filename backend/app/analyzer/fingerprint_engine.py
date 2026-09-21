from typing import Dict, Any, List
from app.analyzer.detectors.frontend import detect_frontend_tech
from app.analyzer.detectors.css import detect_css_frameworks
from app.analyzer.detectors.cms import detect_cms
from app.analyzer.detectors.ecommerce import detect_ecommerce
from app.analyzer.detectors.backend import detect_backend_tech
from app.analyzer.detectors.server import detect_web_server
from app.analyzer.detectors.cdn import detect_cdn
from app.analyzer.detectors.hosting import detect_hosting_provider
from app.analyzer.detectors.deployment import detect_deployment_platform
from app.analyzer.detectors.analytics import detect_analytics
from app.analyzer.detectors.integrations import detect_third_party_integrations
from app.analyzer.detectors.metadata import extract_website_metadata
from app.analyzer.classifier import classifier, get_confidence_label

class FingerprintEngine:
    """
    Centralized Technology Fingerprint Engine (Analyzer v2.0.0).
    Runs all 13 technology detectors, applies strict classification hierarchy,
    and returns evidence-backed normalized technology analysis payloads.
    """
    def run_fingerprint_analysis(
        self,
        target_url: str,
        browser_data: Dict[str, Any],
        http_data: Dict[str, Any],
        dns_data: Dict[str, Any],
        ssl_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        # Merge headers & cookies
        headers = {**http_data.get("headers", {}), **browser_data.get("headers", {})}
        cookies = http_data.get("cookies", {})
        html = browser_data.get("html") or ""
        scripts = browser_data.get("scripts", [])
        stylesheets = browser_data.get("stylesheets", [])
        images = browser_data.get("images", [])
        iframes = browser_data.get("iframes", [])
        meta_tags = browser_data.get("meta_tags", [])
        dom_info = browser_data.get("dom_info", {})
        final_url = browser_data.get("final_url") or http_data.get("final_url") or target_url
        page_title = browser_data.get("page_title") or ""

        # 1. Detectors Execution
        frontend_detected = detect_frontend_tech(html, scripts, headers, dom_info)
        css_detected = detect_css_frameworks(html, stylesheets, dom_info)
        cms_info = detect_cms(html, scripts, stylesheets, headers, cookies, meta_tags)
        ecommerce_info = detect_ecommerce(html, scripts, stylesheets, cookies)
        backend_info = detect_backend_tech(html, headers, cookies, final_url, cms_info)
        server_info = detect_web_server(headers)
        cdn_info = detect_cdn(headers, cookies, dns_data)
        hosting_info = detect_hosting_provider(headers, dns_data, cdn_info)
        deployment_info = detect_deployment_platform(headers, dns_data)
        analytics_info = detect_analytics(html, scripts)
        integrations_info = detect_third_party_integrations(html, scripts, iframes)
        metadata_info = extract_website_metadata(
            html, page_title, final_url, meta_tags, scripts, stylesheets, images, iframes
        )

        # Attach confidence labels to detected items
        for item in frontend_detected + css_detected + analytics_info + integrations_info:
            item["confidence_label"] = get_confidence_label(item["confidence"])

        if cms_info:
            cms_info["confidence_label"] = get_confidence_label(cms_info["confidence"])
        if ecommerce_info:
            ecommerce_info["confidence_label"] = get_confidence_label(ecommerce_info["confidence"])
        if backend_info and backend_info.get("confidence", 0) > 0:
            backend_info["confidence_label"] = get_confidence_label(backend_info["confidence"])
        if server_info and server_info.get("confidence", 0) > 0:
            server_info["confidence_label"] = get_confidence_label(server_info["confidence"])
        if cdn_info:
            cdn_info["confidence_label"] = get_confidence_label(cdn_info["confidence"])

        # 2. Strict Primary Technology Classification Hierarchy
        primary_tech = classifier.classify_primary_technology(
            cms_info=cms_info,
            ecommerce_info=ecommerce_info,
            backend_info=backend_info,
            frontend_tech=frontend_detected,
            css_tech=css_detected,
            html=html,
            scripts=scripts
        )

        # Separate Frontend Frameworks vs JavaScript Libraries
        frontend_frameworks = []
        javascript_libraries = []

        for item in frontend_detected:
            if item.get("category") in ("Core Language", "SPA Framework", "SSR Framework", "Frontend Framework") or item["name"] in ("React", "Vue.js", "Angular", "Svelte", "Next.js", "Nuxt.js"):
                frontend_frameworks.append(item)
            else:
                javascript_libraries.append(item)

        # Aggregate evidence list for detailed inspector
        all_evidence = []
        confidence_values = []

        # Primary evidence
        for ev in primary_tech.get("evidence", []):
            all_evidence.append({
                "technology": primary_tech["name"],
                "category": "Primary Technology",
                "evidence": ev,
                "confidence": primary_tech["confidence"]
            })
        confidence_values.append(primary_tech["confidence"])

        # Secondary tech evidence
        for item in frontend_detected + css_detected + analytics_info + integrations_info:
            confidence_values.append(item["confidence"])
            for ev in item.get("evidence", []):
                all_evidence.append({
                    "technology": item["name"],
                    "category": item.get("category", "Secondary Tech"),
                    "evidence": ev,
                    "confidence": item["confidence"]
                })

        if cms_info:
            confidence_values.append(cms_info["confidence"])
            for ev in cms_info.get("evidence", []):
                all_evidence.append({
                    "technology": cms_info["name"],
                    "category": "CMS Platform",
                    "evidence": ev,
                    "confidence": cms_info["confidence"]
                })

        if ecommerce_info:
            confidence_values.append(ecommerce_info["confidence"])
            for ev in ecommerce_info.get("evidence", []):
                all_evidence.append({
                    "technology": ecommerce_info["name"],
                    "category": "E-Commerce",
                    "evidence": ev,
                    "confidence": ecommerce_info["confidence"]
                })

        if server_info and server_info.get("confidence", 0) > 0:
            confidence_values.append(server_info["confidence"])
            for ev in server_info.get("evidence", []):
                all_evidence.append({
                    "technology": server_info["name"],
                    "category": "Web Server",
                    "evidence": ev,
                    "confidence": server_info["confidence"]
                })

        overall_confidence = int(sum(confidence_values) / len(confidence_values)) if confidence_values else 85

        return {
            "page_title": page_title,
            "final_url": final_url,
            "http_status": browser_data.get("status_code") or http_data.get("status_code") or 200,
            "analyzer_version": "2.0.0",
            "primary_technology": primary_tech,
            "technology_stack": {
                "cms": cms_info,
                "ecommerce": ecommerce_info,
                "frontend_frameworks": frontend_frameworks,
                "javascript_libraries": javascript_libraries,
                "css_frameworks": css_detected,
                "backend": backend_info,
                "web_server": server_info,
                "cdn": cdn_info
            },
            "infrastructure": {
                "hosting_provider": hosting_info,
                "deployment_platform": deployment_info,
                "dns": dns_data,
                "ssl": ssl_data
            },
            "analytics": analytics_info,
            "integrations": integrations_info,
            "metadata_info": metadata_info,
            "performance_metrics": {
                "http_response_time_ms": http_data.get("response_time_ms", 0),
                "script_count": len(scripts),
                "stylesheet_count": len(stylesheets),
                "image_count": len(images)
            },
            "evidence": all_evidence,
            "overall_confidence": overall_confidence
        }

fingerprint_engine = FingerprintEngine()
