from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import Badge, Categoria, MetaCampanha


CATEGORIAS = [
    "Educação", "Surf", "Saúde", "Empreendedorismo", "Cultura", "Ambiental",
]

BADGES = [
    ("Maré", "Primeira doação confirmada.", "wave", 1),
    ("Coral", "R$ 5.000 doados acumulados.", "shell", 5000),
    ("Albatroz", "R$ 15.000 doados acumulados.", "wing", 15000),
]

PROJETOS = [
    ("Surf na Baía", "Aulas gratuitas de surf para crianças e adolescentes da comunidade.", "Surf"),
    ("Mulheres do Mar", "Empreendedorismo e geração de renda para mulheres negras.", "Empreendedorismo"),
    ("Onda Antirracista", "Formação cultural e socioeducativa antirracista.", "Cultura"),
    ("Mães da Maré", "Apoio integral a mães chefes de família.", "Saúde"),
    ("Pequenas Surfistas", "Núcleo dedicado a meninas iniciantes no surf.", "Surf"),
    ("Bem-Viver Costeiro", "Saúde, bem-estar e educação ambiental para a comunidade.", "Saúde"),
]


class Command(BaseCommand):
    help = "Seed inicial: categorias, badges e projetos base."

    def handle(self, *args, **options):
        for nome in CATEGORIAS:
            Categoria.objects.get_or_create(nome=nome, defaults={"slug": slugify(nome)})

        for nome, descricao, icone, criterio in BADGES:
            Badge.objects.get_or_create(
                nome=nome,
                defaults={
                    "slug": slugify(nome),
                    "descricao": descricao,
                    "icone": icone,
                    "criterio_valor": criterio,
                },
            )

        for titulo, descricao, cat_nome in PROJETOS:
            cat = Categoria.objects.get(nome=cat_nome)
            MetaCampanha.objects.get_or_create(
                titulo=titulo,
                defaults={
                    "descricao": descricao,
                    "categoria": cat,
                    "valor_alvo": 0,
                    "ativa": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed concluído."))
