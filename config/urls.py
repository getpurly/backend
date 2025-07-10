from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/v1/addresses/", include("purly.address.urls")),
    path("api/v1/requisitions/", include("purly.requisition.urls")),
    path("api/v1/users/", include("purly.user.urls")),
    path("api/v1/projects/", include("purly.project.urls")),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
]

urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
