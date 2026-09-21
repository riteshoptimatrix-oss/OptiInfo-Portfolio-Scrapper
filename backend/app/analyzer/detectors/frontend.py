from typing import List, Dict, Any
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_frontend_tech(html: str, scripts: List[str], headers: Dict[str, str], dom_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    html_lower = html.lower() if html else ""
    scripts_str = " ".join(scripts).lower()

    # 1. Next.js
    next_signals = []
    if "/_next/static/" in html_lower or "/_next/static/" in scripts_str:
        next_signals.append((SignalWeight.STRONG, "Asset path containing /_next/static/ detected"))
    if "__NEXT_DATA__" in html or dom_info.get("has_next_data"):
        next_signals.append((SignalWeight.STRONG, "__NEXT_DATA__ script tag detected in DOM"))
    if "x-nextjs-page" in headers or "x-nextjs-cache" in headers:
        next_signals.append((SignalWeight.STRONG, "Next.js response header detected"))
    if next_signals:
        conf, ev = calculate_confidence(next_signals)
        results.append({"name": "Next.js", "category": "Framework", "confidence": conf, "evidence": ev})

    # 2. React
    react_signals = []
    if "react" in html_lower or "react-dom" in html_lower or "react" in scripts_str:
        react_signals.append((SignalWeight.MEDIUM, "React library script reference detected"))
    if dom_info.get("has_react_root") or "data-reactroot" in html_lower or "_reactlistening" in html_lower:
        react_signals.append((SignalWeight.STRONG, "React DOM root attribute / event listener marker detected"))
    if next_signals: # Next.js implies React
        react_signals.append((SignalWeight.STRONG, "Next.js framework present (built on React)"))
    if react_signals:
        conf, ev = calculate_confidence(react_signals)
        results.append({"name": "React", "category": "Frontend Library", "confidence": conf, "evidence": ev})

    # 3. Vue.js
    vue_signals = []
    if "/_nuxt/" in html_lower or "v-data-" in html_lower or "data-v-" in html_lower:
        vue_signals.append((SignalWeight.STRONG, "Vue.js DOM scoped attribute (data-v-*) detected"))
    if "vue" in scripts_str or "vue.js" in scripts_str or "vue.min.js" in scripts_str:
        vue_signals.append((SignalWeight.MEDIUM, "Vue.js script asset URL pattern detected"))
    if dom_info.get("has_vue_attr"):
        vue_signals.append((SignalWeight.STRONG, "Vue instance property found on root element"))
    if vue_signals:
        conf, ev = calculate_confidence(vue_signals)
        results.append({"name": "Vue.js", "category": "Frontend Framework", "confidence": conf, "evidence": ev})

    # 4. Nuxt.js
    nuxt_signals = []
    if "/_nuxt/" in html_lower or "/_nuxt/" in scripts_str:
        nuxt_signals.append((SignalWeight.STRONG, "Asset path containing /_nuxt/ detected"))
    if "__NUXT__" in html or dom_info.get("has_nuxt_data"):
        nuxt_signals.append((SignalWeight.STRONG, "__NUXT__ window state payload detected"))
    if nuxt_signals:
        conf, ev = calculate_confidence(nuxt_signals)
        results.append({"name": "Nuxt.js", "category": "Framework", "confidence": conf, "evidence": ev})

    # 5. Angular
    ng_signals = []
    if "ng-version" in html_lower or dom_info.get("has_angular"):
        ng_signals.append((SignalWeight.STRONG, "Angular ng-version attribute detected in DOM"))
    if "ng-app" in html_lower or "ng-controller" in html_lower:
        ng_signals.append((SignalWeight.STRONG, "AngularJS ng-app directive attribute detected"))
    if "angular" in scripts_str:
        ng_signals.append((SignalWeight.MEDIUM, "Angular script file asset pattern detected"))
    if ng_signals:
        conf, ev = calculate_confidence(ng_signals)
        results.append({"name": "Angular", "category": "Frontend Framework", "confidence": conf, "evidence": ev})

    # 6. jQuery
    jq_signals = []
    if "jquery" in scripts_str or "jquery.min.js" in scripts_str or "jquery-" in scripts_str:
        jq_signals.append((SignalWeight.STRONG, "jQuery script asset path pattern detected"))
    if "jquery" in html_lower or "code.jquery.com" in html_lower:
        jq_signals.append((SignalWeight.MEDIUM, "jQuery CDN URL reference detected"))
    if jq_signals:
        conf, ev = calculate_confidence(jq_signals)
        results.append({"name": "jQuery", "category": "JavaScript Library", "confidence": conf, "evidence": ev})

    # 7. Svelte
    svelte_signals = []
    if "svelte-" in html_lower or "class=\"svelte-" in html_lower:
        svelte_signals.append((SignalWeight.STRONG, "Svelte scoped CSS class name pattern detected"))
    if "svelte" in scripts_str:
        svelte_signals.append((SignalWeight.MEDIUM, "Svelte runtime script asset reference detected"))
    if svelte_signals:
        conf, ev = calculate_confidence(svelte_signals)
        results.append({"name": "Svelte", "category": "Frontend Framework", "confidence": conf, "evidence": ev})

    # 8. Alpine.js
    alpine_signals = []
    if "x-data=" in html_lower or "x-init=" in html_lower or "x-show=" in html_lower:
        alpine_signals.append((SignalWeight.STRONG, "Alpine.js directive attribute (x-data/x-init) detected"))
    if "alpine" in scripts_str:
        alpine_signals.append((SignalWeight.MEDIUM, "Alpine.js script asset path detected"))
    if alpine_signals:
        conf, ev = calculate_confidence(alpine_signals)
        results.append({"name": "Alpine.js", "category": "JavaScript Framework", "confidence": conf, "evidence": ev})

    # 9. GSAP (GreenSock)
    gsap_signals = []
    if "gsap" in scripts_str or "greensock" in scripts_str or "ScrollTrigger" in scripts_str:
        gsap_signals.append((SignalWeight.STRONG, "GSAP (GreenSock Animation Platform) script asset pattern detected"))
    if gsap_signals:
        conf, ev = calculate_confidence(gsap_signals)
        results.append({"name": "GSAP (GreenSock)", "category": "Animation Library", "confidence": conf, "evidence": ev})

    # 10. Lodash / Underscore
    lodash_signals = []
    if "lodash" in scripts_str or "lodash.min.js" in scripts_str:
        lodash_signals.append((SignalWeight.STRONG, "Lodash utility library script reference detected"))
    if lodash_signals:
        conf, ev = calculate_confidence(lodash_signals)
        results.append({"name": "Lodash", "category": "JavaScript Library", "confidence": conf, "evidence": ev})

    # 11. Vanilla JS (Default fallback signal if script tags exist)
    if not results and len(scripts) > 0:
        results.append({
            "name": "Vanilla JavaScript",
            "category": "Core Language",
            "confidence": 95,
            "evidence": [f"Page contains {len(scripts)} custom script tag(s) without heavy framework signatures"]
        })

    return results
