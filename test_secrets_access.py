import streamlit as st

print("Testing secrets access...")
print(f"All secrets keys: {list(st.secrets.keys())}")
print(f"TEAM_PASSWORD_HASH exists: {'TEAM_PASSWORD_HASH' in st.secrets}")
if 'TEAM_PASSWORD_HASH' in st.secrets:
    print(f"TEAM_PASSWORD_HASH value: {st.secrets['TEAM_PASSWORD_HASH']}")
else:
    print("TEAM_PASSWORD_HASH not found in secrets")
    
# Try different access methods
print("\nTrying st.secrets.get():")
print(f"Result: {st.secrets.get('TEAM_PASSWORD_HASH', 'NOT_FOUND')}")
