# Render Deploy — Portfolio Site

## Build Command

```
pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

## Start Command

```
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```

## Environment Variables

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Random 50+ characters |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `elvin-babanli.com,www.elvin-babanli.com,.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://elvin-babanli.com,https://www.elvin-babanli.com` |

### PostgreSQL

- Create PostgreSQL → connect to web service → `DATABASE_URL` auto-set

### Email (B Labs) — required for welcome/OTP

| Key | Value |
|-----|-------|
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | `updates@elvin-babanli.com` |
| `EMAIL_HOST_PASSWORD` | Google Workspace App Password (16 chars, no spaces) |
| `DEFAULT_FROM_EMAIL` | `B Labs <updates@elvin-babanli.com>` |
| `SERVER_EMAIL` | `updates@elvin-babanli.com` |

See `EMAIL_SETUP.md` for 535 troubleshooting.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 535 Username and Password not accepted | Use App Password (not account password), 2FA on, paste without spaces |
| Verification code not received | Check `EMAIL_HOST_PASSWORD` in Render Dashboard |
| Blank page | Start Command: gunicorn only; migrate in Build |
