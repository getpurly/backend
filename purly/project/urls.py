from rest_framework import routers

from .views import ProjectViewSet

router = routers.SimpleRouter()

router.register(r"", ProjectViewSet, basename="projects")

urlpatterns = router.urls
