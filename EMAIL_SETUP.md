# Email Setup — B Labs

All system emails (welcome, OTP, forgot password) are sent from:

- **Sender:** B Labs &lt;updates@elvin-babanli.com&gt;
- **Domain:** elvin-babanli.com
- **Workspace:** Google Workspace

## 1. Google Workspace App Password

**Required for SMTP (535 = wrong credentials):**

1. Sign in to Google Account for updates@elvin-babanli.com
2. Security → **2-Step Verification** (must be enabled)
3. App passwords → Generate
4. App: Mail, Device: Other → name it "Django B Labs"
5. Copy the **16-character** password (no spaces when pasting into Render)

## 2. Render Environment Variables (Production)

**Required for email delivery:**

| Key | Value | Required |
|-----|-------|----------|
| `EMAIL_HOST` | `smtp.gmail.com` (never smtp-relay) | Yes |
| `EMAIL_HOST_USER` | `updates@elvin-babanli.com` | Yes |
| `EMAIL_HOST_PASSWORD` | 16-char App Password (no spaces) | Yes |
| `EMAIL_PORT` | `587` | No |
| `EMAIL_USE_TLS` | `True` | No |
| `DEFAULT_FROM_EMAIL` | `B Labs <updates@elvin-babanli.com>` | No |
| `SERVER_EMAIL` | `updates@elvin-babanli.com` | No |

**Critical:** Use `smtp.gmail.com` for authenticated submission. `smtp-relay.gmail.com` causes 550 relay denied.

### 550 "Mail relay denied" fix

- Set `EMAIL_HOST` to `smtp.gmail.com` (not smtp-relay)
- `EMAIL_HOST_USER` must match the From address (updates@elvin-babanli.com)
- Code derives envelope sender from `EMAIL_HOST_USER` automatically

### 535 "Username and Password not accepted" fix

- Ensure `EMAIL_HOST_USER` is exactly `updates@elvin-babanli.com` (no spaces)
- Ensure `EMAIL_HOST_PASSWORD` is the App Password (not account password)
- Paste App Password **without spaces** (16 chars)
- 2-Step Verification must be enabled
- No trailing newline — Render env values are trimmed in code

## 3. Local Development

Leave `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` empty → emails print to console.

## 4. Security

- Never commit passwords
- Use only environment variables
- `EMAIL_HOST_USER` must match the From address domain
