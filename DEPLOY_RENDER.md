# Deploy to Render — Production Checklist

## 1. Create PostgreSQL Database

1. In Render Dashboard → **New** → **PostgreSQL**
2. Create database (e.g. `django-codebase-db`)
3. Copy the **Internal Database URL** (or External if needed)

## 2. Create Web Service

1. **New** → **Web Service**
2. Connect your GitHub repo
3. **Build Command:**
   ```
   pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
   ```
   Or use: `./build.sh` (ensure build.sh is committed)

4. **Start Command:**
   ```
   gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
   ```

## 3. Environment Variables

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate a random 50-char string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app.onrender.com` (add custom domain too if needed) |
| `DATABASE_URL` | From Render PostgreSQL (auto-set if linked) |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.onrender.com` |

### Email (for Forgot Password)
| Key | Value |
|-----|-------|
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | e.g. `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | your email |
| `EMAIL_HOST_PASSWORD` | app password |
| `DEFAULT_FROM_EMAIL` | `noreply@yourdomain.com` |

## 4. Link Database

- In Web Service → **Environment** → **Add Environment Variable**
- Add `DATABASE_URL` and paste the Internal Database URL from step 1
- Or use Render's "Link Database" if available

## 5. Deploy

Push to main branch. Render will:
1. Install dependencies
2. Run migrations (creates auth_user, user_profiles, etc.)
3. Collect static files
4. Start gunicorn
