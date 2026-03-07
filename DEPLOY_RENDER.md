# Render Deploy — Portfolio Site

## Önerilen Ayarlar

### Build Command
```
pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```
veya `./build.sh` (build.sh varsa)

### Start Command
```
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```
**Önemli:** Sadece gunicorn. `start.sh` veya migrate kullanma.

### Neden?
- **migrate** Build sırasında çalışır; tablolar oluşturulur
- **Start** sadece gunicorn başlatır; site hemen açılır
- `start.sh` ile migrate, hata alırsa gunicorn hiç başlamaz → beyaz ekran

---

## Environment Variables

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Rastgele 50 karakter |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `elvin-babanli.com,www.elvin-babanli.com,.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://elvin-babanli.com,https://www.elvin-babanli.com` |

### PostgreSQL (kalıcı veri için)
- New → PostgreSQL
- Web service’e bağla → `DATABASE_URL` otomatik gelir

---

## Sorun Giderme

| Sorun | Çözüm |
|-------|--------|
| Beyaz ekran / site açılmıyor | Start Command’da sadece gunicorn olmalı; migrate Build’de |
| auth_user yok | Build Command’a `python manage.py migrate --noinput` ekle |
| robots.txt / favicon 404 | Son commit deploy edildi mi kontrol et |
