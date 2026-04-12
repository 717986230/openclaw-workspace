#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全和隐私
Security and Privacy
"""

import sqlite3
import hashlib
import secrets
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecurityType(Enum):
    DATA_ENCRYPTION = "data_encryption"
    PERMISSION_MANAGEMENT = "permission_management"
    AUDIT_LOG = "audit_log"

@dataclass
class SecurityResult:
    security_type: str
    success: bool
    explanation: str

class SecurityPrivacy:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.encryption_key = self._generate_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.permissions = {}
        self.audit_log = []

    def _generate_encryption_key(self) -> bytes:
        password = b"default_password_change_me"
        salt = b"default_salt_change_me"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_data(self, data: str) -> str:
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        encrypted = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()

    def encrypt_field(self, table: str, field: str, record_id: int) -> SecurityResult:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(f"SELECT {field} FROM {table} WHERE id = ?", (record_id,))
            result = cursor.fetchone()

            if result:
                original_data = result[0]
                encrypted_data = self.encrypt_data(str(original_data))

                cursor.execute(f"UPDATE {table} SET {field} = ? WHERE id = ?", (encrypted_data, record_id))
                conn.commit()

            conn.close()

            return SecurityResult(
                security_type='data_encryption',
                success=True,
                explanation=f'Encrypted field {field} in table {table} for record {record_id}'
            )
        except Exception as e:
            return SecurityResult(
                security_type='data_encryption',
                success=False,
                explanation=f'Encryption failed: {str(e)}'
            )

    def decrypt_field(self, table: str, field: str, record_id: int) -> SecurityResult:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(f"SELECT {field} FROM {table} WHERE id = ?", (record_id,))
            result = cursor.fetchone()

            if result:
                encrypted_data = result[0]
                decrypted_data = self.decrypt_data(encrypted_data)

            conn.close()

            return SecurityResult(
                security_type='data_encryption',
                success=True,
                explanation=f'Decrypted field {field} in table {table} for record {record_id}'
            )
        except Exception as e:
            return SecurityResult(
                security_type='data_encryption',
                success=False,
                explanation=f'Decryption failed: {str(e)}'
            )

    def grant_permission(self, user_id: str, resource: str, permission: str) -> SecurityResult:
        if user_id not in self.permissions:
            self.permissions[user_id] = {}
        if resource not in self.permissions[user_id]:
            self.permissions[user_id][resource] = []
        if permission not in self.permissions[user_id][resource]:
            self.permissions[user_id][resource].append(permission)

        self._log_audit('grant_permission', user_id, resource, permission)

        return SecurityResult(
            security_type='permission_management',
            success=True,
            explanation=f'Granted {permission} permission on {resource} to user {user_id}'
        )

    def revoke_permission(self, user_id: str, resource: str, permission: str) -> SecurityResult:
        if user_id in self.permissions and resource in self.permissions[user_id]:
            if permission in self.permissions[user_id][resource]:
                self.permissions[user_id][resource].remove(permission)

        self._log_audit('revoke_permission', user_id, resource, permission)

        return SecurityResult(
            security_type='permission_management',
            success=True,
            explanation=f'Revoked {permission} permission on {resource} from user {user_id}'
        )

    def check_permission(self, user_id: str, resource: str, permission: str) -> bool:
        if user_id not in self.permissions:
            return False
        if resource not in self.permissions[user_id]:
            return False
        return permission in self.permissions[user_id][resource]

    def _log_audit(self, action: str, user_id: str, resource: str, details: str):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'resource': resource,
            'details': details
        }
        self.audit_log.append(log_entry)

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        return self.audit_log[-limit:]

    def comprehensive_security(self) -> Dict:
        results = {}
        results['encryption'] = self.encrypt_field('memories', 'content', 1)
        results['permission'] = self.grant_permission('user1', 'memories', 'read')
        results['audit'] = self.get_audit_log(10)
        return results

    def get_security_statistics(self) -> Dict:
        stats = {
            'total_permissions': sum(len(perms) for user_perms in self.permissions.values() for perms in user_perms.values()),
            'total_users': len(self.permissions),
            'audit_log_size': len(self.audit_log),
            'encryption_key_length': len(self.encryption_key)
        }
        return stats

if __name__ == "__main__":
    print("Testing Security and Privacy...")
    security = SecurityPrivacy("memory/database/xiaozhi_memory.db")
    result = security.encrypt_field('memories', 'content', 1)
    print(f"Field encryption: {result.explanation}")
    result = security.decrypt_field('memories', 'content', 1)
    print(f"Field decryption: {result.explanation}")
    result = security.grant_permission('user1', 'memories', 'read')
    print(f"Grant permission: {result.explanation}")
    result = security.revoke_permission('user1', 'memories', 'read')
    print(f"Revoke permission: {result.explanation}")
    has_permission = security.check_permission('user1', 'memories', 'read')
    print(f"Check permission: {has_permission}")
    results = security.comprehensive_security()
    print(f"Comprehensive security: {results}")
    stats = security.get_security_statistics()
    print(f"Statistics: {stats}")
    print("Security and Privacy test complete!")
