import hashlib

password = "waxersu12aa"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(f'TEAM_PASSWORD_HASH = "{hash_value}"')
print(f"\nThe hash for password '{password}' is:")
print(hash_value)
