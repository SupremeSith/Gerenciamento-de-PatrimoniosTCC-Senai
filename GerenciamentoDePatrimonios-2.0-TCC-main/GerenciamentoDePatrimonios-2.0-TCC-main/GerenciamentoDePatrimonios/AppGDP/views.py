from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from .forms import FormLogin, formCadastroUsuario, InventarioForm, SalaForm
from .models import Senai
from django.contrib.auth.models import User, Group
from .models import Inventario, Sala
from django.core.cache import cache
from django.http import HttpResponse
from .models import Inventario
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from rest_framework.response import Response
from django.http import JsonResponse
import json
import logging
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test



# Create your views here.

def homepage(request):
    # Se o usuário já estiver autenticado, redirecione para outra página
    if request.user.is_authenticated:
        return redirect('welcomeHomepage')  # Substitua pelo nome da página desejada
    return render(request, 'homepage.html')

def login(request):
    return render(request, 'login.html')


def profile(request):
    return render(request, 'profile.html')

def faq(request):
    return render(request, 'faq.html')

from django.contrib.auth.models import Group


#logouut 
def logout(request):
    auth_logout(request)
    return redirect('login')

def filtrar_por_status(inventario, status):
    """
    Aplica o filtro ao inventário com base no status fornecido.
    """
    if status:
        inventario = inventario.filter(status_localizacao=status)
        print(f"Filtro aplicado: {status}")  # Para depuração
    else:
        print("Nenhum filtro aplicado.")
    return inventario


def contar_total_itens(inventario):
    """
    Retorna a contagem total de itens no inventário.
    """
    return inventario.count()

def aplicar_filtros_inventario(inventario, params):
    """
    Aplica filtros ao inventário com base nos parâmetros fornecidos.
    """
    query = params.get('q')  
    ordem = params.get('ordem')  
    sala = params.get('sala')  
    status = params.get('status')  

    if query:
        inventario = inventario.filter(num_inventario__icontains=query)
        
    if sala:
        inventario = inventario.filter(sala__icontains=sala)
        
    if status:
        inventario = inventario.filter(status_localizacao=status)
        
    if ordem == "A-Z":
        inventario = inventario.order_by('denominacao')
    elif ordem == "Z-A":
        inventario = inventario.order_by('-denominacao')
    
    return inventario



def contar_status(inventario):
    """
    Retorna a contagem de itens localizados e não localizados.
    """
    total_localizados = inventario.filter(status_localizacao='localizado').count()
    total_nao_localizados = inventario.filter(status_localizacao='nao_localizado').count()
    return total_localizados, total_nao_localizados


def filtrar_inventario_por_grupo(user, is_coordenador, is_professor):
    """
    Filtra o inventário com base no grupo do usuário.
    - Coordenador vê todos os itens.
    - Professor vê apenas os itens das salas que ele gerencia.
    - Outros usuários não veem nada.
    """
    if is_coordenador:
        return Inventario.objects.all()  # Coordenador vê todos os itens
    elif is_professor:
        salas_responsavel = Sala.objects.filter(responsavel=user.username).values_list('sala', flat=True)
        return Inventario.objects.filter(sala__in=salas_responsavel)  # Professor vê itens de suas salas
    return Inventario.objects.none()  # Usuário sem permissão não vê nada


def aplicar_filtros_inventario(inventario, query, ordem, sala):
    """
    Aplica filtros de pesquisa, ordenação e sala ao inventário.
    """
    if query:
        inventario = inventario.filter(num_inventario__icontains=query)
    if ordem:
        inventario = inventario.order_by('denominacao' if ordem == 'A-Z' else '-denominacao')
    if sala:
        inventario = inventario.filter(sala__icontains=sala)
    return inventario

def aplicar_filtros_salas(salas, query, ordem):
    """
    Aplica os filtros de pesquisa e ordenação às salas.
    """
    if query:
        salas = salas.filter(sala__icontains=query)
    if ordem:
        salas = salas.order_by('sala' if ordem == 'A-Z' else '-sala')
    return salas

def verificar_grupo_usuario(user):
    """
    Verifica se o usuário pertence aos grupos 'Coordenador' ou 'Professor'.
    """
    is_coordenador = user.groups.filter(name="Coordenador").exists()
    is_professor = user.groups.filter(name="Professor").exists()
    return is_coordenador, is_professor

def filtrar_salas(user, is_coordenador, is_professor):
    """
    Filtra as salas com base no grupo do usuário.
    """
    if is_coordenador:
        return Sala.objects.all()  # Coordenador vê todas as salas
    elif is_professor:
        return Sala.objects.filter(responsavel=user.username)  # Professor vê salas específicas
    return []  # Usuário sem grupo relevante não vê nada

def grupo_coordenador_required(view_func):
    decorator = user_passes_test(
        lambda user: user.groups.filter(name='Coordenador').exists(),
        login_url='/welcomeHomepage',  # Redireciona se o usuário não for do grupo Coordenador
        redirect_field_name=None  # Remove o parâmetro ?next= no redirecionamento
    )
    return decorator(view_func)

@login_required
def welcomeHomepage(request):
    """
    View principal para a página de boas-vindas.
    """
    # Verifica os grupos do usuário
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)

    # Filtra as salas com base nos grupos
    sala = filtrar_salas(request.user, is_coordenador, is_professor)

    # Processa o formulário
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('welcomeHomepage')
    else:
        form = SalaForm()


    # Renderiza a página com o contexto adequado
    return render(request, 'welcomeHomepage.html', {
        'form': form,
        'sala': sala,
        'is_coordenador': is_coordenador,
        'is_professor': is_professor,
    })




# Importar o modelo de itens (substitua Item pelo nome correto do seu modelo)


#---------------------------- CRUD DE SALAS ----------------------------
@login_required
def buscar_salas(request):
    """
    View para buscar e filtrar salas.
    """
    # Contexto inicial
    context = {}

    # Verifica os grupos do usuário
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)

    # Adiciona informações de grupos ao contexto
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor

    # Filtra as salas com base nos grupos
    salas = filtrar_salas(request.user, is_coordenador, is_professor)

    # Aplica filtros de pesquisa e ordenação
    query = request.GET.get('q')
    ordem = request.GET.get('ordem')
    salas = aplicar_filtros_salas(salas, query, ordem)

    # Adiciona salas e formulário ao contexto
    context['sala'] = salas
    context['form'] = SalaForm()

    # Renderiza a página com o contexto
    return render(request, 'salas.html', context)

@login_required
def buscar_itens_sala(request):
    """
    View para buscar itens de inventário com base na sala e permissões do usuário.
    """
    # Contexto inicial
    context = {}

    # Obtém os parâmetros da requisição
    query = request.GET.get('q')  
    ordem = request.GET.get('ordem')  
    sala = request.GET.get('sala')  

    # Verifica grupos do usuário
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)

    # Filtra o inventário com base no grupo
    inventario = filtrar_inventario_por_grupo(request.user, is_coordenador, is_professor)

    # Aplica filtros adicionais
    inventario = aplicar_filtros_inventario(inventario, query, ordem, sala)
    
    # Recupera o status da querystring
    status = request.GET.get('status')

    # Filtra o inventário pelo status
    inventario = filtrar_por_status(inventario, status)

    # Calcula os totais
    total_itens = contar_total_itens(inventario)
    total_localizados, total_nao_localizados = contar_status(inventario)


    # Adiciona informações ao contexto
    context['inventario'] = inventario
    context['form'] = InventarioForm()
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor
    context['total_itens'] = total_itens  # Adiciona a quantidade de itens ao contexto
    context['total_localizados'] = total_localizados

    # Renderiza a página
    return render(request, 'itens.html', context)



@login_required
def adicionar_salas(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('welcomeHomepage')
    else:
        form = SalaForm()

    sala = Sala.objects.all()
    
    return render(request, 'welcomeHomepage.html', {'form': form, 'sala': sala, 'errors': form.errors})
@login_required
def update_sala(request):
    if request.method == 'POST':
        sala = request.POST.get('sala')
        
        # Busca a sala no banco de dados
        sala = get_object_or_404(Sala, sala=sala)

        # Atualiza os valores com base nos dados do formulário
        sala.descricao = request.POST.get('descricao')
        sala.localizacao = request.POST.get('localizacao')
        sala.link_imagem = request.POST.get('link_imagem')	
        sala.responsavel = request.POST.get('responsavel')
        sala.quantidade_itens = request.POST.get('quantidade_itens')
        sala.email_responsavel = request.POST.get('email_responsavel')
        sala.save()

        # Redireciona de volta à página de salas ou para onde você quiser
        return redirect('salas')  

    return HttpResponse("Método não permitido.", status=405)
@login_required
def excluir_sala(request):
    if request.method == 'POST':
        sala = request.POST.get('sala')
        
        # Exclui a sala com base no nome
        try:
            sala = Sala.objects.get(sala=sala)
            sala.delete()
            return redirect('salas')  # Redireciona para a lista de salas após exclusão
        except Sala.DoesNotExist:
            return HttpResponse("Sala não encontrada.", status=404)

@login_required
def salas(request):
    context = {}
    # Verifica os grupos do usuário
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)

    # Filtra as salas com base no grupo do usuário
    sala = filtrar_salas(request.user, is_coordenador, is_professor)

    # Gerenciamento de formulário (caso aplicável)
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('salas')
    else:
        form = SalaForm()

    form = SalaForm()
    context['form'] = form
    context['sala'] = sala
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor

    return render(request, 'salas.html', context)


#---------------------------- LOGIN E CADASTRO DE USUÁRIO ----------------------------
@grupo_coordenador_required
@login_required
def cadastroUsuario(request):
    if not request.user.groups.filter(name='Coordenador').exists():
        return redirect('/login')  # Redireciona para a página de login ou qualquer outra página
    
    context = {}
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)
    dadosSenai = Senai.objects.all()
    context["dadosSenai"] = dadosSenai
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor
    
    if request.method == 'POST':
        form = formCadastroUsuario(request.POST)
        if form.is_valid():
            var_nome = form.cleaned_data['first_name']
            var_sobrenome = form.cleaned_data['last_name']
            var_usuario = form.cleaned_data['user']
            var_email = form.cleaned_data['email']
            var_senha = form.cleaned_data['password']
            var_grupo = form.cleaned_data['group']  # Captura o grupo selecionado
            var_sala = form.cleaned_data['sala']  # Captura a sala selecionada
            # Cria o usuário
            user = User.objects.create_user(username=var_usuario, email=var_email, password=var_senha)
            user.first_name = var_nome
            user.last_name = var_sobrenome
            user.save()

            # Atribui o usuário ao grupo selecionado
            grupo = Group.objects.get(name=var_grupo)
            user.groups.add(grupo)
            

            return redirect('/welcomeHomepage')
            print('Cadastro realizado com sucesso')
    else:
        form = formCadastroUsuario()
        context['form'] = form
        print('Cadastro falhou')
    
    return render(request, 'cadastroUsuario.html', context)


def login(request):
    context = {}
    dadosSenai = Senai.objects.all()
    context["dadosSenai"] = dadosSenai
    
    if request.method == 'POST':
        form = FormLogin(request.POST)
        if form.is_valid():
            var_usuario = form.cleaned_data['user']
            var_senha = form.cleaned_data['password']
            
            user = authenticate(username=var_usuario, password=var_senha)

            if user is not None:
                auth_login(request, user)
                return redirect('/welcomeHomepage')  
            else:
                # Adiciona uma mensagem de erro
                messages.error(request, 'Usuário ou senha inválidos. Por favor, tente novamente.')
        else:
            messages.error(request, 'Erro ao validar o formulário.')
    else:
        form = FormLogin()
    
    context['form'] = form
    return render(request, 'login.html', context)

#---------------------------- CRUD DE INVENTÁRIO ----------------------------
@login_required
def itens(request):
    context = {}
    # Verifica os grupos do usuário
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)

    # Filtra o inventário com base no grupo do usuário
    inventario = filtrar_inventario_por_grupo(request.user, is_coordenador, is_professor)

    # Recupera o status da querystring

    query = request.GET.get('q')  
    ordem = request.GET.get('ordem')  
    sala = request.GET.get('sala')  
    status = request.GET.get('status')  
    if query:
        inventario = inventario.filter(num_inventario__icontains=query)
        
    if sala:
        inventario = inventario.filter(sala__icontains=sala)
        
    if status:
        inventario = inventario.filter(status_localizacao=status)
        
    if ordem == "A-Z":
        inventario = inventario.order_by('denominacao')
    elif ordem == "Z-A":
        inventario = inventario.order_by('-denominacao')

    # Calcula os totais
    total_itens = contar_total_itens(inventario)
    total_localizados, total_nao_localizados = contar_status(inventario)

    # Gerenciamento de formulário (caso aplicável)
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('itens')  # Redireciona para a página de itens
    else:
        form = InventarioForm()

    # Adiciona informações ao contexto
    context['form'] = form
    context['inventario'] = inventario
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor
    context['total_itens'] = total_itens
    context['total_localizados'] = total_localizados
    context['total_nao_localizados'] = total_nao_localizados
    context['status'] = status

    return render(request, 'itens.html', context)


    
    

@login_required
def adicionar_inventario(request):
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecionar para a rota inicial, independente de onde estava
    else:
        form = InventarioForm()
    
    # Se precisar listar todos os itens no modal de adição, inclua isso:
    inventario = Inventario.objects.all()
    
    return render(request, 'itens.html', {'form': form, 'inventario': inventario})

@login_required
def buscar_itens(request):
    context = {}
    query = request.GET.get('q')  # Pega o valor do campo de busca
    ordem = request.GET.get('ordem')  # Pega o valor da ordem A-Z ou Z-A
    sala = request.GET.get('sala')  # Pega o valor da sala
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)

    # Filtra o inventário com base no grupo do usuário
    inventario = filtrar_inventario_por_grupo(request.user, is_coordenador, is_professor)

    # Aplica filtros de pesquisa e ordenação
    inventario = aplicar_filtros_inventario(inventario, query, ordem, sala)
    total_itens = inventario.count()  # Caso seja um queryset, .count() funciona be

    context['inventario'] = inventario
    form = InventarioForm()
    context['form'] = form
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor
    context['total_itens'] = total_itens  # Adiciona a quantidade de itens ao contexto

    return render(request, 'itens.html', context)


@login_required
def update_item(request):
    if request.method == 'POST':
        num_inventario = request.POST.get('numInventario')
        
        # Busca o item no banco de dados
        item = get_object_or_404(Inventario, num_inventario=num_inventario)

        # Atualiza os valores com base nos dados do formulário
        item.denominacao = request.POST.get('denominacao')
        item.localizacao = request.POST.get('localizacao')
        item.sala = request.POST.get('sala')
        item.link_imagem = request.POST.get('imagem')
        item.save()

        # Redireciona de volta à página de itens ou para onde você quiser
        return redirect('itens')  

    return HttpResponse("Método não permitido.", status=405)
@login_required
def excluir_inventario(request):
    if request.method == 'POST':
        num_inventario = request.POST.get('numInventario')
        
        # Exclui o item com base no número de inventário
        try:
            item = Inventario.objects.get(num_inventario=num_inventario)
            item.delete()
            return redirect('itens')  # Redireciona para a lista de itens após exclusão
        except Inventario.DoesNotExist:
            return HttpResponse("Item não encontrado.", status=404)
        




#---------------------------- PROFILE ----------------------------


@login_required
def profile(request):
    user = request.user
    sala = Sala.objects.filter(responsavel=user).first()  # Assume que 'responsavel' é o campo que liga o usuário à sala
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)
    if request.method == 'POST':
        # Atualiza os campos do usuário apenas se forem fornecidos novos valores
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Exibe uma mensagem de sucesso
        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect('profile')  # Redireciona para evitar múltiplos envios do formulário

    context = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'id': user.id,
        'sala': sala.sala if sala else "Nenhuma sala atribuída",
        'is_coordenador': is_coordenador,
        'is_professor': is_professor,
    }

    return render(request, 'profile.html', context)





#---------------------------- Usuários ----------------------------#
@grupo_coordenador_required
@login_required
def gerenciar_usuarios(request):
    context = {}
    # Obtenha todos os usuários e informações dos grupos
    is_coordenador, is_professor = verificar_grupo_usuario(request.user)
    usuarios = User.objects.all().select_related()
    usuarios_info = []

    for user in usuarios:
        # Obtenha o grupo do usuário
        user_groups = user.groups.values_list('name', flat=True)
        role = "Professor" if "Professor" in user_groups else "Coordenador" if "Coordenador" in user_groups else ""

        # Adiciona o usuário e seu papel ao dicionário
        usuarios_info.append({
            'user': user,
            'role': role
        })

    # Processa o formulário de atualização de usuário
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.username = request.POST.get('username', user.username)
            user.email = request.POST.get('email', user.email)
            password = request.POST.get('password')
            
            # Atualiza a senha apenas se fornecida
            if password:
                user.set_password(password)
            
            user.save()
            return redirect('gerenciar_usuarios')
        except User.DoesNotExist:
            pass  # Gerencie erros se necessário
    
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor
    context['usuarios_info'] = usuarios_info
    return render(request, 'usuarios.html', context)


@login_required
def editar_usuario(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        return redirect('gerenciar_usuarios')
    
@login_required
def excluir_usuario(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.delete()
    return redirect('gerenciar_usuarios')


#---------------------------- FUNÇÕES DA API ----------------------------
@api_view(['POST'])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Autenticação do usuário
    user = authenticate(username=username, password=password)

    if user is not None:
        # Verificar se o usuário pertence ao grupo 'Coordenador' ou 'Professor'
        if user.groups.filter(name="Coordenador").exists():
            user_type = "Coordenador"
        elif user.groups.filter(name="Professor").exists():
            user_type = "Professor"
        else:
            user_type = "Outro"  # Caso o usuário não pertença a nenhum desses grupos
        
        # Autenticação bem-sucedida
        return Response({
            "message": "Login bem-sucedido", 
            "user": user.username,
            "user_type": user_type ,
            "first_name": user.first_name,
        })
    else:
        # Falha na autenticação
        return Response({"error": "Credenciais inválidas"}, status=400)

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_salas(request):
    """
    View para retornar todas as salas em formato JSON.
    """
    salas = Sala.objects.all().values('id', 'sala', 'descricao', 'localizacao', 'link_imagem', 'responsavel')
    return Response(list(salas), status=200)


@api_view(['GET'])
def get_inventarios(request):
    """
    View para retornar todos os inventários em formato JSON.
    """
    inventarios = Inventario.objects.all().values(
        'id', 
        'num_inventario',  # Aqui estão os campos do seu modelo
        'denominacao', 
        'localizacao', 
        'link_imagem', 
        'sala'
    )
    return Response(list(inventarios), status=200)

@api_view(['POST'])
def add_inventario(request):
    """
    View para adicionar um novo inventário (patrimônio) no banco de dados.
    """
    try:
        data = json.loads(request.body)  # Tenta carregar o JSON
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Dados inválidos ou mal formatados'}, status=400)

    denominacao = data.get('denominacao')
    localizacao = data.get('localizacao')
    sala = data.get('sala')
    link_imagem = data.get('link_imagem')
    num_inventario = data.get('num_inventario')

    # Validar os dados recebidos
    if not denominacao or not localizacao or not sala or not num_inventario:
        return JsonResponse({'message': 'Dados faltando'}, status=400)

    # Verifique se o num_inventario já existe
    if Inventario.objects.filter(num_inventario=num_inventario).exists():
        return JsonResponse({'message': 'num_inventario já existe.'}, status=400)

    # Criar o inventário (patrimônio)
    try:
        inventario = Inventario.objects.create(
            denominacao=denominacao,
            localizacao=localizacao,
            sala=sala,
            link_imagem=link_imagem,
            num_inventario=num_inventario
        )
        return JsonResponse({'message': 'Inventário adicionado com sucesso!'}, status=201)
    except IntegrityError:
        return JsonResponse({'message': 'Erro ao adicionar inventário, tente novamente.'}, status=400)
    
    
@api_view(['DELETE'])
def delete_inventario(request):
    num_inventario = request.data.get('num_inventario')  # Obtém o num_inventario do corpo da requisição
    if not num_inventario:
        return Response({"detail": "Número de inventário não fornecido."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        patrimonio = Inventario.objects.get(num_inventario=num_inventario)
        patrimonio.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Inventario.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

@csrf_exempt
def editar_inventario(request):
    if request.method in ['POST', 'PUT']:
        # Se for PUT, processa o JSON manualmente
        if request.method == 'PUT':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST

        num_inventario = data.get('num_inventario')
        denominacao = data.get('denominacao')
        localizacao = data.get('localizacao')
        sala = data.get('sala')
        link_imagem = data.get('link_imagem')

        # Busca o item no banco de dados
        item = get_object_or_404(Inventario, num_inventario=num_inventario)

        # Atualiza os valores
        item.denominacao = denominacao
        item.localizacao = localizacao
        item.sala = sala
        item.link_imagem = link_imagem
        item.save()

        return JsonResponse({"message": "Item atualizado com sucesso."}, status=200)

    return JsonResponse({"error": "Método não permitido."}, status=405)


@api_view(['POST'])
def add_sala(request):
    """
    View para adicionar uma nova sala no banco de dados.
    """
    try:
        data = json.loads(request.body)  # Tenta carregar o JSON
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Dados inválidos ou mal formatados'}, status=400)

    sala = data.get('sala')
    descricao = data.get('descricao')
    localizacao = data.get('localizacao')
    link_imagem = data.get('link_imagem')
    responsavel = data.get('responsavel')
    email_responsavel = data.get('email_responsavel')

    # Validar os dados recebidos
    if not sala or not descricao or not localizacao or not responsavel:
        return JsonResponse({'message': 'Dados faltando'}, status=400)
    
     # Verifique campos específicos
    erro_campos = []
    if Sala.objects.filter(sala=sala).exists():
        erro_campos.append("sala")
    if Sala.objects.filter(localizacao=localizacao).exists():
        erro_campos.append("localizacao")
    if Sala.objects.filter(email_responsavel=email_responsavel).exists():
        erro_campos.append("email_responsavel")
        
    if erro_campos:
        return JsonResponse({'message': 'Valores duplicados', 'fields': erro_campos}, status=400)


    # Verifique se a sala já existe
    if Sala.objects.filter(sala=sala).exists():
        return JsonResponse({'message': 'Sala já existe.'}, status=400)

    # Criar a sala
    try:
        sala_obj = Sala.objects.create(
            sala=sala,
            descricao=descricao,
            localizacao=localizacao,
            link_imagem=link_imagem,
            responsavel=responsavel,
            email_responsavel=email_responsavel,
        )
        return JsonResponse({'message': 'Sala adicionada com sucesso!'}, status=201)
    
    except IntegrityError:
        return JsonResponse({'message': 'Erro ao adicionar sala, tente novamente.'}, status=400)


@api_view(['GET'])
def get_inventarios_por_sala(request):
    """
    View para retornar os inventários associados a uma sala pelo nome da sala.
    """
    nome_sala = request.query_params.get('sala')
    
    if not nome_sala:
        return Response({"error": "Nome da sala não fornecido."}, status=400)

    # Busca os patrimônios pela sala
    inventarios = Inventario.objects.filter(sala=nome_sala).values(
        'id',
        'num_inventario',
        'denominacao',
        'localizacao',
        'link_imagem',
        'sala',
    )

    if not inventarios:
        return Response({"message": "Nenhum patrimônio encontrado para essa sala."}, status=404)

    return Response(list(inventarios), status=200)

@api_view(['DELETE'])
def delete_sala(request):
    """
    View para deletar uma sala do banco de dados.
    """
    sala_nome = request.data.get('sala')  # Obtém o nome da sala do corpo da requisição
    if not sala_nome:
        return Response({"detail": "Nome da sala não fornecido."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        sala = Sala.objects.get(sala=sala_nome)
        sala.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Sala.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    
@csrf_exempt
def editar_sala(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)

            # Identificação da sala pelo nome
            sala_nome = data.get('sala')
            if not sala_nome:
                return JsonResponse({'error': 'O campo sala é necessário para identificar o registro.'}, status=400)

            # Buscar a sala no banco de dados
            sala = get_object_or_404(Sala, sala=sala_nome)

            # Atualizar os campos permitidos
            sala.descricao = data.get('descricao', sala.descricao)
            sala.localizacao = data.get('localizacao', sala.localizacao)
            sala.link_imagem = data.get('link_imagem', sala.link_imagem)
            sala.responsavel = data.get('responsavel', sala.responsavel)
            sala.email_responsavel = data.get('email_responsavel', sala.email_responsavel)

            # Salvar as mudanças
            sala.save()

            return JsonResponse({'message': 'Sala editada com sucesso!'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato de dados inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Ocorreu um erro: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)


@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            first_name = data.get("first_name")
            last_name = data.get("last_name")
            username = data.get("user")
            email = data.get("email")
            password = data.get("password")
            group_name = data.get("group")
            sala = data.get("sala")

            # Verifica se o e-mail ou o nome de usuário já está cadastrado
            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email já cadastrado."}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Nome de usuário já cadastrado."}, status=400)

            # Cria o usuário
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Adiciona o usuário ao grupo especificado
            if group_name:
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    return JsonResponse({"error": "Grupo não encontrado."}, status=400)

            # Salva a sala do usuário (supondo que seja um campo de perfil ou similar)
            # Aqui seria o lugar onde você salvaria a `sala` caso seja necessária no perfil do usuário.
            # Se precisar de um relacionamento mais complexo, considere um perfil ou modelo específico.

            return JsonResponse({"message": "Usuário cadastrado com sucesso."})

        except IntegrityError:
            return JsonResponse({"error": "Erro ao salvar usuário."}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Método não permitido."}, status=405)


@api_view(['GET'])
def user_data(request):
    username = request.headers.get('Authorization')

    if username:  # Verifica se o username foi fornecido
        try:
            user = User.objects.get(username=username)
            user_info = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                # Adicione outros campos que você deseja retornar aqui
            }
            return Response(user_info, status=200)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=404)
    return Response({'error': 'Username não fornecido.'}, status=400)


@csrf_exempt
@require_http_methods(["PUT"])
def update_user_data(request):
    try:
        data = json.loads(request.body)
        username = request.headers.get('Authorization')

        if not username:
            return JsonResponse({'error': 'Username not provided'}, status=400)
        
        user = User.objects.get(username=username)
        
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()

        return JsonResponse({'message': 'Dados atualizados com sucesso'})

    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def get_user_room(request):
    if request.method == "POST":
        try:
            # Carrega o JSON com o username
            data = json.loads(request.body)
            username = data.get("username")

            if not username:
                return JsonResponse({'error': 'Username is required.'}, status=400)

            # Busca o usuário pelo username
            user = User.objects.get(username=username)
            
            # Procura a sala onde o email do responsável coincide com o email do usuário
            room = Sala.objects.filter(email_responsavel=user.email).first()
            
            if room:
                # Retorna os detalhes da sala, se encontrada
                return JsonResponse({
                    'sala': room.sala,
                    'descricao': room.descricao,
                    'localizacao': room.localizacao,
                    'link_imagem': room.link_imagem,
                    'responsavel': room.responsavel,
                    'email_responsavel': room.email_responsavel
                })
            else:
                return JsonResponse({'message': 'No room found for this user.'}, status=404)
        
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
@csrf_exempt
def atualizar_status_localizacao(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            num_inventario = data.get('num_inventario')

            # Verifica se o número de inventário foi enviado
            if not num_inventario:
                return JsonResponse({'error': 'Número de inventário não informado'}, status=400)

            # Busca o inventário no banco de dados
            inventario = Inventario.objects.filter(num_inventario=num_inventario).first()

            if not inventario:
                return JsonResponse({'error': 'Inventário não encontrado'}, status=404)

            # Atualiza o status para "localizado"
            inventario.status_localizacao = 'localizado'
            inventario.save()

            return JsonResponse({'message': 'Status atualizado com sucesso'}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Ocorreu um erro: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método não permitido'}, status=405)
