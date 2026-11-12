"""Minimal login test — no model/DB loading, just auth.

Usage (from the repo root):
    StuId=xxx UISPsw=xxx TOTP_SECRET=xxx python scripts/test_login.py

Prints the TOTP code it generates so you can compare against your
authenticator app, then runs the full WebVPN + iCourse CAS login
(including the OTP second factor), retrying a couple of times to ride
out WebVPN's intermittent "cold session" hiccups.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.runtime import config
from src.api.webvpn import WebVPNSession, generate_totp
from src.api.icourse import ICourseClient


def main() -> None:
    if config.TOTP_SECRET:
        print(f"[TOTP] current code: {generate_totp(config.TOTP_SECRET)}")

    for attempt in range(3):
        try:
            vpn = WebVPNSession()
            print(f"\n=== login attempt {attempt + 1}/3 ===")
            vpn.login()
            vpn.authenticate_icourse()
            client = ICourseClient(vpn)
            if client.check_alive():
                print("[OK] login + iCourse auth succeeded")
                return
            print(f"[FAIL] session not alive (attempt {attempt + 1}/3)")
        except Exception as e:
            print(f"[FAIL] attempt {attempt + 1}/3: {type(e).__name__}: {e}")
        if attempt < 2:
            time.sleep(3)

    print("[FAIL] login failed after 3 attempts")


if __name__ == "__main__":
    main()
