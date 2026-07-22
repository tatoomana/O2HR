#!/usr/bin/env python3
"""
Backend API Testing for AI Stack Console
Tests all endpoints and validates docker-compose.yml content
"""
import requests
import sys
import zipfile
import io
from datetime import datetime

class BackendTester:
    def __init__(self, base_url="https://devops-docker-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def log(self, msg, level="INFO"):
        prefix = {
            "INFO": "🔍",
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️"
        }.get(level, "ℹ️")
        print(f"{prefix} {msg}")

    def test(self, name, condition, detail=""):
        """Run a single test assertion"""
        self.tests_run += 1
        if condition:
            self.tests_passed += 1
            self.log(f"PASS: {name}", "PASS")
            if detail:
                print(f"     {detail}")
            return True
        else:
            self.tests_failed += 1
            self.failures.append(name)
            self.log(f"FAIL: {name}", "FAIL")
            if detail:
                print(f"     {detail}")
            return False

    def test_overview(self):
        """Test GET /api/overview"""
        self.log("\n=== Testing GET /api/overview ===")
        try:
            resp = requests.get(f"{self.api_url}/overview", timeout=10)
            self.test("Overview endpoint returns 200", resp.status_code == 200)
            
            if resp.status_code == 200:
                data = resp.json()
                self.test("Overview has 'title' field", "title" in data)
                self.test("Overview has 'services' array", "services" in data and isinstance(data["services"], list))
                self.test("Overview has 2 services", len(data.get("services", [])) == 2)
                
                services = data.get("services", [])
                oh = next((s for s in services if s.get("id") == "openhands"), None)
                hr = next((s for s in services if s.get("id") == "headroom"), None)
                
                self.test("OpenHands service present", oh is not None)
                if oh:
                    self.test("OpenHands host_port is 5000", oh.get("host_port") == 5000)
                    self.test("OpenHands container_port is 3000", oh.get("container_port") == 3000)
                
                self.test("Headroom service present", hr is not None)
                if hr:
                    self.test("Headroom host_port is 5001", hr.get("host_port") == 5001)
                    self.test("Headroom container_port is 8787", hr.get("container_port") == 8787)
                
                self.test("Network is 'ai-stack-network'", data.get("network") == "ai-stack-network")
                self.test("Forbidden ports are [3000, 4000]", data.get("forbidden_ports") == [3000, 4000])
                
                fixes = data.get("fixes", [])
                self.test("Fixes array present", isinstance(fixes, list))
                self.test("Has 2 fixes (socket + dind)", len(fixes) == 2)
                
                fix_ids = [f.get("id") for f in fixes]
                self.test("Socket fix present", "socket" in fix_ids)
                self.test("DinD fix present", "dind" in fix_ids)
                
        except Exception as e:
            self.test("Overview endpoint accessible", False, str(e))

    def test_files_list(self):
        """Test GET /api/files"""
        self.log("\n=== Testing GET /api/files ===")
        try:
            resp = requests.get(f"{self.api_url}/files", timeout=10)
            self.test("Files list endpoint returns 200", resp.status_code == 200)
            
            if resp.status_code == 200:
                data = resp.json()
                files = data.get("files", [])
                self.test("Files array present", isinstance(files, list))
                self.test("Has 6 files", len(files) == 6, f"Found {len(files)} files")
                
                expected_files = [
                    "docker-compose.yml",
                    ".env.example",
                    "init.sh",
                    "README.md",
                    ".gitignore",
                    "validate_stack.py"
                ]
                
                file_names = [f.get("name") for f in files]
                for expected in expected_files:
                    self.test(f"File '{expected}' in list", expected in file_names)
                
                # Check metadata for each file
                for f in files:
                    name = f.get("name", "unknown")
                    self.test(f"{name}: has 'language' field", "language" in f)
                    self.test(f"{name}: has lines > 0", f.get("lines", 0) > 0)
                    self.test(f"{name}: has size > 0", f.get("size", 0) > 0)
                    
        except Exception as e:
            self.test("Files list endpoint accessible", False, str(e))

    def test_docker_compose_content(self):
        """Test GET /api/files/docker-compose.yml and validate critical fixes"""
        self.log("\n=== Testing GET /api/files/docker-compose.yml (CRITICAL) ===")
        try:
            resp = requests.get(f"{self.api_url}/files/docker-compose.yml", timeout=10)
            self.test("docker-compose.yml endpoint returns 200", resp.status_code == 200)
            
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("content", "")
                
                self.test("docker-compose.yml has content", len(content) > 0)
                self.test("Content has 'language' field", data.get("language") == "yaml")
                
                # CRITICAL FIXES - these MUST be present
                self.log("\n  🔒 Checking CRITICAL FIXES:")
                
                # Fix 1: Socket permissions via group_add
                has_group_add = "group_add" in content and "${DOCKER_GID" in content
                self.test("✓ Socket fix: group_add with ${DOCKER_GID", has_group_add)
                
                # Fix 2: DinD networking
                has_host_gateway = "host.docker.internal:host-gateway" in content
                self.test("✓ DinD fix: host.docker.internal:host-gateway", has_host_gateway)
                
                has_workspace_mount = "WORKSPACE_MOUNT_PATH" in content
                self.test("✓ DinD fix: WORKSPACE_MOUNT_PATH env var", has_workspace_mount)
                
                has_socket_mount = "/var/run/docker.sock:/var/run/docker.sock" in content
                self.test("✓ Socket mount present", has_socket_mount)
                
                # Port mappings
                self.log("\n  🔌 Checking PORT MAPPINGS:")
                has_5000_3000 = "5000:3000" in content or "${OPENHANDS_HOST_PORT:-5000}:3000" in content
                self.test("✓ OpenHands port 5000:3000", has_5000_3000)
                
                has_5001_8787 = "5001:8787" in content or "${HEADROOM_HOST_PORT:-5001}:8787" in content
                self.test("✓ Headroom port 5001:8787", has_5001_8787)
                
                # Forbidden ports check
                self.log("\n  🚫 Checking FORBIDDEN PORTS:")
                # Check that 3000 and 4000 are NOT used as host ports
                # We need to be careful - 3000 can appear as container port
                lines = content.split('\n')
                host_3000_bound = False
                host_4000_bound = False
                
                for line in lines:
                    # Look for port mappings in the ports: section
                    if 'ports:' not in content[:content.find(line)].split('\n')[-5:]:
                        continue
                    # Check if line has port mapping format
                    if ':' in line and '-' in line and '"' in line:
                        # Extract host port from patterns like "3000:xxxx" or "${VAR:-3000}:xxxx"
                        if line.strip().startswith('- "3000:') or ':-3000}:' in line:
                            host_3000_bound = True
                        if line.strip().startswith('- "4000:') or ':-4000}:' in line:
                            host_4000_bound = True
                
                self.test("✓ Host port 3000 NOT bound", not host_3000_bound)
                self.test("✓ Host port 4000 NOT bound", not host_4000_bound)
                
                # Compose hygiene
                self.log("\n  📋 Checking COMPOSE HYGIENE:")
                # Check for obsolete version key at top level
                has_version_key = content.strip().startswith("version:") or "\nversion:" in content[:200]
                self.test("✓ No obsolete 'version:' key at top level", not has_version_key)
                
                has_ai_stack_network = "ai-stack-network" in content
                self.test("✓ ai-stack-network present", has_ai_stack_network)
                
        except Exception as e:
            self.test("docker-compose.yml content check", False, str(e))

    def test_individual_files(self):
        """Test GET /api/files/{name} for each file"""
        self.log("\n=== Testing Individual File Endpoints ===")
        files = [".env.example", "init.sh", "README.md", ".gitignore", "validate_stack.py"]
        
        for filename in files:
            try:
                resp = requests.get(f"{self.api_url}/files/{filename}", timeout=10)
                self.test(f"GET /api/files/{filename} returns 200", resp.status_code == 200)
                
                if resp.status_code == 200:
                    data = resp.json()
                    self.test(f"{filename}: has content", len(data.get("content", "")) > 0)
                    self.test(f"{filename}: has language", "language" in data)
                    
            except Exception as e:
                self.test(f"GET /api/files/{filename}", False, str(e))

    def test_file_download(self):
        """Test GET /api/files/{name}/download"""
        self.log("\n=== Testing File Download Endpoints ===")
        try:
            resp = requests.get(f"{self.api_url}/files/docker-compose.yml/download", timeout=10)
            self.test("Download endpoint returns 200", resp.status_code == 200)
            self.test("Download has Content-Disposition header", "Content-Disposition" in resp.headers)
            
            if "Content-Disposition" in resp.headers:
                cd = resp.headers["Content-Disposition"]
                self.test("Content-Disposition is 'attachment'", "attachment" in cd)
                self.test("Filename in Content-Disposition", "docker-compose.yml" in cd)
                
        except Exception as e:
            self.test("File download endpoint", False, str(e))

    def test_nonexistent_file(self):
        """Test GET /api/files/nonexistent.txt returns 404"""
        self.log("\n=== Testing 404 for Nonexistent File ===")
        try:
            resp = requests.get(f"{self.api_url}/files/nonexistent.txt", timeout=10)
            self.test("Nonexistent file returns 404", resp.status_code == 404)
            
        except Exception as e:
            self.test("404 handling", False, str(e))

    def test_path_traversal_protection(self):
        """Test comprehensive path traversal protection (REGRESSION FIX VERIFY)"""
        self.log("\n=== Testing Path Traversal Protection (CRITICAL REGRESSION FIX) ===")
        
        # Test cases that MUST return 404 (not 200 or 500)
        traversal_attempts = [
            # Basic traversal patterns
            ("../../../etc/passwd", "Basic traversal with ../../../"),
            ("..\\..\\..\\windows\\system32", "Windows-style traversal"),
            
            # URL-encoded traversal (CRITICAL - mentioned in requirements)
            ("..%2f..%2fetc%2fpasswd", "URL-encoded forward slash traversal"),
            ("..%2F..%2Fetc%2Fpasswd", "URL-encoded uppercase traversal"),
            ("..%5c..%5cwindows", "URL-encoded backslash traversal"),
            
            # Double encoding
            ("..%252f..%252fetc%252fpasswd", "Double URL-encoded traversal"),
            
            # Names containing '..' in various positions
            ("..docker-compose.yml", "Filename starting with .."),
            ("docker..compose.yml", "Filename with .. in middle"),
            ("docker-compose.yml..", "Filename ending with .."),
            ("test..file", "Simple filename with .."),
            
            # Mixed patterns
            ("./docker-compose.yml", "Relative path with ./"),
            ("../docker-compose.yml", "Parent directory reference"),
            ("docker-compose.yml/../init.sh", "Traversal in middle"),
            
            # Absolute paths
            ("/etc/passwd", "Absolute path with /"),
            ("/app/deliverables/docker-compose.yml", "Absolute path to valid file"),
            
            # Names with slashes or backslashes
            ("subdir/docker-compose.yml", "Subdirectory with /"),
            ("subdir\\docker-compose.yml", "Subdirectory with \\"),
            
            # Null byte injection attempts
            ("docker-compose.yml%00.txt", "Null byte injection"),
            
            # Empty and whitespace
            ("", "Empty filename"),
            (" ", "Whitespace filename"),
            ("   ", "Multiple spaces"),
        ]
        
        for filename, description in traversal_attempts:
            try:
                # Use requests.get with allow_redirects=False to prevent following redirects
                resp = requests.get(
                    f"{self.api_url}/files/{filename}",
                    timeout=10,
                    allow_redirects=False
                )
                
                # MUST be 404, not 200 (success) or 500 (server error) or 3xx (redirect)
                is_404 = resp.status_code == 404
                
                if not is_404:
                    detail = f"Got {resp.status_code} (expected 404) - {description}"
                    if resp.status_code == 200:
                        detail += " [SECURITY ISSUE: File accessible!]"
                    elif resp.status_code >= 500:
                        detail += " [Server error - should be 404]"
                    elif 300 <= resp.status_code < 400:
                        detail += f" [Redirect to: {resp.headers.get('Location', 'unknown')}]"
                else:
                    detail = f"Correctly blocked - {description}"
                
                self.test(
                    f"Traversal blocked: {filename[:50]}{'...' if len(filename) > 50 else ''}",
                    is_404,
                    detail
                )
                
            except Exception as e:
                self.test(f"Traversal test: {filename[:30]}", False, f"Error: {str(e)}")

    def test_download_all(self):
        """Test GET /api/download-all returns valid zip"""
        self.log("\n=== Testing GET /api/download-all ===")
        try:
            resp = requests.get(f"{self.api_url}/download-all", timeout=15)
            self.test("Download-all endpoint returns 200", resp.status_code == 200)
            self.test("Download-all returns application/zip", "application/zip" in resp.headers.get("Content-Type", ""))
            self.test("Download-all has Content-Disposition", "Content-Disposition" in resp.headers)
            
            if resp.status_code == 200:
                # Validate it's a real zip
                try:
                    zip_data = io.BytesIO(resp.content)
                    with zipfile.ZipFile(zip_data, 'r') as zf:
                        files = zf.namelist()
                        self.test("Zip contains files", len(files) > 0)
                        self.test("Zip has 6 files", len(files) == 6, f"Found {len(files)} files")
                        
                        # Check all files are under ai-stack/ directory
                        all_in_dir = all(f.startswith("ai-stack/") for f in files)
                        self.test("All files under ai-stack/ directory", all_in_dir)
                        
                        # Check for key files
                        file_basenames = [f.split("/")[-1] for f in files]
                        self.test("Zip contains docker-compose.yml", "docker-compose.yml" in file_basenames)
                        self.test("Zip contains init.sh", "init.sh" in file_basenames)
                        
                except zipfile.BadZipFile:
                    self.test("Zip file is valid", False, "Invalid zip format")
                    
        except Exception as e:
            self.test("Download-all endpoint", False, str(e))

    def test_validate(self):
        """Test GET /api/validate returns validation report"""
        self.log("\n=== Testing GET /api/validate ===")
        try:
            resp = requests.get(f"{self.api_url}/validate", timeout=10)
            self.test("Validate endpoint returns 200", resp.status_code == 200)
            
            if resp.status_code == 200:
                data = resp.json()
                self.test("Validate has 'summary' field", "summary" in data)
                self.test("Validate has 'groups' field", "groups" in data)
                
                summary = data.get("summary", {})
                self.test("Summary has 'passed' count", "passed" in summary)
                self.test("Summary has 'failed' count", "failed" in summary)
                self.test("Summary has 'total' count", "total" in summary)
                
                total = summary.get("total", 0)
                passed = summary.get("passed", 0)
                failed = summary.get("failed", 0)
                
                self.test("Total checks is 18", total == 18, f"Total: {total}")
                self.test("All checks passing (failed == 0)", failed == 0, f"Failed: {failed}, Passed: {passed}")
                
                groups = data.get("groups", [])
                self.test("Has validation groups", len(groups) > 0)
                
                expected_groups = [
                    "Ports & Constraints",
                    "Networking (DinD fix)",
                    "Security (socket fix)",
                    "Persistence & Volumes",
                    "Compose Hygiene"
                ]
                
                group_names = [g.get("name") for g in groups]
                for expected in expected_groups:
                    self.test(f"Group '{expected}' present", expected in group_names)
                    
        except Exception as e:
            self.test("Validate endpoint", False, str(e))

    def run_all_tests(self):
        """Run all backend tests"""
        self.log(f"\n{'='*70}")
        self.log(f"AI Stack Console - Backend API Tests")
        self.log(f"Base URL: {self.base_url}")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*70}")
        
        # Run all test suites
        self.test_overview()
        self.test_files_list()
        self.test_docker_compose_content()
        self.test_individual_files()
        self.test_file_download()
        self.test_nonexistent_file()
        self.test_path_traversal_protection()  # NEW: Comprehensive traversal tests
        self.test_download_all()
        self.test_validate()
        
        # Summary
        self.log(f"\n{'='*70}")
        self.log(f"TEST SUMMARY")
        self.log(f"{'='*70}")
        self.log(f"Total Tests: {self.tests_run}")
        self.log(f"Passed: {self.tests_passed}", "PASS")
        self.log(f"Failed: {self.tests_failed}", "FAIL" if self.tests_failed > 0 else "INFO")
        
        if self.tests_failed > 0:
            self.log(f"\n❌ FAILED TESTS:", "FAIL")
            for i, failure in enumerate(self.failures, 1):
                print(f"  {i}. {failure}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"\nSuccess Rate: {success_rate:.1f}%")
        
        return 0 if self.tests_failed == 0 else 1

def main():
    tester = BackendTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
