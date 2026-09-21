from typing import List, Dict, Any, Optional
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_ecommerce(html: str, scripts: List[str], stylesheets: List[str], cookies: Dict[str, str]) -> Optional[Dict[str, Any]]:
    html_lower = html.lower() if html else ""
    scripts_str = " ".join(scripts).lower()
    styles_str = " ".join(stylesheets).lower()

    # 1. WooCommerce
    wc_signals = []
    if "woocommerce" in html_lower or "woocommerce" in styles_str or "woocommerce" in scripts_str:
        wc_signals.append((SignalWeight.STRONG, "WooCommerce asset path or stylesheet reference detected"))
    if "wc-add-to-cart" in html_lower or "woocommerce-cart" in html_lower or "woocommerce-checkout" in html_lower:
        wc_signals.append((SignalWeight.STRONG, "WooCommerce DOM action class (wc-add-to-cart/woocommerce-cart) detected"))
    if wc_signals:
        conf, ev = calculate_confidence(wc_signals)
        return {"name": "WooCommerce", "category": "E-commerce Platform", "confidence": conf, "evidence": ev}

    # 2. Shopify
    shopify_signals = []
    if "cdn.shopify.com" in html_lower or "shopify" in scripts_str:
        shopify_signals.append((SignalWeight.STRONG, "Shopify CDN domain / asset structure detected"))
    if "shopify-pay" in html_lower or "shopify-checkout" in html_lower:
        shopify_signals.append((SignalWeight.STRONG, "Shopify Checkout DOM payment components detected"))
    if shopify_signals:
        conf, ev = calculate_confidence(shopify_signals)
        return {"name": "Shopify", "category": "E-commerce Platform", "confidence": conf, "evidence": ev}

    # 3. Magento / Adobe Commerce
    magento_signals = []
    if "mage/cookies.js" in scripts_str or "mage/template.js" in scripts_str or "skin/frontend/default" in html_lower:
        magento_signals.append((SignalWeight.STRONG, "Magento script asset path (mage/*.js) detected"))
    if "varien" in html_lower or "catalog/product/view" in html_lower:
        magento_signals.append((SignalWeight.MEDIUM, "Magento DOM JavaScript object (Varien) / view structure detected"))
    if magento_signals:
        conf, ev = calculate_confidence(magento_signals)
        return {"name": "Magento", "category": "E-commerce Platform", "confidence": conf, "evidence": ev}

    # 4. PrestaShop
    ps_signals = []
    if "prestashop" in html_lower or "prestashop" in scripts_str or "modules/ps_" in html_lower:
        ps_signals.append((SignalWeight.STRONG, "PrestaShop asset or module path (/modules/ps_) detected"))
    if ps_signals:
        conf, ev = calculate_confidence(ps_signals)
        return {"name": "PrestaShop", "category": "E-commerce Platform", "confidence": conf, "evidence": ev}

    # 5. OpenCart
    oc_signals = []
    if "catalog/view/theme" in html_lower and "index.php?route=checkout" in html_lower:
        oc_signals.append((SignalWeight.STRONG, "OpenCart URL routing structure and theme path detected"))
    if oc_signals:
        conf, ev = calculate_confidence(oc_signals)
        return {"name": "OpenCart", "category": "E-commerce Platform", "confidence": conf, "evidence": ev}

    return None
