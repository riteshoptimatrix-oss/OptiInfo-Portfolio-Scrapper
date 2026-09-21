import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.analyzer.classifier import PrimaryTechnologyClassifier
from app.analyzer.detectors.backend import detect_backend_tech
from app.analyzer.detectors.cms import detect_cms
from app.analyzer.detectors.frontend import detect_frontend_tech
from app.analyzer.detectors.cdn import detect_cdn
from app.analyzer.detectors.hosting import detect_hosting_provider

class TestProductionAnalyzerRules(unittest.TestCase):
    def setUp(self):
        self.classifier = PrimaryTechnologyClassifier()

    def test_1_static_html_css_js(self):
        """Test Case 1: Pure Static HTML/CSS/JS"""
        html = "<html><head><title>Static Site</title><link rel='stylesheet' href='style.css'></head><body><h1>Hello World</h1><script src='app.js'></script></body></html>"
        cms = detect_cms(html, ["app.js"], ["style.css"], {}, {}, [])
        frontend = detect_frontend_tech(html, ["app.js"], {}, {})
        backend = detect_backend_tech(html, {}, {}, "https://example.com/", cms)
        
        primary = self.classifier.classify_primary_technology(cms, None, backend, frontend, [], html, ["app.js"])
        
        self.assertEqual(primary["name"], "HTML / CSS / JavaScript")
        self.assertEqual(primary["type"], "static")
        self.assertEqual(backend["status"], "Not publicly detectable")
        self.assertEqual(backend["language"], "Unknown")

    def test_2_static_with_jquery(self):
        """Test Case 2: Static HTML + jQuery (jQuery MUST NOT become primary)"""
        html = "<html><head><script src='https://code.jquery.com/jquery-3.6.0.min.js'></script></head><body></body></html>"
        cms = detect_cms(html, ["jquery-3.6.0.min.js"], [], {}, {}, [])
        frontend = detect_frontend_tech(html, ["jquery-3.6.0.min.js"], {}, {})
        backend = detect_backend_tech(html, {}, {}, "https://example.com/", cms)
        
        primary = self.classifier.classify_primary_technology(cms, None, backend, frontend, [], html, ["jquery-3.6.0.min.js"])
        
        self.assertEqual(primary["name"], "HTML / CSS / JavaScript")
        js_lib_names = [f["name"] for f in frontend if f.get("category") == "JavaScript Library"]
        self.assertIn("jQuery", js_lib_names)

    def test_3_wordpress_classification(self):
        """Test Case 3: WordPress CMS Detection & PHP Inference"""
        html = "<html><head><meta name='generator' content='WordPress 6.4'></head><body><script src='/wp-content/themes/theme/script.js'></script></body></html>"
        cms = detect_cms(html, ["/wp-content/themes/theme/script.js"], [], {}, {}, [{"name": "generator", "content": "WordPress 6.4"}])
        backend = detect_backend_tech(html, {}, {}, "https://example.com/", cms)
        
        primary = self.classifier.classify_primary_technology(cms, None, backend, [], [], html, [])
        
        self.assertEqual(primary["name"], "WordPress")
        self.assertEqual(primary["type"], "cms")
        self.assertEqual(backend["language"], "PHP")

    def test_4_wordpress_with_woocommerce(self):
        """Test Case 4: WordPress + WooCommerce (Primary: WordPress, E-Commerce: WooCommerce)"""
        html = "<html><head><meta name='generator' content='WordPress'></head><body class='woocommerce-page'></body></html>"
        cms = detect_cms(html, [], [], {}, {}, [{"name": "generator", "content": "WordPress"}])
        from app.analyzer.detectors.ecommerce import detect_ecommerce
        ecom = detect_ecommerce(html, [], [], {})
        
        primary = self.classifier.classify_primary_technology(cms, ecom, None, [], [], html, [])
        
        self.assertEqual(primary["name"], "WordPress")
        self.assertIsNotNone(ecom)
        self.assertEqual(ecom["name"], "WooCommerce")

    def test_5_custom_php_website(self):
        """Test Case 5: Custom PHP website without WordPress (Primary: PHP Server-rendered)"""
        html = "<html><body><form action='contact.php' method='POST'></form></body></html>"
        cookies = {"PHPSESSID": "abcdef123456"}
        headers = {"x-powered-by": "PHP/8.2.0"}
        cms = detect_cms(html, [], [], headers, cookies, [])
        backend = detect_backend_tech(html, headers, cookies, "https://example.com/index.php", cms)
        
        primary = self.classifier.classify_primary_technology(cms, None, backend, [], [], html, [])
        
        self.assertEqual(primary["name"], "PHP / Traditional Server-rendered Website")
        self.assertEqual(backend["language"], "PHP")

    def test_6_laravel_framework(self):
        """Test Case 6: Laravel Framework Detection"""
        cookies = {"laravel_session": "xyz", "XSRF-TOKEN": "abc"}
        backend = detect_backend_tech("", {}, cookies, "https://example.com/", None)
        
        primary = self.classifier.classify_primary_technology(None, None, backend, [], [], "", [])
        
        self.assertEqual(primary["name"], "Laravel")
        self.assertEqual(backend["framework"], "Laravel")
        self.assertEqual(backend["language"], "PHP")

    def test_7_nextjs_with_react(self):
        """Test Case 7: Next.js SSR Framework with React"""
        html = "<html><head></head><body><div id='__next'></div><script src='/_next/static/chunks/main.js'></script></body></html>"
        frontend = detect_frontend_tech(html, ["/_next/static/chunks/main.js"], {}, {})
        
        primary = self.classifier.classify_primary_technology(None, None, None, frontend, [], html, ["/_next/static/chunks/main.js"])
        
        self.assertEqual(primary["name"], "Next.js")
        fw_names = [f["name"] for f in frontend]
        self.assertIn("Next.js", fw_names)
        self.assertIn("React", fw_names)

    def test_8_cloudflare_cdn_hosting_separation(self):
        """Test Case 8: Cloudflare CDN / DNS vs Origin Hosting Separation"""
        headers = {"server": "cloudflare", "cf-ray": "859385938593-BOM"}
        cdn = detect_cdn(headers, {}, {})
        hosting = detect_hosting_provider(headers, {}, cdn)
        
        self.assertIsNotNone(cdn)
        self.assertEqual(cdn["name"], "Cloudflare CDN / Proxy")
        self.assertEqual(hosting["name"], "Unknown")
        self.assertEqual(hosting["reason"], "Website is behind Cloudflare CDN/Reverse Proxy which masks origin hosting provider.")

    def test_9_react_only_classification(self):
        """Test Case 9: React SPA Framework without Next.js"""
        html = "<html><body><div id='root' data-reactroot=''></div><script src='bundle.js'></script></body></html>"
        frontend = detect_frontend_tech(html, ["bundle.js"], {}, {"has_react_root": True})
        primary = self.classifier.classify_primary_technology(None, None, None, frontend, [], html, ["bundle.js"])
        
        self.assertEqual(primary["name"], "React")
        self.assertEqual(primary["type"], "framework")

    def test_10_vue_framework(self):
        """Test Case 10: Vue.js SPA Framework"""
        html = "<html><body><div id='app' data-v-123456></div><script src='vue.js'></script></body></html>"
        frontend = detect_frontend_tech(html, ["vue.js"], {}, {})
        primary = self.classifier.classify_primary_technology(None, None, None, frontend, [], html, ["vue.js"])
        
        self.assertEqual(primary["name"], "Vue.js")

    def test_11_django_framework(self):
        """Test Case 11: Django Backend Framework"""
        cookies = {"csrftoken": "secret_csrf_token"}
        backend = detect_backend_tech("", {}, cookies, "https://example.com/admin/", None)
        primary = self.classifier.classify_primary_technology(None, None, backend, [], [], "", [])
        
        self.assertEqual(primary["name"], "Django")
        self.assertEqual(backend["framework"], "Django")
        self.assertEqual(backend["language"], "Python")

    def test_12_static_with_bootstrap(self):
        """Test Case 12: Static HTML + Bootstrap CSS (Bootstrap MUST NOT become primary)"""
        html = "<html><head><link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'></head><body></body></html>"
        from app.analyzer.detectors.css import detect_css_frameworks
        css = detect_css_frameworks(html, ["bootstrap.min.css"], {})
        primary = self.classifier.classify_primary_technology(None, None, None, [], css, html, [])
        
        self.assertEqual(primary["name"], "HTML / CSS / JavaScript")
        self.assertEqual(css[0]["name"], "Bootstrap")
        self.assertEqual(css[0]["category"], "CSS Framework")

    def test_13_wordpress_with_jquery(self):
        """Test Case 13: WordPress + jQuery (WordPress is primary, jQuery is library)"""
        html = "<html><head><meta name='generator' content='WordPress 6.4'></head><body><script src='/wp-includes/js/jquery/jquery.min.js'></script></body></html>"
        cms = detect_cms(html, ["/wp-includes/js/jquery/jquery.min.js"], [], {}, {}, [{"name": "generator", "content": "WordPress 6.4"}])
        frontend = detect_frontend_tech(html, ["/wp-includes/js/jquery/jquery.min.js"], {}, {})
        backend = detect_backend_tech(html, {}, {}, "https://example.com/", cms)
        primary = self.classifier.classify_primary_technology(cms, None, backend, frontend, [], html, [])
        
        self.assertEqual(primary["name"], "WordPress")
        js_libs = [f["name"] for f in frontend if f.get("category") == "JavaScript Library"]
        self.assertIn("jQuery", js_libs)

if __name__ == "__main__":
    unittest.main()
