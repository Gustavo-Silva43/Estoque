from django.urls import path
from . import views

app_name = 'core' # Isso registra o namespace 'core' para ser usado com reverse()

urlpatterns = [
    # Mapeia a URL raiz de 'core/' para a view 'index'
    path('', views.index, name='index'),

    # Mapeia 'core/products/' para a view 'product_list'
    # Ajuste o nome da URL 'products/' se quiser algo diferente
    path('products/', views.product_list, name='product_list'),
]