# Hockey Stats App - Authentication Setup

This app uses a simple team password authentication system to protect your hockey statistics.

## Setting Up Authentication

### 1. Generate Your Password Hash

First, you need to create a hashed version of your team password:

```bash
python generate_password_hash.py
```

This will:
- Prompt you to enter your team password (hidden input)
- Generate a SHA-256 hash of your password
- Display the hash to add to your secrets

### 2. Add Password Hash to Streamlit Secrets

#### For Local Development

Create or edit `.streamlit/secrets.toml`:

```toml
TEAM_PASSWORD_HASH = "your_generated_hash_here"
```

#### For Streamlit Community Cloud

1. Go to your app dashboard on Streamlit Community Cloud
2. Click on "Settings" → "Secrets"
3. Add the following:

```toml
TEAM_PASSWORD_HASH = "your_generated_hash_here"
```

### 3. Share the Password with Your Team

Share the original password (not the hash!) with your team members. They'll use this to log in.

## How It Works

1. When users visit the app, they'll see a login screen
2. They enter the team password
3. The password is hashed and compared to the stored hash
4. If correct, they gain access to the dashboard
5. The session remains active until they logout or close the browser

## Security Notes

- Never commit the actual password or hash to your repository
- Use a strong password (at least 8 characters, mix of letters/numbers)
- The password is hashed using SHA-256 for security
- Passwords are never stored in plain text
- Consider changing the password periodically

## Troubleshooting

**"Incorrect password" error:**
- Ensure you're entering the exact password (case-sensitive)
- Check that the hash in secrets matches what was generated

**Can't generate hash:**
- Make sure you have Python installed
- Run the script from the project directory

**Authentication not working on deployment:**
- Verify the TEAM_PASSWORD_HASH is properly set in Streamlit secrets
- Check for any typos in the hash value
