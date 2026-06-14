from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.urls import include, path

from apps.users.web import views as accounts_views


def home(request):
    return render(request, "home.html")


urlpatterns = [
    path("", home, name="home"),
    path("api/accounts/", include("apps.users.api")),
    path("login/", accounts_views.login_view, name="login"),
    path("logout/", accounts_views.logout_view, name="logout"),
    path("register/", accounts_views.register_view, name="register"),
    path("profile/", accounts_views.profile_view, name="profile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
