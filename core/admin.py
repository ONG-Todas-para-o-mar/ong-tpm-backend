from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Badge,
    Categoria,
    Doacao,
    Doador,
    DoadorBadge,
    ImpactoLog,
    MetaCampanha,
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_admin_ong", "is_public_in_ranking", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("TPM", {"fields": ("is_admin_ong", "is_public_in_ranking", "nickname")}),
    )


@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ("user", "total_doado", "city", "state", "desde")
    search_fields = ("user__username", "user__email")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(MetaCampanha)
class MetaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "valor_atual", "valor_alvo", "ativa", "prazo")
    list_filter = ("ativa", "categoria")
    search_fields = ("titulo",)


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "doador", "valor", "metodo", "status", "criada_em")
    list_filter = ("status", "metodo")
    search_fields = ("doador__user__username",)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "criterio_valor")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(DoadorBadge)
class DoadorBadgeAdmin(admin.ModelAdmin):
    list_display = ("doador", "badge", "obtida_em")


@admin.register(ImpactoLog)
class ImpactoLogAdmin(admin.ModelAdmin):
    list_display = ("tipo", "meta", "criado_em")
    list_filter = ("tipo",)
