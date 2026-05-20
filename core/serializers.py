from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password", "nickname"]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        if not validated_data.get("username"):
            validated_data["username"] = validated_data["email"]
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_admin_ong", "is_public_in_ranking", "nickname"]
        read_only_fields = ["is_admin_ong"]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "nome", "slug", "descricao", "icone", "criterio_valor"]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome", "slug"]


class MetaSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        source="categoria", queryset=Categoria.objects.all(), write_only=True
    )
    progresso_pct = serializers.SerializerMethodField()

    class Meta:
        model = MetaCampanha
        fields = [
            "id",
            "titulo",
            "descricao",
            "categoria",
            "categoria_id",
            "valor_alvo",
            "valor_atual",
            "progresso_pct",
            "prazo",
            "ativa",
            "criada_em",
        ]
        read_only_fields = ["valor_atual", "criada_em"]

    def get_progresso_pct(self, obj):
        if obj.valor_alvo and obj.valor_alvo > 0:
            return round(float(obj.valor_atual / obj.valor_alvo) * 100, 2)
        return 0


class DoadorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    badges = serializers.SerializerMethodField()

    class Meta:
        model = Doador
        fields = ["id", "user", "phone", "city", "state", "total_doado", "desde", "badges"]
        read_only_fields = ["total_doado", "desde"]

    def get_badges(self, obj):
        return BadgeSerializer(
            [db.badge for db in obj.badges_obtidas.select_related("badge").all()],
            many=True,
        ).data


class DoacaoSerializer(serializers.ModelSerializer):
    doador = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Doacao
        fields = [
            "id",
            "doador",
            "meta",
            "valor",
            "metodo",
            "status",
            "gateway_ref",
            "criada_em",
            "confirmada_em",
        ]
        read_only_fields = ["status", "gateway_ref", "criada_em", "confirmada_em", "doador"]


class DoadorBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = DoadorBadge
        fields = ["id", "badge", "obtida_em"]


class ImpactoLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactoLog
        fields = ["id", "tipo", "descricao", "valor_numerico", "midia_url", "meta", "criado_em"]


class RankingEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    name = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    donations_count = serializers.IntegerField()
    since = serializers.DateField()
    badge = serializers.CharField(allow_blank=True)
