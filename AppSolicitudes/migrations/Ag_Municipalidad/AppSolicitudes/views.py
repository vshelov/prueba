from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Solicitud
from .forms import SolicitudUsuarioForm
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# Decorador para verificar roles
def user_in_group(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorator

# Página principal (sin autenticación)
def inicio(request):
    return render(request, 'inicio.html')

# Dashboard del Administrador
@login_required
@user_in_group('Administrador')
def administrador_dashboard(request):
    return render(request, 'inicio_adm.html')  # Plantilla del Administrador

# Dashboard del Vendedor
@login_required
@user_in_group('Vendedor')
def vendedor_dashboard(request):
    return render(request, 'vendedor/dashboard_vendedor.html')  # Plantilla del Vendedor

# Ingresar solicitud
def ingresar_solicitud(request):
    if request.method == 'POST':
        form = SolicitudUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Solicitud enviada correctamente!")
            return redirect('inicio')  # Redirige al inicio o a la página que prefieras
    else:
        form = SolicitudUsuarioForm()
    return render(request, 'solicitudes/ingresar_solicitud.html', {'form': form})

# Crear solicitud
@login_required
def crear_solicitud(request):
    if request.method == 'POST':
        form = SolicitudUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Solicitud creada correctamente.")
            return redirect('listar_solicitudes')
    else:
        form = SolicitudUsuarioForm()
    return render(request, 'solicitudes/crear_solicitud.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from AppSolicitudes.models import Solicitud

@login_required
def listar_solicitudes(request):
    rut_filtrado = request.GET.get('rut', '').strip()
    solicitudes = Solicitud.objects.none()  # Inicializa como vacío
    mensaje_no_encontrado = False  # Variable para controlar el mensaje

    if rut_filtrado:
        rut_normalizado = rut_filtrado.replace('.', '').upper()
        solicitudes = Solicitud.objects.filter(rut=rut_normalizado)
        mensaje_no_encontrado = not solicitudes.exists()  # Activa mensaje si no hay resultados
    else:
        solicitudes = Solicitud.objects.all()  # Muestra todas si no hay filtro

    # Clasifica las solicitudes según su estado
    solicitudes_pendientes = solicitudes.filter(estado='pendiente')
    solicitudes_aceptadas = solicitudes.filter(estado='aceptada')
    solicitudes_rechazadas = solicitudes.filter(estado='rechazada')
    solicitudes_expiradas = solicitudes.filter(estado='expirada')

    # Renderiza la plantilla con las solicitudes y el estado del mensaje
    return render(request, 'solicitudes/ListarSolicitud.html', {
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aceptadas': solicitudes_aceptadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'solicitudes_expiradas': solicitudes_expiradas,
        'rut_query': rut_filtrado,  # Mantén el valor en el formulario
        'mensaje_no_encontrado': mensaje_no_encontrado,  # Controla el mensaje
    })

# Editar el estado de una solicitud
@login_required
@permission_required('AppSolicitudes.change_solicitud', raise_exception=True)
def editar_estado_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        solicitud.estado = nuevo_estado
        if nuevo_estado == 'aceptada':
            solicitud.fecha_aceptacion = timezone.now()
        else:
            solicitud.fecha_aceptacion = None
        solicitud.save()
        messages.success(request, "Estado de la solicitud actualizado correctamente.")
        return redirect('listar_solicitudes')
    return render(request, 'solicitudes/editar_solicitud.html', {'solicitud': solicitud})

# Ver detalles de una solicitud
@login_required
def detalles_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    return render(request, 'solicitudes/detalle_solicitud.html', {'solicitud': solicitud})

# Eliminar solicitud
@login_required
@permission_required('AppSolicitudes.delete_solicitud', raise_exception=True)
def eliminar_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, f"Solicitud de {solicitud.nombre} eliminada correctamente.")
        return redirect('listar_solicitudes')
    return render(request, 'solicitudes/eliminar_solicitud.html', {'solicitud': solicitud})

# Buscar solicitudes
@login_required
def buscar_solicitud(request):
    rut = request.GET.get('rut', None)
    solicitudes = Solicitud.objects.filter(rut=rut) if rut else []
    return render(request, 'solicitudes/buscar_solicitud.html', {
        'solicitudes': solicitudes,
        'rut_query': rut,
    })

# Redirección basada en roles en login_view
from django.shortcuts import redirect

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Verificar si el email está asociado a un usuario
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'El correo no está registrado.')
            return render(request, 'usuarios/login.html')

        # Autenticar usando el username del usuario
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)

            # Verificar el grupo al que pertenece el usuario
            if user.groups.filter(name='Administrador').exists():
                return redirect('administrador_dashboard')  # Redirige al panel de admin
            elif user.groups.filter(name='Vendedor').exists():
                return redirect('vendedor_dashboard')  # Redirige al panel de vendedor
            else:
                messages.error(request, 'No tienes permisos para acceder.')
                return render(request, 'usuarios/login.html')
        else:
            messages.error(request, 'Contraseña incorrecta.')
            return render(request, 'usuarios/login.html')
    return render(request, 'usuarios/login.html')


@login_required
def inicio_adm(request):
    return render(request, 'inicio_adm.html')

def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        rol = request.POST.get('rol')

        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('crear_usuario')

        if User.objects.filter(username=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return redirect('crear_usuario')

        try:
            # Crear el usuario
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido
            )
            # Asignar grupo
            group = Group.objects.get(name=rol)
            user.groups.add(group)

            messages.success(request, f"Usuario '{email}' creado con éxito.")
            return redirect('administrador_dashboard')
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")
            return redirect('crear_usuario')

    return render(request, 'panel_admin/crear_usuario.html')



@login_required
@permission_required('auth.add_user', raise_exception=True)
def crear_usuario(request):
    roles = Group.objects.values_list('name', flat=True)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rol = request.POST.get('rol')  # 'Administrador' o 'Vendedor'

        if User.objects.filter(username=email).exists():
            messages.error(request, "El usuario ya existe.")
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=nombre,
                last_name=apellido,
                password=password
            )
            group = Group.objects.get(name=rol)
            user.groups.add(group)

            # Mostrar mensaje de éxito
            messages.success(request, f"Usuario '{user.username}' creado con éxito.")
            
        # Recargar la misma página para mantener el formulario
        return render(request, 'panel_admin/crear_usuario.html', {'roles': roles})

    return render(request, 'panel_admin/crear_usuario.html', {'roles': roles})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def listar_usuarios(request):
    # Filtro de usuarios
    query = request.GET.get('q')
    if query:
        usuarios = User.objects.filter(username__icontains=query)  # Filtro por nombre de usuario
    else:
        usuarios = User.objects.all()

    # Eliminación de usuario
    if request.method == 'POST' and 'eliminar_usuario' in request.POST:
        user_id = request.POST.get('eliminar_usuario')
        try:
            user_to_delete = User.objects.get(id=user_id)
            user_to_delete.delete()
            messages.success(request, f"El usuario {user_to_delete.username} ha sido eliminado.")
        except User.DoesNotExist:
            messages.error(request, "El usuario no existe.")

    # Restablecimiento de contraseña
    if request.method == 'POST' and 'restablecer_contraseña' in request.POST:
        user_id = request.POST.get('restablecer_contraseña')
        new_password = request.POST.get('nueva_contraseña')
        try:
            user_to_reset = User.objects.get(id=user_id)
            user_to_reset.set_password(new_password)
            user_to_reset.save()
            messages.success(request, f"Contraseña del usuario {user_to_reset.username} restablecida.")
        except User.DoesNotExist:
            messages.error(request, "El usuario no existe.")

    return render(request, 'panel_admin/listar_usuarios.html', {'usuarios': usuarios, 'query': query})


# AppSolicitudes/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def perfil(request):
    if request.method == 'POST':
        # Si es un POST, intentamos cambiar la contraseña
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Guardar la nueva contraseña
            form.save()
            # Mantener la sesión activa después de cambiar la contraseña
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('perfil')  # Redirigimos a la misma página para evitar reenvíos de formulario
        else:
            messages.error(request, 'Hubo un error al cambiar la contraseña. Asegúrate de que las contraseñas coincidan.')

    else:
        # Si es un GET, mostramos el perfil y el formulario de cambio de contraseña
        form = PasswordChangeForm(request.user)

    return render(request, 'perfil.html', {'usuario': request.user, 'form': form})

@login_required
def cambiar_contraseña(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validaciones
        if not request.user.check_password(old_password):
            messages.error(request, 'La contraseña actual no es correcta.')
            return redirect('perfil')

        if new_password != confirm_password:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return redirect('perfil')

        if len(new_password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('perfil')

        # Si las contraseñas son válidas
        user = request.user
        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)  # Mantiene al usuario autenticado
        messages.success(request, 'Tu contraseña ha sido cambiada con éxito.')
        return redirect('perfil')
    
    return render(request, 'perfil.html')

# Vista para el listado de solicitudes para el vendedor
def listar_solicitudes_vendedor(request):
    solicitudes_pendientes = Solicitud.objects.filter(estado='pendiente')
    return render(request, 'vendedor/ListarSolicitudesVendedor.html', {
        'solicitudes_pendientes': solicitudes_pendientes,
    })
    
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def perfil_vendedor(request):
    if request.method == 'POST':
        # Si es un POST, intentamos cambiar la contraseña
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Guardar la nueva contraseña
            form.save()
            # Mantener la sesión activa después de cambiar la contraseña
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('perfil_vendedor')  # Redirigimos a la misma página para evitar reenvíos de formulario
        else:
            messages.error(request, 'Hubo un error al cambiar la contraseña. Asegúrate de que las contraseñas coincidan.')

    else:
        # Si es un GET, mostramos el perfil y el formulario de cambio de contraseña
        form = PasswordChangeForm(request.user)

    return render(request, 'vendedor/perfil_vendedor.html', {'usuario': request.user, 'form': form})
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def cambiar_contraseña_vendedor(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validaciones
        if not request.user.check_password(old_password):
            messages.error(request, 'La contraseña actual no es correcta.')
            return redirect('perfil_vendedor')  # Redirige al perfil vendedor

        if new_password != confirm_password:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return redirect('perfil_vendedor')  # Redirige al perfil vendedor

        if len(new_password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('perfil_vendedor')  # Redirige al perfil vendedor

        # Si las contraseñas son válidas
        user = request.user
        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)  # Mantiene al usuario autenticado
        messages.success(request, 'Tu contraseña ha sido cambiada con éxito.')
        return redirect('perfil_vendedor')  # Redirige al perfil vendedor después de un cambio exitoso

    return render(request, 'perfil_vendedor.html')  # Renderiza la página del perfil vendedor


