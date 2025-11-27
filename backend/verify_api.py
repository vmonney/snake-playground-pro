#!/usr/bin/env python3
"""
Verify API script - Tests all endpoints against a running server.

Usage:
    1. Start the server: uv run uvicorn main:app --host 0.0.0.0 --port 3000
    2. Run this script: uv run python verify_api.py

This script tests all API endpoints and prints a validation report.
"""

import sys
import time
from dataclasses import dataclass

import httpx

BASE_URL = "http://localhost:3000/api/v1"

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


@dataclass
class TestResult:
    """Result of an API test."""

    name: str
    passed: bool
    message: str
    status_code: int | None = None


class APIVerifier:
    """Verifies API endpoints against the running server."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        self.base_url = base_url
        self.client = httpx.Client(timeout=10.0)
        self.results: list[TestResult] = []
        self.token: str | None = None
        self.user_id: str | None = None

    def run_all_tests(self) -> bool:
        """Run all API tests and return True if all passed."""
        print(f"\n{BOLD}{BLUE}=== Snake Playground Pro API Verification ==={RESET}\n")

        # Check if server is running
        if not self._check_server():
            return False

        # Run test groups
        self._test_health_endpoints()
        self._test_auth_endpoints()
        self._test_user_endpoints()
        self._test_leaderboard_endpoints()
        self._test_live_endpoints()

        # Print summary
        self._print_summary()

        return all(r.passed for r in self.results)

    def _check_server(self) -> bool:
        """Check if the server is running."""
        print(f"{BOLD}Checking server connection...{RESET}")
        try:
            response = self.client.get(f"{self.base_url.replace('/api/v1', '')}/health")
            if response.status_code == 200:
                print(f"{GREEN}✓ Server is running{RESET}\n")
                return True
        except httpx.ConnectError:
            pass

        print(f"{RED}✗ Server is not running!{RESET}")
        print(f"{YELLOW}Please start the server with:{RESET}")
        print(f"  cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 3000\n")
        return False

    def _add_result(
        self,
        name: str,
        passed: bool,
        message: str,
        status_code: int | None = None,
    ) -> None:
        """Add a test result."""
        result = TestResult(name=name, passed=passed, message=message, status_code=status_code)
        self.results.append(result)
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        code_str = f" [{status_code}]" if status_code else ""
        print(f"  {status} {name}{code_str}: {message}")

    def _test_health_endpoints(self) -> None:
        """Test health and root endpoints."""
        print(f"{BOLD}Health Endpoints:{RESET}")

        # Test root endpoint
        try:
            response = self.client.get(self.base_url.replace("/api/v1", "/"))
            self._add_result(
                "GET /",
                response.status_code == 200,
                "Root endpoint",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /", False, str(e))

        # Test health endpoint
        try:
            response = self.client.get(self.base_url.replace("/api/v1", "/health"))
            self._add_result(
                "GET /health",
                response.status_code == 200 and response.json().get("status") == "healthy",
                "Health check",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /health", False, str(e))

        print()

    def _test_auth_endpoints(self) -> None:
        """Test authentication endpoints."""
        print(f"{BOLD}Authentication Endpoints:{RESET}")

        # Test signup
        try:
            response = self.client.post(
                f"{self.base_url}/auth/signup",
                json={
                    "username": "TestUser123",
                    "email": "testuser@verify.com",
                    "password": "testpass123",
                },
            )
            if response.status_code == 201:
                data = response.json()
                self.token = data.get("token")
                self.user_id = data.get("user", {}).get("id")
                self._add_result(
                    "POST /auth/signup",
                    True,
                    "User created successfully",
                    response.status_code,
                )
            elif response.status_code == 409:
                # User already exists, try login instead
                self._add_result(
                    "POST /auth/signup",
                    True,
                    "User already exists (expected)",
                    response.status_code,
                )
                # Login to get token
                login_resp = self.client.post(
                    f"{self.base_url}/auth/login",
                    json={"email": "testuser@verify.com", "password": "testpass123"},
                )
                if login_resp.status_code == 200:
                    data = login_resp.json()
                    self.token = data.get("token")
                    self.user_id = data.get("user", {}).get("id")
            else:
                self._add_result(
                    "POST /auth/signup",
                    False,
                    response.text,
                    response.status_code,
                )
        except Exception as e:
            self._add_result("POST /auth/signup", False, str(e))

        # Test login
        try:
            response = self.client.post(
                f"{self.base_url}/auth/login",
                json={"email": "snake@test.com", "password": "password123"},
            )
            if response.status_code == 200:
                data = response.json()
                if not self.token:
                    self.token = data.get("token")
                    self.user_id = data.get("user", {}).get("id")
            self._add_result(
                "POST /auth/login",
                response.status_code == 200 and "token" in response.json(),
                "Login successful" if response.status_code == 200 else response.text,
                response.status_code,
            )
        except Exception as e:
            self._add_result("POST /auth/login", False, str(e))

        # Test login with invalid credentials
        try:
            response = self.client.post(
                f"{self.base_url}/auth/login",
                json={"email": "snake@test.com", "password": "wrongpassword"},
            )
            self._add_result(
                "POST /auth/login (invalid)",
                response.status_code == 401,
                "Correctly rejected",
                response.status_code,
            )
        except Exception as e:
            self._add_result("POST /auth/login (invalid)", False, str(e))

        # Test get current user
        if self.token:
            try:
                response = self.client.get(
                    f"{self.base_url}/auth/me",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                self._add_result(
                    "GET /auth/me",
                    response.status_code == 200 and "username" in response.json(),
                    "User info retrieved",
                    response.status_code,
                )
            except Exception as e:
                self._add_result("GET /auth/me", False, str(e))

        # Test get current user without auth
        try:
            response = self.client.get(f"{self.base_url}/auth/me")
            self._add_result(
                "GET /auth/me (no auth)",
                response.status_code == 401,
                "Correctly rejected",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /auth/me (no auth)", False, str(e))

        print()

    def _test_user_endpoints(self) -> None:
        """Test user endpoints."""
        print(f"{BOLD}User Endpoints:{RESET}")

        # Test get user profile
        try:
            response = self.client.get(f"{self.base_url}/users/user-1")
            self._add_result(
                "GET /users/{userId}",
                response.status_code == 200 and "username" in response.json(),
                "Profile retrieved",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /users/{userId}", False, str(e))

        # Test get user profile not found
        try:
            response = self.client.get(f"{self.base_url}/users/nonexistent")
            self._add_result(
                "GET /users/{userId} (404)",
                response.status_code == 404,
                "Correctly returned 404",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /users/{userId} (404)", False, str(e))

        # Test get user stats
        try:
            response = self.client.get(f"{self.base_url}/users/user-1/stats")
            data = response.json()
            self._add_result(
                "GET /users/{userId}/stats",
                response.status_code == 200
                and "highScore" in data
                and "gamesPlayed" in data
                and "rank" in data,
                "Stats retrieved",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /users/{userId}/stats", False, str(e))

        # Test update user profile
        if self.token and self.user_id:
            try:
                response = self.client.patch(
                    f"{self.base_url}/users/{self.user_id}",
                    json={"username": "UpdatedTestUser"},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                self._add_result(
                    "PATCH /users/{userId}",
                    response.status_code == 200,
                    "Profile updated",
                    response.status_code,
                )
            except Exception as e:
                self._add_result("PATCH /users/{userId}", False, str(e))

        # Test update another user's profile (should fail)
        if self.token:
            try:
                response = self.client.patch(
                    f"{self.base_url}/users/user-1",
                    json={"username": "HackerName"},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                self._add_result(
                    "PATCH /users/{userId} (forbidden)",
                    response.status_code == 403,
                    "Correctly rejected",
                    response.status_code,
                )
            except Exception as e:
                self._add_result("PATCH /users/{userId} (forbidden)", False, str(e))

        print()

    def _test_leaderboard_endpoints(self) -> None:
        """Test leaderboard endpoints."""
        print(f"{BOLD}Leaderboard Endpoints:{RESET}")

        # Test get leaderboard
        try:
            response = self.client.get(f"{self.base_url}/leaderboard")
            data = response.json()
            self._add_result(
                "GET /leaderboard",
                response.status_code == 200 and isinstance(data, list),
                f"Retrieved {len(data)} entries",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /leaderboard", False, str(e))

        # Test get leaderboard with filters
        try:
            response = self.client.get(f"{self.base_url}/leaderboard?limit=5&mode=walls")
            data = response.json()
            all_walls = all(e.get("mode") == "walls" for e in data)
            self._add_result(
                "GET /leaderboard?limit=5&mode=walls",
                response.status_code == 200 and len(data) <= 5 and all_walls,
                f"Filtered correctly ({len(data)} entries)",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /leaderboard?limit=5&mode=walls", False, str(e))

        # Test submit score
        if self.token:
            try:
                response = self.client.post(
                    f"{self.base_url}/leaderboard/scores",
                    json={"score": 999, "mode": "walls"},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                self._add_result(
                    "POST /leaderboard/scores",
                    response.status_code == 201 and response.json().get("score") == 999,
                    "Score submitted",
                    response.status_code,
                )
            except Exception as e:
                self._add_result("POST /leaderboard/scores", False, str(e))

        # Test submit score without auth
        try:
            response = self.client.post(
                f"{self.base_url}/leaderboard/scores",
                json={"score": 100, "mode": "walls"},
            )
            self._add_result(
                "POST /leaderboard/scores (no auth)",
                response.status_code == 401,
                "Correctly rejected",
                response.status_code,
            )
        except Exception as e:
            self._add_result("POST /leaderboard/scores (no auth)", False, str(e))

        # Test get user rank
        try:
            response = self.client.get(f"{self.base_url}/leaderboard/rank/user-1")
            data = response.json()
            self._add_result(
                "GET /leaderboard/rank/{userId}",
                response.status_code == 200 and "rank" in data and "userId" in data,
                f"Rank: {data.get('rank')}",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /leaderboard/rank/{userId}", False, str(e))

        print()

    def _test_live_endpoints(self) -> None:
        """Test live player endpoints."""
        print(f"{BOLD}Live Player Endpoints:{RESET}")

        # Test get live players
        try:
            response = self.client.get(f"{self.base_url}/live/players")
            data = response.json()
            self._add_result(
                "GET /live/players",
                response.status_code == 200 and isinstance(data, list),
                f"Retrieved {len(data)} players",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /live/players", False, str(e))

        # Test get specific live player
        try:
            response = self.client.get(f"{self.base_url}/live/players/live-1")
            if response.status_code == 200:
                data = response.json()
                has_fields = all(
                    k in data
                    for k in ["id", "username", "score", "snake", "food", "direction", "isAlive"]
                )
                self._add_result(
                    "GET /live/players/{playerId}",
                    has_fields,
                    "Player data retrieved",
                    response.status_code,
                )
            else:
                self._add_result(
                    "GET /live/players/{playerId}",
                    False,
                    response.text,
                    response.status_code,
                )
        except Exception as e:
            self._add_result("GET /live/players/{playerId}", False, str(e))

        # Test get non-existent live player
        try:
            response = self.client.get(f"{self.base_url}/live/players/nonexistent")
            self._add_result(
                "GET /live/players/{playerId} (404)",
                response.status_code == 404,
                "Correctly returned 404",
                response.status_code,
            )
        except Exception as e:
            self._add_result("GET /live/players/{playerId} (404)", False, str(e))

        # Test join as watcher
        try:
            response = self.client.post(f"{self.base_url}/live/players/live-1/watch")
            self._add_result(
                "POST /live/players/{playerId}/watch",
                response.status_code == 200 and "watcherCount" in response.json(),
                f"Watcher count: {response.json().get('watcherCount')}",
                response.status_code,
            )
        except Exception as e:
            self._add_result("POST /live/players/{playerId}/watch", False, str(e))

        # Test leave as watcher
        try:
            response = self.client.delete(f"{self.base_url}/live/players/live-1/watch")
            self._add_result(
                "DELETE /live/players/{playerId}/watch",
                response.status_code == 200 and "watcherCount" in response.json(),
                f"Watcher count: {response.json().get('watcherCount')}",
                response.status_code,
            )
        except Exception as e:
            self._add_result("DELETE /live/players/{playerId}/watch", False, str(e))

        print()

    def _test_logout(self) -> None:
        """Test logout endpoint."""
        if self.token:
            try:
                response = self.client.post(
                    f"{self.base_url}/auth/logout",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                self._add_result(
                    "POST /auth/logout",
                    response.status_code == 200,
                    "Logged out",
                    response.status_code,
                )
            except Exception as e:
                self._add_result("POST /auth/logout", False, str(e))

    def _print_summary(self) -> None:
        """Print test summary."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        print(f"{BOLD}{'=' * 50}{RESET}")
        print(f"{BOLD}Summary:{RESET}")
        print(f"  {GREEN}Passed: {passed}{RESET}")
        print(f"  {RED}Failed: {failed}{RESET}")
        print(f"  Total: {total}")
        print()

        if failed == 0:
            print(f"{GREEN}{BOLD}✓ All tests passed!{RESET}")
        else:
            print(f"{RED}{BOLD}✗ Some tests failed:{RESET}")
            for r in self.results:
                if not r.passed:
                    print(f"  {RED}• {r.name}: {r.message}{RESET}")

        print()


def main() -> int:
    """Main entry point."""
    verifier = APIVerifier()
    success = verifier.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
