from typing import List, Dict, Any
from app.analyzer.confidence import SignalWeight, calculate_confidence

def detect_third_party_integrations(html: str, scripts: List[str], iframes: List[str]) -> List[Dict[str, Any]]:
    results = []
    html_lower = html.lower() if html else ""
    scripts_str = " ".join(scripts).lower()
    iframes_str = " ".join(iframes).lower()

    # 1. Google Maps
    if "maps.googleapis.com" in scripts_str or "google.com/maps/embed" in iframes_str:
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "Google Maps JavaScript API script or embedded iframe detected")])
        results.append({"name": "Google Maps", "category": "Maps & Location", "confidence": conf, "evidence": ev})

    # 2. reCAPTCHA
    if "google.com/recaptcha" in scripts_str or "g-recaptcha" in html_lower or "grecaptcha" in html_lower:
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "Google reCAPTCHA widget / script tag detected")])
        results.append({"name": "reCAPTCHA", "category": "Security / Spam Protection", "confidence": conf, "evidence": ev})

    # 3. YouTube Embed
    if "youtube.com/embed" in iframes_str or "youtube-nocookie.com" in iframes_str:
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "YouTube video player embedded iframe detected")])
        results.append({"name": "YouTube Video Player", "category": "Media", "confidence": conf, "evidence": ev})

    # 4. WhatsApp Widget / Link
    if "api.whatsapp.com/send" in html_lower or "wa.me/" in html_lower or "whatsapp" in scripts_str:
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "WhatsApp click-to-chat API widget/link detected")])
        results.append({"name": "WhatsApp Chat Widget", "category": "Communication", "confidence": conf, "evidence": ev})

    # 5. Stripe
    if "js.stripe.com" in scripts_str or "stripe" in html_lower:
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "Stripe Payment Gateway checkout JS library detected")])
        results.append({"name": "Stripe Payments", "category": "Payment Gateway", "confidence": conf, "evidence": ev})

    # 6. Razorpay
    if "checkout.razorpay.com" in scripts_str or "razorpay" in html_lower:
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "Razorpay Payment Gateway checkout script detected")])
        results.append({"name": "Razorpay Payments", "category": "Payment Gateway", "confidence": conf, "evidence": ev})

    # 7. Calendly
    if "assets.calendly.com" in scripts_str or "calendly-inline-widget" in html_lower:
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "Calendly appointment booking widget script detected")])
        results.append({"name": "Calendly", "category": "Scheduling", "confidence": conf, "evidence": ev})

    # 8. HubSpot
    if "js.hs-scripts.com" in scripts_str or "hubspot" in html_lower:
        conf, ev = calculate_confidence([(SignalWeight.STRONG, "HubSpot CRM & Marketing automation script tag detected")])
        results.append({"name": "HubSpot", "category": "CRM & Marketing", "confidence": conf, "evidence": ev})

    return results
