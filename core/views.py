from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (
    Badge,
    Categoria,
    Doacao,
    Doador,
    ImpactoLog,
    MetaCampanha,
)
from .permissions import IsAdminOng, IsAdminOngOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    BadgeSerializer,
    CategoriaSerializer,
    DoacaoSerializer,
    DoadorSerializer,
    ImpactoLogSerializer,
    MetaSerializer,
    RankingEntrySerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class DoadorMeView(generics.RetrieveAPIView):
    serializer_class = DoadorSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Doador.objects.get(user=self.request.user)


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]


class MetaViewSet(viewsets.ModelViewSet):
    queryset = MetaCampanha.objects.select_related("categoria").all()
    serializer_class = MetaSerializer
    permission_classes = [IsAdminOngOrReadOnly]
    filterset_fields = ["ativa", "categoria"]
    search_fields = ["titulo", "descricao"]

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def progresso(self, request, pk=None):
        meta = self.get_object()
        pct = 0
        if meta.valor_alvo and meta.valor_alvo > 0:
            pct = round(float(meta.valor_atual / meta.valor_alvo) * 100, 2)
        return Response({
            "meta": meta.id,
            "valor_atual": meta.valor_atual,
            "valor_alvo": meta.valor_alvo,
            "progresso_pct": pct,
        })


class DoacaoViewSet(viewsets.ModelViewSet):
    serializer_class = DoacaoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ["status", "metodo"]
    ordering_fields = ["criada_em", "valor"]

    def get_queryset(self):
        user = self.request.user
        qs = Doacao.objects.select_related("doador__user", "meta")
        if user.is_admin_ong:
            return qs
        return qs.filter(doador__user=user)

    def perform_create(self, serializer):
        doador = Doador.objects.get(user=self.request.user)
        serializer.save(doador=doador)


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [AllowAny]


class ImpactoLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImpactoLog.objects.select_related("meta").all()
    serializer_class = ImpactoLogSerializer
    permission_classes = [AllowAny]


class RankingView(generics.ListAPIView):
    serializer_class = RankingEntrySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Doador.objects.filter(user__is_public_in_ranking=True, total_doado__gt=0)
            .select_related("user")
            .order_by("-total_doado")[:50]
        )

    def list(self, request, *args, **kwargs):
        rows = []
        for idx, d in enumerate(self.get_queryset(), start=1):
            name = d.user.get_full_name() or d.user.nickname or d.user.username
            top_badge = (
                d.badges_obtidas.select_related("badge")
                .order_by("-badge__criterio_valor")
                .first()
            )
            rows.append({
                "rank": idx,
                "name": name,
                "total": d.total_doado,
                "donations_count": d.doacoes.filter(status=Doacao.CONFIRMADA).count(),
                "since": d.desde,
                "badge": top_badge.badge.nome if top_badge else "",
            })
        return Response(self.get_serializer(rows, many=True).data)


class DashboardPublicoView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        confirmed = Doacao.objects.filter(status=Doacao.CONFIRMADA)
        total = confirmed.aggregate(s=Sum("valor"))["s"] or 0
        donors = Doador.objects.filter(total_doado__gt=0).count()
        donations_count = confirmed.count()

        since = timezone.now() - timedelta(days=14)
        daily = (
            confirmed.filter(criada_em__gte=since)
            .extra(select={"day": "date(criada_em)"})
            .values("day")
            .annotate(total=Sum("valor"), count=Count("id"))
            .order_by("day")
        )

        return Response({
            "total_arrecadado": total,
            "doadores_ativos": donors,
            "doacoes_confirmadas": donations_count,
            "ticket_medio": float(total / donors) if donors else 0,
            "serie_14d": list(daily),
        })


class AdminStatsView(generics.GenericAPIView):
    permission_classes = [IsAdminOng]

    def get(self, request):
        confirmed = Doacao.objects.filter(status=Doacao.CONFIRMADA)
        by_method = list(
            confirmed.values("metodo").annotate(total=Sum("valor"), count=Count("id"))
        )
        pending = Doacao.objects.filter(status=Doacao.PENDENTE).count()
        return Response({
            "total_arrecadado": confirmed.aggregate(s=Sum("valor"))["s"] or 0,
            "doacoes_pendentes": pending,
            "por_metodo": by_method,
        })
