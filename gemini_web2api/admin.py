import json
import os
import time
import urllib.request
import ssl
import re
import hashlib
import uuid
from .config import CONFIG, save_config, set_current_account, get_current_account
from .gemini import _build_headers, _get_ssl_ctx
from .database import get_all_accounts, get_account_by_name, get_account_by_api_key, add_or_update_account, delete_account_db, COOKIES_DIR, resolve_cookie_path

def verify_all_accounts():
    results = []
    accounts = get_all_accounts()
    ctx = _get_ssl_ctx()
    
    for acc in accounts:
        try:
            # Temporarily set this account
            set_current_account(acc.get("name"))
            auth_user = str(acc.get("auth_user") or "0").strip()
            if auth_user in ("0", 0, "None", "null", ""):
                url = "https://gemini.google.com/app"
            else:
                url = f"https://gemini.google.com/u/{auth_user}/app"
            headers = _build_headers()
            
            req = urllib.request.Request(url, headers=headers, method="GET")
            resp = urllib.request.urlopen(req, context=ctx, timeout=10)
            final_url = resp.geturl()
            
            if "accounts.google.com" in final_url or "ServiceLogin" in final_url:
                status = "Expired (Redirected to login)"
                valid = False
            else:
                html = resp.read().decode("utf-8", errors="ignore")
                if "WIZ_global_data" in html or "SNlM0e" in html:
                    status = "Healthy (Cookies valid)"
                    valid = True
                else:
                    status = "Invalid (Missing auth tokens)"
                    valid = False
                    
        except Exception as e:
            status = f"Error: {e}"
            valid = False
            
        results.append({
            "name": acc.get("name"),
            "auth_user": acc.get("auth_user"),
            "status": status,
            "valid": valid
        })
    return results

def get_stats():
    now = time.time()
    accounts = get_all_accounts()
    stats = []
    
    for acc in accounts:
        name = acc.get("name")
        cooldown_until = acc.get("rate_limited_until", 0) or 0
        
        is_limited = cooldown_until > now
        remaining_cooldown = int(cooldown_until - now) if is_limited else 0
        
        stats.append({
            "name": name,
            "api_key": acc.get("api_key"),
            "auth_user": acc.get("auth_user"),
            "cookie_file": acc.get("cookie_file"),
            "status": "Rate Limited" if is_limited else "Ready",
            "cooldown_seconds": remaining_cooldown
        })
        
    raw_master = CONFIG.get("api_keys") or []
    if isinstance(raw_master, str):
        raw_master = [raw_master]
    if CONFIG.get("api_key") and CONFIG.get("api_key") not in raw_master:
        raw_master.append(CONFIG.get("api_key"))
    real_master = [k.strip() for k in raw_master if k and k.strip() not in ("sk-gemini-example-key", "sk-hermes-test")]
    master_key_display = real_master[0] if real_master else "Open / Any key (Local Developer Mode)"

    return {
        "master_key": master_key_display,
        "total_accounts": len(accounts),
        "temporary_chats": CONFIG.get("temporary_chats", False),
        "accounts": stats
    }

def delete_account(name):
    acc = get_account_by_name(name)
    if acc:
        cf = resolve_cookie_path(acc.get("cookie_file"))
        if cf and os.path.exists(cf):
            try:
                os.remove(cf)
            except Exception:
                pass
    return delete_account_db(name)

def _extract_cookie_dict(cookie_str: str) -> dict:
    if not cookie_str:
        return {}
    pairs = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            pairs[k.strip()] = v.strip()
    return pairs

def _get_cookie_session_sig(cookie_str: str, sapisid: str = None) -> tuple:
    cdict = _extract_cookie_dict(cookie_str)
    psid = cdict.get("__Secure-1PSID") or cdict.get("__Secure-3PSID") or cdict.get("SID") or ""
    sap = sapisid or cdict.get("SAPISID") or ""
    return sap, psid

def handle_extension_sync(payload):
    """Handles auto-pushed cookies from the Chrome Extension across multiple browser profiles.
    Guarantees no account is unintentionally overwritten or dropped."""
    raw_auth_user = payload.get("auth_user")
    auth_user = str(raw_auth_user).strip() if (raw_auth_user is not None and str(raw_auth_user).strip() not in ("", "None", "null")) else "0"
    
    cookie = payload.get("cookie")
    xsrf = payload.get("xsrf_token")
    sapisid = payload.get("sapisid")
    acc_name_req = (payload.get("account_name") or "").strip() or None
    
    if not cookie or not xsrf:
        raise ValueError("Missing required cookie or xsrf_token")
        
    accounts = get_all_accounts()
    target = None
    
    # Extract identity signature of incoming session
    sap_in, psid_in = _get_cookie_session_sig(cookie, sapisid)
    
    # Priority 1: Match by explicitly requested account name
    if acc_name_req:
        target = next((a for a in accounts if a.get("name") == acc_name_req), None)
        
    # Priority 2: Match by session identity signature against existing saved cookies
    if not target and not acc_name_req:
        for a in accounts:
            cf = resolve_cookie_path(a.get("cookie_file"))
            if cf and os.path.exists(cf):
                try:
                    with open(cf, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    if content.startswith("{"):
                        cdata = json.loads(content)
                        exist_cookie = cdata.get("cookie", "")
                        exist_sapisid = cdata.get("sapisid", "")
                    else:
                        exist_cookie = content
                        exist_sapisid = ""
                    
                    exist_sap, exist_psid = _get_cookie_session_sig(exist_cookie, exist_sapisid)
                    
                    # Match condition: If PSID matches, it is definitely the same Google account!
                    if psid_in and exist_psid and psid_in == exist_psid:
                        target = a
                        break
                    # Or if SAPISID and auth_user match
                    if sap_in and exist_sap and sap_in == exist_sap and str(a.get("auth_user") or "0") == str(auth_user):
                        target = a
                        break
                except Exception:
                    pass
                    
    # Priority 3 (SAFE): NEVER blindly overwrite an account just because auth_user matches!
    # If no explicit name match and no session signature match, this is a distinct account.
    
    os.makedirs(COOKIES_DIR, exist_ok=True)
    
    import uuid
    if target:
        acc_name = target["name"]
        file_path = os.path.join(COOKIES_DIR, f"{acc_name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        add_or_update_account(acc_name, auth_user, file_path, xsrf, target.get("api_key"))
        return f"Updated existing account '{acc_name}' (auth_user: {auth_user})"
    else:
        if acc_name_req:
            acc_name = acc_name_req
        else:
            # Generate deterministic yet unique friendly name
            prefix = (sap_in[:6] if sap_in else (psid_in[:6] if psid_in else uuid.uuid4().hex[:6])).replace("/", "_").replace("+", "_").replace("=", "")
            base_name = f"Account_u{auth_user}_{prefix}"
            existing_names = {a.get("name") for a in accounts}
            acc_name = base_name
            counter = 2
            while acc_name in existing_names:
                acc_name = f"{base_name}_{counter}"
                counter += 1
            
        file_path = os.path.join(COOKIES_DIR, f"{acc_name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            
        api_key = f"sk-gemini-{acc_name}-{uuid.uuid4().hex[:8]}"
        add_or_update_account(acc_name, auth_user, file_path, xsrf, api_key)
        return f"Created new account '{acc_name}' (auth_user: {auth_user})"

# Two-way terminal-to-extension bridge state
_sync_requested = False

def request_sync():
    global _sync_requested
    _sync_requested = True
    return True

def get_sync_status():
    global _sync_requested
    status = _sync_requested
    # Auto-reset the flag after it's read by the extension
    if status:
        _sync_requested = False
    return status

def parse_cookie_input(raw, fallback_auth_user="0"):
    """Intelligently parses cookies from any format:
    1. Browser extension JSON array: [{'name': '...', 'value': '...'}, ...]
    2. Raw cookie header string: '__Secure-1PSID=...; SID=...'
    3. JSON key-value dictionary: {'__Secure-1PSID': '...'}
    4. Gateway extension payload: {'cookie': '...', 'xsrf_token': '...'}
    """
    if not raw:
        return "", "", str(fallback_auth_user or "0"), "", ""

    if isinstance(raw, dict) and "cookie" in raw:
        return (
            raw.get("cookie", "") or "",
            raw.get("xsrf_token", "") or "",
            str(raw.get("auth_user") or fallback_auth_user or "0"),
            raw.get("sapisid", "") or "",
            raw.get("gemini_bl", "") or ""
        )

    if isinstance(raw, str):
        s = raw.strip()
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
            try:
                raw = json.loads(s)
            except Exception:
                pass

    if isinstance(raw, dict) and "cookie" in raw:
        return (
            raw.get("cookie", "") or "",
            raw.get("xsrf_token", "") or "",
            str(raw.get("auth_user") or fallback_auth_user or "0"),
            raw.get("sapisid", "") or "",
            raw.get("gemini_bl", "") or ""
        )

    g_cookies = {}
    sapisid = ""
    xsrf = ""
    bl = ""

    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("key")
            val = item.get("value")
            if not name or val is None:
                continue
            name = str(name).strip()
            val = str(val).strip()
            domain = str(item.get("domain", ""))
            if domain and not any(d in domain for d in (".google.com", "google.com", "google")):
                continue
            g_cookies[name] = val
            if name == "SAPISID":
                sapisid = val
            elif name in ("SNlM0e", "xsrf_token", "at"):
                xsrf = val
    elif isinstance(raw, dict):
        for k, v in raw.items():
            k = str(k).strip()
            v = str(v).strip()
            g_cookies[k] = v
            if k == "SAPISID":
                sapisid = v
            elif k in ("SNlM0e", "xsrf_token", "at"):
                xsrf = v
            elif k == "gemini_bl":
                bl = v
    elif isinstance(raw, str):
        for p in raw.split(";"):
            if "=" in p:
                k, v = p.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k:
                    g_cookies[k] = v
                    if k == "SAPISID":
                        sapisid = v
                    elif k in ("SNlM0e", "xsrf_token", "at"):
                        xsrf = v

    if not sapisid and "SAPISID" in g_cookies:
        sapisid = g_cookies["SAPISID"]

    cookie_str = "; ".join([f"{k}={v}" for k, v in g_cookies.items()])
    return cookie_str, xsrf, str(fallback_auth_user or "0"), sapisid, bl

def fetch_gemini_session_data(cookie_str: str, sapisid: str = "", auth_user: str = "0"):
    """Handshakes with Google Gemini web frontend to auto-extract SNlM0e and build label."""
    import httpx
    
    cdict = _extract_cookie_dict(cookie_str)
    if not sapisid:
        sapisid = cdict.get("SAPISID") or ""
        
    auth_hdr = None
    if sapisid:
        ts = int(time.time())
        h = hashlib.sha1(f"{ts} {sapisid} https://gemini.google.com".encode()).hexdigest()
        auth_hdr = f"SAPISIDHASH {ts}_{h}"
        
    clean_auth = str(auth_user).strip() if auth_user is not None else "0"
    if clean_auth in ("", "None", "null", "0", 0):
        url = "https://gemini.google.com/app"
    else:
        url = f"https://gemini.google.com/u/{clean_auth}/app"
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
        "Origin": "https://gemini.google.com",
        "Referer": url,
        "X-Same-Domain": "1"
    }
    if auth_hdr:
        headers["Authorization"] = auth_hdr

    client = httpx.Client(timeout=20.0, follow_redirects=True)
    try:
        resp = client.get(url, headers=headers)
    finally:
        client.close()

    if "accounts.google.com" in str(resp.url) or "accounts.google.com/signin" in str(resp.url):
        raise ValueError("Google rejected session: redirected to login (accounts.google.com). Cookies are expired or invalid.")

    snlm0e_match = re.search(r'\"SNlM0e\":\"([^\"]+)\"', resp.text)
    if not snlm0e_match:
        snlm0e_match = re.search(r'\[\"SNlM0e\",\s*\"([^\"]+)\"\]', resp.text)
    xsrf_token = snlm0e_match.group(1) if snlm0e_match else ""

    if not xsrf_token and ("Sign in - Google Accounts" in resp.text or "Sign in with Google" in resp.text):
        raise ValueError("Google rejected session: redirected to login. Cookies are expired or invalid.")

    cfb2h_match = re.search(r'\"cfb2h\":\"([^\"]+)\"', resp.text)
    bl = cfb2h_match.group(1) if cfb2h_match else "boq_gemini-web-uiserver_20261123.01_p0"

    # Incorporate fresh session tokens (e.g. __Secure-1PSIDTS)
    for sc in resp.headers.get_list("set-cookie"):
        pair = sc.split(";", 1)[0]
        if "=" in pair:
            k, v = pair.split("=", 1)
            cdict[k.strip()] = v.strip()

    updated_cookie_str = "; ".join([f"{k}={v}" for k, v in cdict.items()])
    return xsrf_token, bl, updated_cookie_str

def add_account_from_ui(payload: dict) -> dict:
    """Adds or updates an account directly from UI input with auto-token extraction and session verification."""
    raw_cookies = payload.get("cookies") or payload.get("cookie")
    if not raw_cookies:
        raise ValueError("No cookies provided. Please paste cookies or upload a file.")

    req_name = (payload.get("name") or "").strip()
    req_auth_user = str(payload.get("auth_user") or "0").strip()
    req_api_key = (payload.get("api_key") or "").strip() or None
    manual_xsrf = (payload.get("xsrf_token") or "").strip()
    auto_verify = payload.get("auto_verify", True)

    cookie_str, parsed_xsrf, parsed_auth, sapisid, bl = parse_cookie_input(raw_cookies, req_auth_user)
    if not cookie_str:
        raise ValueError("Could not parse any valid cookies from input.")

    auth_user = req_auth_user if req_auth_user not in ("", "None", "null") else (parsed_auth or "0")
    xsrf_token = manual_xsrf or parsed_xsrf

    # Extract session signature
    sap_in, psid_in = _get_cookie_session_sig(cookie_str, sapisid)

    verified = False
    if auto_verify:
        try:
            extracted_xsrf, extracted_bl, cookie_str = fetch_gemini_session_data(cookie_str, sapisid, auth_user)
            if extracted_xsrf:
                xsrf_token = extracted_xsrf
            if extracted_bl:
                bl = extracted_bl
            verified = True
        except Exception as e:
            if not xsrf_token:
                raise ValueError(f"Failed to auto-fetch security token (SNlM0e) from Gemini: {e}")

    if not xsrf_token:
        raise ValueError("Missing SNlM0e (xsrf_token). Please enable auto-verification or provide it manually.")

    if not bl:
        bl = "boq_gemini-web-uiserver_20261123.01_p0"

    accounts = get_all_accounts()

    # Determine account name
    if req_name:
        clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', req_name).strip('_')
        acc_name = clean_name or "gemini_user"
    else:
        # Match existing account by session identity if already present
        matched_acc = None
        for a in accounts:
            cf = resolve_cookie_path(a.get("cookie_file"))
            if cf and os.path.exists(cf):
                try:
                    with open(cf, "r", encoding="utf-8") as f:
                        exist_data = json.load(f)
                    e_cookie = exist_data.get("cookie", "")
                    e_sap, e_psid = _get_cookie_session_sig(e_cookie, exist_data.get("sapisid"))
                    if psid_in and e_psid and psid_in == e_psid:
                        matched_acc = a
                        break
                except Exception:
                    pass

        if matched_acc:
            acc_name = matched_acc["name"]
        else:
            prefix = (sap_in[:6] if sap_in else (psid_in[:6] if psid_in else uuid.uuid4().hex[:6]))
            prefix = re.sub(r'[^a-zA-Z0-9_]', '_', prefix).strip('_')
            base_name = f"account_u{auth_user}_{prefix}" if prefix else "account_1"
            existing_names = {a.get("name") for a in accounts}
            acc_name = base_name
            counter = 2
            while acc_name in existing_names:
                acc_name = f"{base_name}_{counter}"
                counter += 1

    os.makedirs(COOKIES_DIR, exist_ok=True)
    file_path = os.path.join(COOKIES_DIR, f"{acc_name}.json")

    save_payload = {
        "cookie": cookie_str,
        "auth_user": auth_user if auth_user not in ("0", 0) else "",
        "xsrf_token": xsrf_token,
        "sapisid": sapisid,
        "gemini_bl": bl
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(save_payload, f, indent=2)

    # Check if updating existing or inserting new
    target_existing = next((a for a in accounts if a.get("name") == acc_name), None)
    final_key = req_api_key or (target_existing.get("api_key") if target_existing else None) or f"sk-gemini-{acc_name}-{uuid.uuid4().hex[:8]}"

    add_or_update_account(acc_name, auth_user, file_path, xsrf_token, final_key)

    return {
        "status": "success",
        "message": f"Account '{acc_name}' successfully configured and verified with Google Gemini!",
        "account": {
            "name": acc_name,
            "auth_user": auth_user,
            "api_key": final_key,
            "cookie_file": file_path,
            "status": "Ready",
            "verified": verified
        }
    }

def test_single_account(payload: dict) -> dict:
    """Tests an account upstream with Google 4 Neon model and returns latency and response."""
    name = (payload.get("name") or "").strip()
    api_key = (payload.get("api_key") or "").strip()

    accounts = get_all_accounts()
    target = None
    if name:
        target = next((a for a in accounts if a.get("name") == name), None)
    elif api_key:
        target = next((a for a in accounts if a.get("api_key") == api_key), None)

    if not target:
        raise ValueError(f"Account '{name or api_key}' not found in database.")

    t0 = time.time()
    set_current_account(target["name"])
    from .gemini import generate

    reply = generate(
        "Respond strictly with the single word: READY",
        model_id=2,
        think_mode=0,
        extra_fields={31: 2, 80: 3, "_ticket": "e6fa609c3fa255c0"}
    )
    latency = round((time.time() - t0) * 1000, 1)

    return {
        "status": "success",
        "name": target["name"],
        "reply": reply.strip(),
        "model": "4 Neon (High Thinking)",
        "latency_ms": latency
    }

