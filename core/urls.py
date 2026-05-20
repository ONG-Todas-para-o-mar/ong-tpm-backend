from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register("categorias", views.CategoriaViewSet, basename="categoria")
router.register("metas", views.MetaViewSet, basename="meta")
router.register("doacoes", views.DoacaoViewSet, basename="doacao")
router.register("badges", views.BadgeViewSet, basename="badge")
router.register("impacto", views.ImpactoLogViewSet, basename="impacto")

urlpatterns = [
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    path("me/", views.MeView.as_view(), name="me"),
    path("doadores/me/", views.DoadorMeView.as_view(), name="doador-me"),

    path("ranking/", views.RankingView.as_view(), name="ranking"),
    path("dashboard/publico/", views.DashboardPublicoView.as_view(), name="dashboard-publico"),
    path("dashboard/admin/", views.AdminStatsView.as_view(), name="dashboard-admin"),

    path("", include(router.urls)),
]
