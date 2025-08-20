import streamlit as st
import hashlib

# Test password
password = "waxersu12aa"
expected_hash = "6bcdafb5a5b08541139298d0c4b359cd10fadc3ac19354ed7f2781a0c56a408b"

# Generate hash
generated_hash = hashlib.sha256(password.encode()).hexdigest()

print(f"Password: {password}")
print(f"Generated hash: {generated_hash}")
print(f"Expected hash:  {expected_hash}")
print(f"Hashes match: {generated_hash == expected_hash}")

# Check if secrets are accessible
print("\nChecking Streamlit secrets...")
try:
    secret_hash = st.secrets.get("TEAM_PASSWORD_HASH", "NOT_FOUND")
    print(f"Secret hash from st.secrets: {secret_hash}")
    print(f"Secret matches expected: {secret_hash == expected_hash}")
except Exception as e:
    print(f"Error accessing secrets: {e}")

# Test the authentication logic
def test_auth(input_password):
    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    secret_hash = "6bcdafb5a5b08541139298d0c4b359cd10fadc3ac19354ed7f2781a0c56a408b"
    
    print(f"\nTesting authentication with '{input_password}':")
    print(f"Input hash:  {input_hash}")
    print(f"Secret hash: {secret_hash}")
    print(f"Match: {input_hash == secret_hash}")
    
    return input_hash == secret_hash

# Test with the password
result = test_auth("waxersu12aa")
print(f"\nAuthentication result: {result}")

# Test with variations (common issues)
print("\nTesting common variations:")
test_auth("waxersu12aa ")  # with trailing space
test_auth(" waxersu12aa")  # with leading space
test_auth("Waxersu12aa")   # different case
