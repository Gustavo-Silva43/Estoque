from django.shortcuts import render
import csv 
import io
from datetime import datetime 
import pandas as pd 
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect,JsonResponse
from django.shortcuts import render 
from django.urls import reverse
from django.views.generic import CreateView,ListView, UpdateView
import os
from django.conf import settings

from .actions.export_xlsx import export_xlsx
from .actions.import_xlsx import \
    import_xlsx as action_import_xlsx

from .forms import ProdutoForm
from .models import Produto, Categoria 

def produto_list(request):
    template_name = 'produto_list.html'
    objects = Produto.objects.all()
    search = request.GET.get('search')
    if search:
        objects = objects.filter(produto_icontains=search)
    context = {'object_list': objects}
    return render(request, template_name, context)

class ProdutoList(ListView):
    model = Produto
    template_name = 'produto_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super(ProdutoList, self).get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(produto__icontains=search) | 
                Q(ncm__icontains=search)   
            )
        return queryset 

def produto_detail(request, pk):
    template_name = 'produto_detail.html'
    obj = Produto.objects.get(pk=pk)
    context = {'object': obj}
    return render(request, template_name, context) 

def produto_add(request):
    form = ProdutoForm(request.POST or None)
    template_name = 'produto_form.html'

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('produto:produto_list'))

    context = {'form': form}
    return render(request,template_name, context)


class ProdutoCreate(CreateView):
    model = Produto
    template_name = 'produto_form.html'
    form_class = ProdutoForm

class ProdutoUpdate(UpdateView):
    model = Produto
    template_name = 'produto_form.html'
    form_class = ProdutoForm

def produto_json(request, pk):
    produto = Produto.objects.filter(pk=pk)
    data = [item.to_dict_json() for item in produto]
    return JsonResponse({'data': data})


def save_data(data): 
    aux = []
    for item in data:
        produto = item.get('produto')
        ncm = str(item.get('ncm'))
        importado = True if item.get('importado') == 'True' else False
        preco = item.get('preco')
        estoque = item.get('estoque')
        estoque_minimo = item.get('estoque_minimo')
        obj = Produto(
            produto=produto,
            ncm=ncm,
            importado=importado,
            preco=preco,
            estoque=estoque,
            estoque_minimo=estoque_minimo,
        )
        aux.append(obj)
    Produto.objects.bulk_create(aux)

def import_csv(request):
    template_name = 'produto_import.html'

    if request.method == 'POST':
        myfile = request.FILES.get('myfile')  

        if myfile:  
            try:
                file_data = myfile.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(file_data))
                data = [line for line in reader]
                save_data(data)  
                messages.success(request, "Dados importados com sucesso!")
                return HttpResponseRedirect(reverse('produto:produto_list'))
            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo CSV: {e}")
        else:  
            messages.error(request, "Nenhum arquivo foi selecionado para upload.")

    return render(request, template_name)


def export_csv(request):
    header = (
        'importado','ncm', 'produto','preco','estoque','estoque_minimo',
    )
    produtos = Produto.objects.all().values_list(*header)

    export_dir = 'fix' 

    from django.conf import settings
    full_export_path = os.path.join(settings.BASE_DIR, export_dir)

    os.makedirs(full_export_path, exist_ok=True) 
    file_path = os.path.join(full_export_path, 'produtos_exportados.csv')

    with open(file_path, 'w', newline='') as csvfile: 
        produto_writer = csv.writer(csvfile)
        produto_writer.writerow(header)
        for produto in produtos:
            produto_writer.writerow(produto)

    messages.success(request, 'Produtos exportados com sucesso.')
    return HttpResponseRedirect(reverse('produto:produto_list'))

def import_xlsx(request):
    filename = os.path.join(settings.BASE_DIR, 'fix', 'produtos.xlsx') 
    action_import_xlsx(filename) 
    messages.success(request, 'Produto(s) importado(s) com sucesso.')
    return HttpResponseRedirect(reverse('produto:produto_list'))


def exportar_produtos_xlsx(request):
    MDATA = datetime.now().strftime('%Y-%m-%d')
    model = 'Produto'
    base_filename = 'produto_exportados.xlsx' 
    _filename_parts = base_filename.rsplit('.', 1) 

    filename_final = f'{_filename_parts[0]}_{MDATA}.{_filename_parts[1]}'

    queryset = Produto.objects.all().values_list(
        'importado',
        'ncm',
        'produto',
        'preco',
        'estoque',
        'estoque_minimo',
        'categoria__categoria',
    )
    columns = ('Importado', 'NCM', 'Produto', 'Preco',
               'Estoque', 'Estoque_mínimo', 'Categoria')


    response = export_xlsx(model, filename_final, queryset, columns) 
    return response

def import_csv_with_pandas(request):
    filename = os.path.join(settings.BASE_DIR, 'fix', 'produtos.csv') 
    
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        messages.error(request, f"Arquivo {filename} não encontrado.")
        return HttpResponseRedirect(reverse('produto:produto_list'))
    except Exception as e:
        messages.error(request, f"Erro ao ler o arquivo CSV: {e}")
        return HttpResponseRedirect(reverse('produto:produto_list'))
    
    for index, row in df.iterrows(): 
        try:
            produto_nome = row[0]
            ncm_val = row[1]
            importado_val = row[2]
            preco_val = row[3]
            estoque_val = row[4]
            estoque_minimo_val = row[5]
            obj, created = Produto.objects.update_or_create(
                produto=produto_nome, 
                defaults={
                    'ncm': ncm_val,
                    'importado': importado_val,
                    'preco': preco_val,
                    'estoque': estoque_val,
                    'estoque_minimo': estoque_minimo_val,
                }
            )
            
            if created:
                messages.info(request, f"Produto '{produto_nome}' criado com sucesso.")
            else:
                messages.info(request, f"Produto '{produto_nome}' atualizado com sucesso.")
            
        except Exception as e:
            messages.error(request, f"Erro ao processar produto '{produto_nome}' na linha {index}: {e}")

    messages.success(request, 'Processo de importação/atualização de produtos concluído.')
    return HttpResponseRedirect(reverse('produto:produto_list'))
