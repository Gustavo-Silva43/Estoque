
from django.contrib import admin
from .models import Produto 

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'importado',
        'ncm',
        'produto',
        'preco',
        'estoque',
        'estoque_minimo',
    )
    search_fields = ('produto',)
    list_filter = ('importado',)
    actions = ('export_as_csv', 'export_as_xlsx')

    class Media:
        js = (
            'https://code.jquery.com/jquery-3.3.1.min.js',
            '/static/js/estoque_admin.js'
        )

    def export_as_csv(self, request, queryset):
