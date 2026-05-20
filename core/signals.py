from decimal import Decimal

from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Badge, Doacao, Doador, DoadorBadge, User


@receiver(post_save, sender=User)
def ensure_doador(sender, instance, created, **kwargs):
    if created and not instance.is_admin_ong:
        Doador.objects.get_or_create(user=instance)


@receiver(post_save, sender=Doacao)
def on_doacao_saved(sender, instance, created, **kwargs):
    if instance.status != Doacao.CONFIRMADA:
        return

    if instance.confirmada_em is None:
        instance.confirmada_em = timezone.now()
        Doacao.objects.filter(pk=instance.pk).update(confirmada_em=instance.confirmada_em)

    Doador.objects.filter(pk=instance.doador_id).update(
        total_doado=F("total_doado") + instance.valor
    )

    if instance.meta_id:
        from .models import MetaCampanha

        MetaCampanha.objects.filter(pk=instance.meta_id).update(
            valor_atual=F("valor_atual") + instance.valor
        )

    doador = Doador.objects.get(pk=instance.doador_id)
    for badge in Badge.objects.filter(criterio_valor__lte=doador.total_doado):
        DoadorBadge.objects.get_or_create(doador=doador, badge=badge)
