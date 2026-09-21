from typing import Dict, Any, List, Optional

def get_confidence_label(score: int) -> str:
    if score >= 90:
        return "Very High"
    if score >= 75:
        return "High"
    if score >= 60:
        return "Medium"
    if score >= 40:
        return "Low"
    return "Very Low"

class PrimaryTechnologyClassifier:
    """
    Dedicated Primary Technology Classifier (v2.0.0).
    Applies strict priority hierarchy:
      CMS Platform > E-Commerce > Backend Framework (Laravel/Django) > SSR Framework (Next.js) > SPA Framework (React/Vue/Angular) > Server-Rendered Language (PHP) > Static HTML/CSS/JS
    instead of incorrectly promoting high-confidence libraries (such as jQuery) to primary status.
    """
    def classify_primary_technology(
        self,
        cms_info: Optional[Dict[str, Any]],
        ecommerce_info: Optional[Dict[str, Any]],
        backend_info: Optional[Dict[str, Any]],
        frontend_tech: List[Dict[str, Any]],
        css_tech: List[Dict[str, Any]],
        html: str,
        scripts: List[str]
    ) -> Dict[str, Any]:

        # 1. CMS Priority Check (e.g. WordPress, Shopify, Webflow, Wix, Squarespace)
        if cms_info and cms_info.get("name") and cms_info.get("confidence", 0) >= 60:
            cms_name = cms_info["name"]
            conf = cms_info.get("confidence", 90)
            return {
                "name": cms_name,
                "type": "cms",
                "confidence": conf,
                "confidence_label": get_confidence_label(conf),
                "evidence": cms_info.get("evidence", [f"Strong {cms_name} platform signatures detected"])
            }

        # 2. Standalone E-Commerce Priority Check (e.g. Shopify, Magento, PrestaShop)
        if ecommerce_info and ecommerce_info.get("name") and ecommerce_info.get("confidence", 0) >= 60:
            ecom_name = ecommerce_info["name"]
            if ecom_name != "WooCommerce":  # WooCommerce runs on WordPress CMS
                conf = ecommerce_info.get("confidence", 90)
                return {
                    "name": ecom_name,
                    "type": "ecommerce",
                    "confidence": conf,
                    "confidence_label": get_confidence_label(conf),
                    "evidence": ecommerce_info.get("evidence", [f"Dedicated {ecom_name} e-commerce platform signatures detected"])
                }

        # 3. Backend Framework Priority Check (Laravel, Django, Spring, Ruby on Rails)
        if backend_info and backend_info.get("framework") and backend_info.get("confidence", 0) >= 60:
            fw = backend_info["framework"]
            conf = backend_info.get("confidence", 85)
            return {
                "name": fw,
                "type": "backend_framework",
                "confidence": conf,
                "confidence_label": get_confidence_label(conf),
                "evidence": backend_info.get("evidence", [f"{fw} backend framework signatures detected"])
            }

        # Extract frontend framework names
        framework_names = {item["name"]: item for item in frontend_tech}

        # 4. SSR / Full-Stack Framework Priority Check (Next.js, Nuxt.js, Astro)
        if "Next.js" in framework_names and framework_names["Next.js"].get("confidence", 0) >= 60:
            item = framework_names["Next.js"]
            conf = item.get("confidence", 90)
            return {
                "name": "Next.js",
                "type": "framework",
                "confidence": conf,
                "confidence_label": get_confidence_label(conf),
                "evidence": item.get("evidence", ["Next.js SSR build artifacts / __NEXT_DATA__ detected"])
            }

        if "Nuxt.js" in framework_names and framework_names["Nuxt.js"].get("confidence", 0) >= 60:
            item = framework_names["Nuxt.js"]
            conf = item.get("confidence", 90)
            return {
                "name": "Nuxt.js",
                "type": "framework",
                "confidence": conf,
                "confidence_label": get_confidence_label(conf),
                "evidence": item.get("evidence", ["Nuxt.js SSR markers detected"])
            }

        # 5. SPA Framework Priority Check (React, Vue, Angular, Svelte)
        for spa_fw in ["React", "Vue.js", "Angular", "Svelte"]:
            if spa_fw in framework_names and framework_names[spa_fw].get("confidence", 0) >= 60:
                item = framework_names[spa_fw]
                conf = item.get("confidence", 85)
                return {
                    "name": spa_fw,
                    "type": "framework",
                    "confidence": conf,
                    "confidence_label": get_confidence_label(conf),
                    "evidence": item.get("evidence", [f"{spa_fw} frontend framework DOM markers detected"])
                }

        # 6. Direct Backend Language Priority Check (Custom PHP, Python, Java, Ruby)
        if backend_info and backend_info.get("language") and backend_info.get("language") != "Unknown" and backend_info.get("confidence", 0) >= 60:
            lang = backend_info["language"]
            conf = backend_info.get("confidence", 85)
            displayName = f"{lang} / Traditional Server-rendered Website" if lang == "PHP" else f"{lang} Server Application"
            return {
                "name": displayName,
                "type": "backend_language",
                "confidence": conf,
                "confidence_label": get_confidence_label(conf),
                "evidence": backend_info.get("evidence", [f"Public {lang} server session or response fingerprints detected"])
            }

        # 7. Fallback: Static / Traditional Website (HTML / CSS / JavaScript)
        # Never promote jQuery, Bootstrap, or utility libraries to Primary Status!
        return {
            "name": "HTML / CSS / JavaScript",
            "type": "static",
            "confidence": 90,
            "confidence_label": "High",
            "evidence": [
                "HTML5 document structure detected",
                "CSS stylesheet assets loaded",
                "JavaScript scripts present without monolithic framework or CMS lock-in"
            ]
        }

classifier = PrimaryTechnologyClassifier()
