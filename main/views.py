from django.shortcuts import render
from django.http import HttpResponse

from .home_news import get_home_feed


def get4o4(request):
    return render(request, "4o4.html")

# Frameworks____________________________________________
def get_django(request):
    return render(request, "django.html")

def get_flask(request):
    return render(request, "flask.html")


# Libraries_____________________________________________
def get_pandas(request):
    return render(request,"pandas.html")

def get_numpy(request):
    return render(request,"numpy.html")

def get_matplotlib(request):
    return render(request,"matplotlib.html")

# Pages_________________________________________________

def get_git(request):
    return render(request,"git.html")

def get_crud(request):
    return render(request,"crud.html")

def get_python_basics(request):
    return render(request,"python_basics.html")

def valentine_page(request):
    return render(request,"valentine.html")


# Projects______________________________________________

# def weather_app(request):
#     return render(request, "weather_app.html")

def home(request):
    articles_ai = get_home_feed()
    
    context = {
        "articles_ai": articles_ai,       
        "articles": articles_ai,  
        # lazım ola biləcək digər listlər də varsa, hamısına boş dəyər ver:
        # "projects": [],
        # "news": [],
        # "tools": [],
    }
    return render(request, "index.html", context)


def about(request):
    profile = {
        "name": "Elvin Babanlı",
        "title": "AI Engineer & Web Developer · Python ",
        "location": "Warsaw, Poland",
        "email": "elvinbabanli0@gmail.com",
        "github": "https://github.com/elvin-babanli",
        "linkedin": "https://www.linkedin.com/in/elvin-babanl%C4%B1-740038240/",
        "instagram": "https://www.instagram.com/elvin_babanli/",
        "skills": [
            "Python",
            "Django",
            "Flask",
            "FastAPI",
            "REST API",
            "Machine Learning-Basics",
            "Pandas",
            "NumPy",
            "TensorFlow-Basics",
            "HTML/CSS",
            "Bootstrap",
            "SQL",
            "PostgreSQL",
            "Git",
            "GitHub",
            "APIs & Integrations",
            "Automation Scripts"
        ],
        "projects": [
            {"name":"Django Store","url":"https://github.com/elvin-babanli/Django-store"},
            {"name":"Django CRUD","url":"https://github.com/elvin-babanli/Django-CRUD"},
            {"name":"Summarizer","url":"https://github.com/elvin-babanli/summerizer"},
            {"name":"Django Web Online","url":"https://github.com/elvin-babanli/Django-web-online"},
            {"name":"Cheap Flight Finder","url":"https://github.com/elvin-babanli/Cheap_Flight_Finder"},
            {"name":"Stock Predictor","url":"https://github.com/elvin-babanli/Stock_Predictor"},
            {"name":"Weather Control App","url":"https://github.com/elvin-babanli/Weather-control-app"},
            {"name":"Cashly V1.9","url":"https://github.com/elvin-babanli/Cashly_V1.9"},
        ],
    }
    return render(request, "about.html", {"profile": profile})