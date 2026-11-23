import unittest
import json
from gemini_web2api.admin import parse_cookie_input

class TestUIAccounts(unittest.TestCase):
    def test_parse_cookie_editor_array(self):
        sample = [
            {"name": "__Secure-1PSID", "value": "test_psid_val", "domain": ".google.com"},
            {"name": "__Secure-1PSIDTS", "value": "test_ts_val", "domain": ".google.com"},
            {"name": "SAPISID", "value": "test_sapisid_val", "domain": ".google.com"},
            {"name": "other_ad_cookie", "value": "ignored", "domain": "adservice.googleadservices.com"}
        ]
        cookie_str, xsrf, auth_user, sapisid, bl = parse_cookie_input(sample, fallback_auth_user="1")
        self.assertIn("__Secure-1PSID=test_psid_val", cookie_str)
        self.assertIn("__Secure-1PSIDTS=test_ts_val", cookie_str)
        self.assertEqual(sapisid, "test_sapisid_val")
        self.assertEqual(auth_user, "1")

    def test_parse_raw_cookie_header(self):
        sample_str = "__Secure-1PSID=abc123; SAPISID=sap456; __Secure-1PSIDTS=ts789;"
        cookie_str, xsrf, auth_user, sapisid, bl = parse_cookie_input(sample_str, fallback_auth_user="0")
        self.assertIn("__Secure-1PSID=abc123", cookie_str)
        self.assertEqual(sapisid, "sap456")
        self.assertEqual(auth_user, "0")

    def test_parse_sync_object(self):
        sync_obj = {
            "cookie": "__Secure-1PSID=xyz;",
            "xsrf_token": "token123",
            "auth_user": "2",
            "sapisid": "sap789"
        }
        cookie_str, xsrf, auth_user, sapisid, bl = parse_cookie_input(sync_obj)
        self.assertEqual(cookie_str, "__Secure-1PSID=xyz;")
        self.assertEqual(xsrf, "token123")
        self.assertEqual(auth_user, "2")
        self.assertEqual(sapisid, "sap789")

if __name__ == "__main__":
    unittest.main()
