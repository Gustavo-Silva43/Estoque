from django.contrib.auth.models import User
from django.db import models
from core.models import TimeStampedModel
from produto.models import Produto
from django.urls import reverse_lazy
from .managers import EstoqueEntradaManager, EstoqueSaidaManager


MOVIMENTO = (
    ('e', 'entrada'),
    ('s', 'saida'),
)


class Estoque(TimeStampedModel):
    funcionario = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    nf = models.PositiveIntegerField('nota fiscal', null=True, blank=True)
    movimento = models.CharField(max_length=1, choices=MOVIMENTO, blank=True)

    class Meta:
        ordering = ('-created_at',)
        permissions = [
            ("pode_adicionar-estoque", "Pode adicionar novos itens ao estoque"),
            ("pode_excluir_estoque", "Pode excluir itens do estoque"),
            ("pode_ver_relatorios", "Pode ver relatórios de estoque"),
        ] 

    def __str__(self):
        if self.nf:
            return '{} - {} - {}'.format(self.pk, self.nf, self.created_at.strftime('%d-%m-%Y'))
        return '{} --- {}'.format(self.pk, self.created_at.strftime('%d-%m-%Y'))
    
    def nf_formated(self):
        if self.nf:
            return str(self.nf).zfill(3)
        return '---'


class EstoqueEntrada(Estoque):

    objects = EstoqueEntradaManager()

    class Meta:
        proxy = True
        verbose_name = 'estoque entrada'
        verbose_name_plural = 'estoque entrada'


class EstoqueSaida(Estoque):

    objects = EstoqueSaidaManager()

    class Meta:
        proxy = True
        verbose_name = 'estoque saída'
        verbose_name_plural = 'estoque saída'


class EstoqueItens(models.Model):
    estoque = models.ForeignKey(
        Estoque,
        on_delete=models.CASCADE,
        related_name='estoques'
    )
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    saldo = models.PositiveIntegerField(blank=True)

    class Meta:
        ordering = ('pk',)

    def __str__(self):
        return '{} - {} - {}'.format(self.pk, self.estoque.pk, self.produto)


class ProtocoloEntrega(TimeStampedModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estoque_atualizado = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse_lazy('estoque:protocolo_de_entrega_detail', kwargs={'pk': self.pk})


class ProtocoloEntregaItens(models.Model):
    protocolo_entrega = models.ForeignKey(
        ProtocoloEntrega,
        on_delete=models.CASCADE,
        related_name='protocolo_entrega_itens'
    )
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return '{} - {} - {}'.format(self.pk, self.protocolo_entrega.pk, self.produto)
