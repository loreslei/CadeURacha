import traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Arena, Jogo
from .forms import ArenaForm, EditProfileForm, CustomPasswordChangeForm, JogoForm
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, timezone
from django.utils import timezone
from django.db.models import Q
from django.contrib.messages import get_messages

def register(request):
    # Handle GET request - show registration form
    
    if request.method == 'GET':
        return render(request, 'app_synes/register.html')
    
    # Handle POST request
    if request.method == 'POST':
        # Check if request is AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                return JsonResponse({'success': False, 'message': 'As senhas não coincidem.'})

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Nome de usuário já existe.'})

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'E-mail já está registrado.'})

            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            return JsonResponse({'success': True, 'message': 'Cadastro realizado com sucesso!'})
        
        # Handle non-AJAX POST request
        return render(request, 'app_synes/register.html')

    # Handle other methods
    return HttpResponseNotAllowed(['GET', 'POST'])

def login_view(request):
    if request.method == 'POST':
        login_input = request.POST['login']
        password = request.POST['password']
        
        # Check if login_input is an email or username
        if '@' in login_input:
            try:
                user = CustomUser.objects.get(email=login_input)
                username = user.username
            except CustomUser.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid email or password'})
        else:
            username = login_input
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Login efetuado com sucesso!'})
        else:
            return JsonResponse({'success': False, 'message': 'Usuário/E-mail ou senha inválidos.'})
    
    return render(request, 'app_synes/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    """
    View para a página inicial.
    """
    return render(request, "app_synes/index.html")

def map_view(request):
    arenas = Arena.objects.all().order_by('nome')
    neighborhoods = Arena.objects.values_list('bairro', flat=True).distinct().order_by('bairro')
    return render(request, 'app_synes/map.html', {'arenas': arenas, 'neighborhoods': neighborhoods})

@login_required
def cadastrar_arena(request):
    if request.method == 'POST':
        form = ArenaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ArenaForm()
    return render(request, 'app_synes/cadastrar_arena.html', {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = EditProfileForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        
        if 'username' in request.POST or 'email' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Perfil atualizado com sucesso.')
            else:
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, error, extra_tags='danger')
        
        if 'old_password' in request.POST or 'new_password1' in request.POST or 'new_password2' in request.POST:
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)  # Important!
                messages.success(request, 'Senha alterada com sucesso.')
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        if field == 'old_password' and 'incorrect' in error.lower():
                            messages.error(request, 'A senha atual está incorreta.', extra_tags='danger')
                        elif 'The two password fields didn’t match.' in error:
                            messages.error(request, 'Os dois campos de senha não coincidem.', extra_tags='danger')
                        else:
                            messages.error(request, error, extra_tags='danger')
        
        return redirect('edit_profile')
    else:
        profile_form = EditProfileForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'app_synes/edit_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

@login_required
def confirm_delete_account(request):
    return render(request, 'app_synes/confirm_delete_account.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        messages.success(request, 'Sua conta foi desativada com sucesso.')
        return redirect('index')
    return redirect('confirm_delete_account')

def criar_jogo(request):
    if request.method == 'POST':
        form = JogoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('nome_da_view_de_sucesso')
    else:
        form = JogoForm()
    return render(request, 'app_synes/criar_jogo.html', {'form': form})

@login_required
def cadastrar_jogo(request):
    if request.method == 'POST':
        form = JogoForm(request.POST)
        if form.is_valid():
            try:
                jogo = form.save(commit=False)
                jogo.usuario = request.user  # Set the usuario field to the current user
                jogo.save()

                # Verificar o valor direto do banco
                jogo_db = Jogo.objects.get(id=jogo.id)
                print("Horário lido do banco:", repr(jogo_db.horario))
                
                messages.success(request, 'Jogo criado com sucesso!')
                jogos = Jogo.objects.all()
                return render(request, 'app_synes/listar_todos_jogos.html', {'jogos': jogos})
            except Exception as e:
                print(f"Erro ao salvar jogo: {e}")
                print("Traceback completo:", traceback.format_exc())
                messages.error(request, 'Erro ao salvar o jogo')
        else:
            print("Erros no formulário:", form.errors)
    else:
        form = JogoForm()
    return render(request, 'app_synes/cadastrar_jogo.html', {'form': form})

@login_required
def listar_jogos(request):
    jogos = Jogo.objects.all()
    storage = get_messages(request)
    for message in storage:
        print(f"Mensagem: {message}")
    jogos = Jogo.objects.filter(usuario=request.user)
    return render(request, 'app_synes/listar_jogos.html', {'jogos': jogos})

def listar_todos_jogos(request):
    jogos = Jogo.objects.all()
    return render(request, 'app_synes/listar_todos_jogos.html', {'jogos': jogos})

def search(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        if len(query) >= 2:
            # Primeiro pesquisar arenas
            arenas = Arena.objects.filter(
                Q(nome__icontains=query) |
                Q(bairro__icontains=query)
            )[:5]  # Limit results

            # IDs das arenas encontradas
            arena_ids = [arena.id for arena in arenas]

            # Pesquisar jogos relacionados à query ou às arenas encontradas
            jogos = Jogo.objects.filter(
                Q(titulo__icontains=query) |
                Q(descricao__icontains=query) |
                Q(arena_id__in=arena_ids)
            ).select_related('arena')[:5]  # Limit results and optimize query

            results = {
                'arenas': [
                    {
                        'id': arena.id,
                        'nome': arena.nome,
                        'endereco': f"{arena.bairro}, {arena.cidade}",
                        'tipo': 'quadra'
                    } for arena in arenas
                ],
                'jogos': [
                    {
                        'id': jogo.id,
                        'titulo': jogo.titulo,
                        'arena': jogo.arena.nome,
                        'data': jogo.data.strftime('%d/%m/%Y'),
                        'horario': str(jogo.horario),
                        'tipo': 'jogo'
                    } for jogo in jogos
                ]
            }
            return JsonResponse(results)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def editar_jogo(request, id):
    jogo = get_object_or_404(Jogo, id=id)
    jogos = Jogo.objects.all()
    if request.method == 'POST':
        form = JogoForm(request.POST, instance=jogo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jogo atualizado com sucesso!')
            return redirect('listar_jogos')
            
        else:
            messages.error(request, 'Erro ao atualizar jogo.')
    else:
        form = JogoForm(instance=jogo)
    return render(request, 'app_synes/editar_jogo.html', {'form': form, 'jogo': jogo})

@login_required
def excluir_jogo(request, id):
    jogo = get_object_or_404(Jogo, id=id)
    if request.method == 'POST':
        jogo.delete()
        messages.success(request, 'Jogo excluído com sucesso!')
        return redirect('listar_jogos')
    return render(request, 'app_synes/excluir_jogo.html', {'jogo': jogo})