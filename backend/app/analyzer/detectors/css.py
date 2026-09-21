from typing import List, Dict, Any
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_css_frameworks(html: str, stylesheets: List[str], dom_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    html_lower = html.lower() if html else ""
    styles_str = " ".join(stylesheets).lower()

    # 1. Tailwind CSS
    tailwind_signals = []
    if "tailwind" in styles_str or "tailwind.min.css" in styles_str:
        tailwind_signals.append((SignalWeight.STRONG, "Tailwind CSS stylesheet file path pattern detected"))
    # Check for characteristic utility class combinations in DOM
    tw_classes = ["flex ", "items-center", "justify-between", "grid-cols-", "px-", "py-", "text-sm", "bg-", "rounded-xl"]
    matched_classes = [c for c in tw_classes if c in html_lower]
    if len(matched_classes) >= 4:
        tailwind_signals.append((SignalWeight.STRONG, f"Multiple Tailwind CSS utility class combinations detected ({', '.join(matched_classes[:4])})"))
    if tailwind_signals:
        conf, ev = calculate_confidence(tailwind_signals)
        results.append({"name": "Tailwind CSS", "category": "CSS Framework", "confidence": conf, "evidence": ev})

    # 2. Bootstrap
    bs_signals = []
    if "bootstrap" in styles_str or "bootstrap.min.css" in styles_str or "bootstrap.bundle" in html_lower:
        bs_signals.append((SignalWeight.STRONG, "Bootstrap stylesheet / script asset path detected"))
    bs_classes = ["container-fluid", "col-md-", "col-lg-", "navbar-expand", "btn-primary", "card-body"]
    matched_bs = [c for c in bs_classes if c in html_lower]
    if len(matched_bs) >= 2:
        bs_signals.append((SignalWeight.STRONG, f"Bootstrap DOM grid class markers detected ({', '.join(matched_bs)})"))
    if bs_signals:
        conf, ev = calculate_confidence(bs_signals)
        results.append({"name": "Bootstrap", "category": "CSS Framework", "confidence": conf, "evidence": ev})

    # 3. Material UI (MUI)
    mui_signals = []
    if "MuiButton-" in html or "MuiTypography-" in html or "MuiGrid-" in html or "mui-" in html_lower:
        mui_signals.append((SignalWeight.STRONG, "Material UI (MUI) class prefix markers (MuiButton/MuiGrid) detected"))
    if mui_signals:
        conf, ev = calculate_confidence(mui_signals)
        results.append({"name": "Material UI (MUI)", "category": "UI Library", "confidence": conf, "evidence": ev})

    # 4. Font Awesome
    fa_signals = []
    if "font-awesome" in styles_str or "fontawesome" in styles_str or "cdnjs.cloudflare.com/ajax/libs/font-awesome" in html_lower:
        fa_signals.append((SignalWeight.STRONG, "Font Awesome stylesheet URL reference detected"))
    if "fa-" in html_lower or "fas " in html_lower or "fab " in html_lower or "far " in html_lower:
        fa_signals.append((SignalWeight.MEDIUM, "Font Awesome icon class attribute (fa-*) detected in DOM"))
    if fa_signals:
        conf, ev = calculate_confidence(fa_signals)
        results.append({"name": "Font Awesome", "category": "Icon Toolkit", "confidence": conf, "evidence": ev})

    # 5. Bulma
    bulma_signals = []
    if "bulma" in styles_str or "bulma.min.css" in styles_str:
        bulma_signals.append((SignalWeight.STRONG, "Bulma CSS stylesheet reference detected"))
    if "is-flex" in html_lower and "has-text-centered" in html_lower:
        bulma_signals.append((SignalWeight.MEDIUM, "Bulma class utility markers detected"))
    if bulma_signals:
        conf, ev = calculate_confidence(bulma_signals)
        results.append({"name": "Bulma", "category": "CSS Framework", "confidence": conf, "evidence": ev})

    return results
