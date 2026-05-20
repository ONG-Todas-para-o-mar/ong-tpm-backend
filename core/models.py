from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_admin_ong = models.BooleanField(default=False)
    is_public_in_ranking = models.BooleanField(default=True)
    nickname = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.username or self.email


class Doador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doador")
    cpf = models.CharField(max_length=14, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=2, blank=True)
    cep = models.CharField(max_length=10, blank=True)
    total_doado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    desde = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-total_doado"]

    def __str__(self):
        return f"Doador<{self.user_id}>"


class Categoria(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    def __str__(self):
        return self.nome


class MetaCampanha(models.Model):
    titulo = models.CharField(max_length=160)
    descricao = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="metas")
    valor_alvo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prazo = models.DateField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "Meta"
        verbose_name_plural = "Metas"

    def __str__(self):
        return self.titulo


class Doacao(models.Model):
    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    FALHA = "falha"
    STATUS_CHOICES = [
        (PENDENTE, "Pendente"),
        (CONFIRMADA, "Confirmada"),
        (FALHA, "Falha"),
    ]

    doador = models.ForeignKey(Doador, on_delete=models.PROTECT, related_name="doacoes")
    meta = models.ForeignKey(MetaCampanha, on_delete=models.SET_NULL, null=True, blank=True, related_name="doacoes")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=PENDENTE)
    gateway_ref = models.CharField(max_length=120, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    confirmada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criada_em"]
        indexes = [models.Index(fields=["status", "criada_em"])]

    def __str__(self):
        return f"Doacao<{self.id}:{self.status}>"


class Badge(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    descricao = models.TextField(blank=True)
    icone = models.CharField(max_length=40, blank=True)
    criterio_valor = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["criterio_valor"]

    def __str__(self):
        return self.nome


class DoadorBadge(models.Model):
    doador = models.ForeignKey(Doador, on_delete=models.CASCADE, related_name="badges_obtidas")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="doadores")
    obtida_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("doador", "badge")]


class ImpactoLog(models.Model):
    tipo = models.CharField(max_length=60)
    descricao = models.TextField()
    valor_numerico = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    midia_url = models.URLField(blank=True)
    meta = models.ForeignKey(MetaCampanha, on_delete=models.SET_NULL, null=True, blank=True, related_name="impactos")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
