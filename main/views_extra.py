"""Extra views: robots.txt, favicon, error handlers."""
from django.http import HttpResponse
from django.shortcuts import redirect, render


def robots_txt(request):
    """Serve robots.txt."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /auth/",
        "Sitemap: /sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def favicon_redirect(request):
    """Redirect /favicon.ico to static favicon."""
    return redirect("/static/img/babanli_labs_logo.png", permanent=True)


def server_error(request):
    """Custom 500 handler - user-friendly error page."""
    return render(request, "500.html", status=500)
