#!/usr/bin/env python3
"""
Utility to generate a hashed password for the hockey stats app.
Run this script locally to generate a hash for your team password.
"""

import hashlib
import getpass

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("Hockey Stats App - Password Hash Generator")
    print("-" * 40)
    print("This utility will generate a hashed password for your team.")
    print("The hash will be stored in your Streamlit secrets.\n")
    
    # Get password from user (hidden input)
    password = getpass.getpass("Enter your team password: ")
    confirm = getpass.getpass("Confirm your team password: ")
    
    if password != confirm:
        print("\nError: Passwords don't match!")
        return
    
    if len(password) < 6:
        print("\nWarning: Password should be at least 6 characters for security.")
        proceed = input("Continue anyway? (y/n): ")
        if proceed.lower() != 'y':
            return
    
    # Generate hash
    password_hash = hash_password(password)
    
    print("\n" + "=" * 60)
    print("SUCCESS! Your password hash has been generated.")
    print("=" * 60)
    print("\nAdd this to your .streamlit/secrets.toml file:")
    print(f'\nTEAM_PASSWORD_HASH = "{password_hash}"')
    print("\nIMPORTANT: Keep your original password safe - you'll need it to log in!")
    print("=" * 60)

if __name__ == "__main__":
    main()
