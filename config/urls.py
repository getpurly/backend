from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from .exceptions import page_not_found, server_error

admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.index_title = settings.ADMIN_SITE_INDEX_TITLE
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.login = secure_admin_login(admin.site.login)  # type: ignore


def home(request):
    if request.user.is_authenticated:
        return redirect(settings.FRONTEND)

    return redirect("account_login")


handler404 = page_not_found
handler500 = server_error

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/v1/addresses/", include("purly.address.urls")),
    path("api/v1/approvals/", include("purly.approval.urls")),
    path("api/v1/projects/", include("purly.project.urls")),
    path("api/v1/requisitions/", include("purly.requisition.urls")),
    path("api/v1/users/", include("purly.user.urls")),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", home, name="home"),
]

if settings.DEBUG:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
