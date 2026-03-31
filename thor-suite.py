import customtkinter as ctk
import threading
import socket
import requests
import urllib.parse
import time
import re
import subprocess
from bs4 import BeautifulSoup
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class H4ckthorHub(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FULL PENETRATION TESTER SUITE - MONSTER EDITION")
        self.geometry("1550x980")
        
        self.is_running = {}
        self.found_urls = set()
        self.agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) H4ckthorHub/8.0 (Monster)'}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR  ---
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color="#010101")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="H4CKTHOR HUB", font=("Orbitron", 30, "bold"), text_color="#00FF00").pack(pady=20)
        
        # --- PASSIVE RECON  ---
        ctk.CTkLabel(self.sidebar, text="--- PASSIVE RECON ---", font=("Courier New", 13, "bold"), text_color="#555555").pack(pady=5)
        self.passive_items = [
            ("VIP: Super Fast Port Scan", "port"),
            ("VIP: Reverse IP Lookup", "rev"),
            ("VIP: Subdomain Finder", "sub"),
            ("VIP: WAF Detector", "waf"),
            ("VIP: JS Secret Leaks", "js")
        ]
        self.create_menu_buttons(self.passive_items, "#004d40")

        # --- ACTIVE ATTACK  ---
        ctk.CTkLabel(self.sidebar, text="--- ACTIVE ATTACK ---", font=("Courier New", 13, "bold"), text_color="#555555").pack(pady=10)
        self.active_items = [
            ("VIP: Auto-Crawler Pro", "crawl"),
            ("VIP: Mass Shell Hunter", "shell"),
            ("VIP: SQLi Auto-Tester", "sqli"),    
            ("VIP: Admin Panel Finder", "admin")
        ]
        self.create_menu_buttons(self.active_items, "#b71c1c")

        # --- UTILS ---
        ctk.CTkLabel(self.sidebar, text="--- SYSTEM UTILS ---", font=("Courier New", 13, "bold"), text_color="#555555").pack(pady=10)
        self.util_items = [
            ("SUPER VIP: Exploit Architect (AI)", "arch"),
            ("[i]> Generate Report", "report")
        ]
        self.create_menu_buttons(self.util_items, "#1a237e")
        
        self.setup_frames()
        self.show_page("port")

    def create_menu_buttons(self, items, hover_color):
        for text, pid in items:
            self.is_running[pid] = False
            btn = ctk.CTkButton(self.sidebar, text=text, command=lambda p=pid: self.show_page(p), 
                          height=42, font=("Courier New", 13, "bold"), fg_color="transparent", 
                          hover_color=hover_color, border_width=1, border_color="#00FF00")
            btn.pack(pady=3, padx=20, fill="x")

    def setup_frames(self):
        all_items = self.passive_items + self.active_items + self.util_items
        self.pages = {}
        for name, pid in all_items:
            frame = ctk.CTkFrame(self, corner_radius=25, fg_color="#050505", border_width=1, border_color="#00FF00")
            frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(frame, text=f"// {name.upper()} //", font=("Orbitron", 22, "bold"), text_color="#00FF00").pack(pady=10)
            
            st_lbl = ctk.CTkLabel(frame, text="STATUS: READY", font=("Courier New", 12), text_color="#555555")
            st_lbl.pack()
            setattr(self, f"{pid}_status", st_lbl)

            ent = ctk.CTkEntry(frame, placeholder_text="Target URL or IP (e.g. http://target.com)", width=700, height=45, fg_color="#0a0a0a", border_color="#00FF00")
            ent.pack(pady=10)
            setattr(self, f"{pid}_ent", ent)

            txt = ctk.CTkTextbox(frame, font=("Courier New", 15), border_width=1, border_color="#004d40", fg_color="#010101", text_color="#00FF00")
            txt.pack(padx=30, pady=10, fill="both", expand=True)
            setattr(self, f"{pid}_res", txt)

            btn = ctk.CTkButton(frame, text="RUN H4CKTHOR ENGINE", command=getattr(self, f"start_{pid}"), fg_color="#1b5e20", height=45, font=("Orbitron", 13, "bold"))
            btn.pack(pady=15)
            self.pages[pid] = frame

    def show_page(self, pid):
        for p in self.pages.values(): p.grid_forget()
        self.pages[pid].grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

    def animate(self, pid):
        chars = ["◐", "◓", "◑", "◒"]
        idx = 0
        while self.is_running.get(pid, False):
            try:
                getattr(self, f"{pid}_status").configure(text=f"H4CKTHOR RUNNING {chars[idx]}", text_color="#00FF00")
                idx = (idx + 1) % len(chars)
                time.sleep(0.1)
            except: break
        try: getattr(self, f"{pid}_status").configure(text="ENGINE STOPPED ✓", text_color="cyan")
        except: pass

    # --- 1. ADVANCED PORT SCAN ---
    def start_port(self):
        t = self.port_ent.get().strip().replace("http://", "").replace("https://", "").split("/")[0]
        self.port_res.delete("1.0", "end")
        self.is_running["port"] = True
        threading.Thread(target=self.animate, args=("port",), daemon=True).start()
        def run():
            self.port_res.insert("end", f"[*] Scanning IP/Host: {t}\n[*] Attempting Service Banner Grabbing...\n" + "="*60 + "\n")
            common_ports = {21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3", 443: "HTTPS", 3306: "MySQL", 8080: "Proxy", 8443: "HTTPS-Alt"}
            for p, svc in common_ports.items():
                if not self.is_running["port"]: break
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2.0)
                    if s.connect_ex((t, p)) == 0:
                        banner = "No Banner"
                        try:
                            if p in [80, 443, 8080, 8443]:
                                req_url = f"http{'s' if p in [443,8443] else ''}://{t}:{p}"
                                r = requests.get(req_url, timeout=2, verify=False)
                                banner = r.headers.get("Server", "Unknown Web Server")
                            else:
                                s.send(b"\r\n")
                                banner = s.recv(1024).decode(errors='ignore').strip().split('\n')[0][:40]
                        except: pass
                        self.port_res.insert("end", f"[+] Port {p:<5} | {svc:<10} | {banner}\n")
                        self.port_res.see("end")
                    s.close()
                except: pass
            self.port_res.insert("end", "\n[*] Port Scan Finished.")
            self.is_running["port"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 2. REVERSE IP LOOKUP ---
    def start_rev(self):
        t = self.rev_ent.get().strip().replace("http://", "").replace("https://", "").split("/")[0]
        self.rev_res.delete("1.0", "end")
        self.is_running["rev"] = True
        threading.Thread(target=self.animate, args=("rev",), daemon=True).start()
        def run():
            try:
                self.rev_res.insert("end", f"[*] Reverse IP Lookup for: {t}\n" + "-"*50 + "\n")
                r = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={t}", timeout=10)
                self.rev_res.insert("end", r.text if "API count exceeded" not in r.text else "[-] API Limit Exceeded.")
            except Exception as e: self.rev_res.insert("end", f"[-] API Error: {e}")
            self.is_running["rev"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 3. SUBDOMAIN FINDER ---
    def start_sub(self):
        d = self.sub_ent.get().strip().replace("http://", "").replace("https://", "").split("/")[0]
        self.sub_res.delete("1.0", "end")
        self.is_running["sub"] = True
        threading.Thread(target=self.animate, args=("sub",), daemon=True).start()
        def run():
            try:
                self.sub_res.insert("end", f"[*] Fetching Subdomains for: {d}\n" + "-"*50 + "\n")
                r = requests.get(f"https://api.hackertarget.com/hostsearch/?q={d}", timeout=10)
                self.sub_res.insert("end", r.text if "API count exceeded" not in r.text else "[-] API Limit Exceeded.")
            except Exception as e: self.sub_res.insert("end", f"[-] Error: {e}")
            self.is_running["sub"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 4. AUTO-CRAWLER PRO ---
    def start_crawl(self):
        u = self.crawl_ent.get().strip()
        if not u.startswith("http"): u = "http://" + u
        self.crawl_res.delete("1.0", "end")
        self.is_running["crawl"] = True
        self.found_urls.clear()
        threading.Thread(target=self.animate, args=("crawl",), daemon=True).start()
        def run():
            try:
                r = requests.get(u, headers=self.agent, timeout=7, verify=False)
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    link = urllib.parse.urljoin(u, a['href'])
                    if u.split("//")[1] in link and link not in self.found_urls:
                        self.found_urls.add(link)
                        self.crawl_res.insert("end", f"{'[!] PARAMETER: ' if '?' in link else '[+] FOUND: '}{link}\n")
                        self.crawl_res.see("end")
            except Exception as e: self.crawl_res.insert("end", f"[-] Error: {e}")
            self.crawl_res.insert("end", f"\n[*] Total Found: {len(self.found_urls)}")
            self.is_running["crawl"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 5. MASS SHELL HUNTER ---
    def start_shell(self):
        u = self.shell_ent.get().strip()
        if not u.startswith("http"): u = "http://" + u
        self.shell_res.delete("1.0", "end")
        self.is_running["shell"] = True
        threading.Thread(target=self.animate, args=("shell",), daemon=True).start()
        def run():
            paths = ["/upload.php", "/admin/upload.php", "/v1/upload", "/includes/upload.php", "/wp-content/plugins/simple-file-upload/upload.php", "/assets/upload.php", "/images/upload.php", "/file_upload.php", "/api/upload"]
            for p in paths:
                if not self.is_running["shell"]: break
                try:
                    check_url = u.rstrip('/') + p
                    r = requests.get(check_url, headers=self.agent, timeout=3, verify=False)
                    if r.status_code == 200 and ('type="file"' in r.text or 'multipart' in r.text.lower()):
                        self.shell_res.insert("end", f"[!!!] CRITICAL UPLOAD FOUND: {check_url}\n")
                    else: self.shell_res.insert("end", f"[-] Checked: {p} (Not Found)\n")
                    self.shell_res.see("end")
                except: pass
            self.is_running["shell"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 6. SQLi AUTO-TESTER ---
    def start_sqli(self):
        u = self.sqli_ent.get().strip()
        if not u.startswith("http"): u = "http://" + u
        self.sqli_res.delete("1.0", "end")
        self.is_running["sqli"] = True
        threading.Thread(target=self.animate, args=("sqli",), daemon=True).start()
        def run():
            payloads = ["'", "''", "`", "')", "\"", "%bf%27"]
            errors = ["syntax error", "mysql_fetch", "sqlite3", "ora-", "postgresql"]
            target = u if "?" in u else u + "?id=1"
            for p in payloads:
                if not self.is_running["sqli"]: break
                try:
                    r = requests.get(target + p, headers=self.agent, timeout=5, verify=False)
                    for err in errors:
                        if err in r.text.lower():
                            self.sqli_res.insert("end", f"[!!!] SQLi VULNERABILITY FOUND!\n[>] Payload: {p}\n[>] URL: {target+p}\n\n")
                            self.is_running["sqli"] = False
                            return
                except: pass
            self.sqli_res.insert("end", "[-] No obvious SQLi errors reflected.")
            self.is_running["sqli"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 7. ADMIN PANEL FINDER ---
    def start_admin(self):
        u = self.admin_ent.get().strip()
        if not u.startswith("http"): u = "http://" + u
        self.admin_res.delete("1.0", "end")
        self.is_running["admin"] = True
        threading.Thread(target=self.animate, args=("admin",), daemon=True).start()
        def run():
            panels = ["/admin","/admin/index.php","/admin/login.php","/dashboard/index.php", "/login", "/wp-admin", "/admin_login", "/administrator", "/cpanel", "/dashboard", "/backend", "/admin.php", "/dashboard.php", "/login.php", "/cp", "/Yonetim", "/panel.php", "/cgi-bin", "/wpadmin"]
            for p in panels:
                if not self.is_running["admin"]: break
                try:
                    r = requests.get(u.rstrip('/') + p, headers=self.agent, timeout=3, verify=False)
                    if r.status_code == 200 and ("password" in r.text.lower() or "login" in r.text.lower()):
                        self.admin_res.insert("end", f"[!!!] ADMIN PANEL FOUND: {u.rstrip('/') + p}\n")
                    self.admin_res.see("end")
                except: pass
            self.is_running["admin"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 8. WAF DETECTOR ---
    def start_waf(self):
        u = self.waf_ent.get().strip()
        if not u.startswith("http"): u = "http://" + u
        self.waf_res.delete("1.0", "end")
        self.is_running["waf"] = True
        threading.Thread(target=self.animate, args=("waf",), daemon=True).start()
        def run():
            try:
                r = requests.get(u + "/?id=1' AND 1=1 UNION SELECT 1,2,3 -- <script>alert(1)</script>", headers=self.agent, timeout=5, verify=False)
                h = str(r.headers).lower()
                if "cloudflare" in h or "cf-ray" in h: self.waf_res.insert("end", "[!] WAF: Cloudflare Detected.")
                elif "sucuri" in h: self.waf_res.insert("end", "[!] WAF: Sucuri Detected.")
                elif "mod_security" in h or r.status_code == 406: self.waf_res.insert("end", "[!] WAF: ModSecurity Detected.")
                else: self.waf_res.insert("end", f"[+] None detected. Status: {r.status_code}")
            except Exception as e: self.waf_res.insert("end", f"[-] Error: {e}")
            self.is_running["waf"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 9. JS SECRET LEAKS ---
    def start_js(self):
        u = self.js_ent.get().strip()
        if not u.startswith("http"): u = "http://" + u
        self.js_res.delete("1.0", "end")
        self.is_running["js"] = True
        threading.Thread(target=self.animate, args=("js",), daemon=True).start()
        def run():
            try:
                r = requests.get(u, headers=self.agent, timeout=5, verify=False)
                soup = BeautifulSoup(r.text, 'html.parser')
                scripts = [urllib.parse.urljoin(u, s.get('src')) for s in soup.find_all('script') if s.get('src')]
                for s_url in scripts:
                    if not self.is_running["js"]: break
                    try:
                        js_data = requests.get(s_url, timeout=4, verify=False).text
                        secrets = re.findall(r'(?i)(api_key|secret|token|password|AIza[0-9A-Za-z\-_]{35})["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{10,})', js_data)
                        for sec in secrets: self.js_res.insert("end", f"[!!!] POTENTIAL LEAK: {sec[0]} = {sec[1]}\n")
                    except: pass
            except: pass
            self.is_running["js"] = False
        threading.Thread(target=run, daemon=True).start()

    # --- 10. EXPLOIT ARCHITECT ---
    def start_arch(self):
        v = self.arch_ent.get().strip().lower()
        self.arch_res.delete("1.0", "end")
        db = {"apache 2.4.49": "CVE-2021-41773 (Path Traversal + RCE)", "ssh": "Hydra: hydra -L users.txt -P pass.txt ip ssh", "wordpress": "WPScan: wpscan --url url --enumerate u"}
        found = False
        for k in db:
            if k in v: self.arch_res.insert("end", f"[+] MATCH: {k.upper()}\n{db[k]}\n\n"); found = True
        if not found: self.arch_res.insert("end", f"[-] Check Exploit-DB: https://www.exploit-db.com/search?q={urllib.parse.quote(v)}")

    # --- 11. GENERATE REPORT ---
    def start_report(self):
        fn = f"H4CKTHOR_REPORT_{int(time.time())}.txt"
        try:
            with open(fn, "w") as f: f.write(f"=== H4CKTHOR REPORT ===\nTarget: {self.port_ent.get()}\nDate: {time.ctime()}\n")
            self.report_res.insert("end", f"[+] Report saved as: {fn}")
        except Exception as e: self.report_res.insert("end", f"[-] Error: {e}")

if __name__ == "__main__":
    app = H4ckthorHub()
    app.mainloop()