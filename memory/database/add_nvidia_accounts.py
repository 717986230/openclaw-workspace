#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add NVIDIA API accounts to secure storage
"""

import sys
sys.path.insert(0, str(sys.path[0]))
from secure_storage import get_secure_storage


def add_nvidia_accounts():
    storage = get_secure_storage()

    accounts = [
        # email, password, api_key, status, active
        ("ykpcdejc5079@abgkh520.codingbycursor.com", "0mA%s1r7O6#BRx", "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", "通过", "否"),
        ("zfxoymdu5704@ecplp294.codingbycursor.com", "pgQ!Dz9pXF0roi", "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", "通过", "否"),
        ("zixxyitf9101@kwxls877.codingbycursor.com", "nWsHiGU7e5@&*A", "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", "通过", "否"),
        ("kvbuigbs9415@qevkb835.codingbycursor.com", "ehg$4j3trYNq@U", "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", "通过", "否")
    ]

    for email, password, api_key, status, active in accounts:
        notes = f"API Key: {api_key}, Status: {status}, Active: {active}"
        try:
            account_id = storage.add_account(
                service="NVIDIA API",
                username=email,
                password=password,
                notes=notes,
                category="nvidia_api"
            )
            print(f"[OK] Added account for {email} (ID: {account_id})")
        except Exception as e:
            print(f"[ERROR] Failed to add account for {email}: {e}")

    print()
    stats = storage.get_stats()
    print(f"Total accounts in storage: {stats['total']}")
    if stats['by_category']:
        print(f"By category: {stats['by_category']}")


if __name__ == "__main__":
    add_nvidia_accounts()
