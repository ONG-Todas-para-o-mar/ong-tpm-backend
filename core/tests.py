from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from core.models import Badge, Categoria, Doacao, Doador, MetaCampanha, User


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome="Surf", slug="surf")


@pytest.fixture
def meta(db, categoria):
    return MetaCampanha.objects.create(
        titulo="Pequenas Surfistas",
        categoria=categoria,
        valor_alvo=Decimal("10000"),
    )


@pytest.fixture
def doador_user(db):
    return User.objects.create_user(username="marina", email="m@x.com", password="senha12345")


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin", email="admin@tpm.local", password="senha12345", is_admin_ong=True
    )


@pytest.mark.django_db
def test_register_creates_doador(api):
    r = api.post(
        "/api/auth/register/",
        {"username": "novo", "email": "n@x.com", "password": "AbcDef1234"},
        format="json",
    )
    assert r.status_code == 201
    assert Doador.objects.filter(user__username="novo").exists()


@pytest.mark.django_db
def test_login_returns_jwt(api, doador_user):
    r = api.post(
        "/api/auth/login/",
        {"username": "marina", "password": "senha12345"},
        format="json",
    )
    assert r.status_code == 200
    assert "access" in r.data and "refresh" in r.data


@pytest.mark.django_db
def test_me_requires_auth(api, doador_user):
    assert api.get("/api/me/").status_code == 401
    api.force_authenticate(doador_user)
    assert api.get("/api/me/").status_code == 200


@pytest.mark.django_db
def test_metas_list_public(api, meta):
    r = api.get("/api/metas/")
    assert r.status_code == 200
    assert r.data["count"] == 1


@pytest.mark.django_db
def test_metas_create_requires_admin(api, doador_user, admin_user, categoria):
    payload = {"titulo": "Nova", "categoria_id": categoria.id, "valor_alvo": 100}
    api.force_authenticate(doador_user)
    assert api.post("/api/metas/", payload, format="json").status_code == 403
    api.force_authenticate(admin_user)
    assert api.post("/api/metas/", payload, format="json").status_code == 201


@pytest.mark.django_db
def test_doacao_flow_updates_totals(api, doador_user, meta):
    api.force_authenticate(doador_user)
    r = api.post(
        "/api/doacoes/",
        {"valor": "100.00", "metodo": "pix", "meta": meta.id},
        format="json",
    )
    assert r.status_code == 201

    doacao = Doacao.objects.get(pk=r.data["id"])
    doacao.status = Doacao.CONFIRMADA
    doacao.save()

    doador = Doador.objects.get(user=doador_user)
    assert doador.total_doado == Decimal("100.00")
    meta.refresh_from_db()
    assert meta.valor_atual == Decimal("100.00")


@pytest.mark.django_db
def test_badge_unlocks_on_confirmed_donation(api, doador_user):
    Badge.objects.create(nome="Maré", slug="mare", criterio_valor=Decimal("1"))
    api.force_authenticate(doador_user)
    r = api.post("/api/doacoes/", {"valor": "50.00", "metodo": "pix"}, format="json")
    doacao = Doacao.objects.get(pk=r.data["id"])
    doacao.status = Doacao.CONFIRMADA
    doacao.save()

    doador = Doador.objects.get(user=doador_user)
    assert doador.badges_obtidas.filter(badge__slug="mare").exists()


@pytest.mark.django_db
def test_ranking_excludes_zero_donors(api, doador_user):
    r = api.get("/api/ranking/")
    assert r.status_code == 200
    assert r.data == []


@pytest.mark.django_db
def test_dashboard_publico_returns_zeros_initially(api):
    r = api.get("/api/dashboard/publico/")
    assert r.status_code == 200
    assert r.data["total_arrecadado"] == 0
