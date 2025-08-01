from django.urls import path, include
from . import views 

app_name = 'estoque'

entrada_patterns = [
    path('', views.EstoqueEntradaList.as_view(), name='estoque_entrada_list'),
    path('add/', views.estoque_entrada_add, name='estoque_entrada_add'),
    path('<int:pk>/', views.estoque_entrada_detail, name='estoque_entrada_detail'),
]

saida_patterns = [
    path('', views.EstoqueSaidaList.as_view(), name='estoque_saida_list'),
    path('add/', views.estoque_saida_add, name='estoque_saida_add'),
]

entrega_patterns = [
    path('<int:pk>/', views.protocolo_de_entrega, name='protocolo_de_entrega_detail'),
    path('', views.protocolo_de_entrega, name='protocolo_de_entrega_list'), 
    path(
        '<int:pk>/dar_baixa/',
        views.dar_baixa_no_estoque_com_protocolo_de_entrega,
        name='dar_baixa'
    ),
]

urlpatterns = [
    path('<int:pk>/', views.EstoqueDetail.as_view(), name='estoque_detail'),
    path('entrada/', include(entrada_patterns)),
    path('saida/', include(saida_patterns)),
    path('entrega/', include(entrega_patterns)),
]