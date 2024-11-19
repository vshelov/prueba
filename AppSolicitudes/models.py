from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

ESTADO_SOLICITUD = [
    ('pendiente', 'Pendiente'),
    ('aceptada', 'Aceptada'),
    ('rechazada', 'Rechazada'),
    ('expirada', 'Expirada'),
]

class Solicitud(models.Model):
    rut = models.CharField(max_length=12)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    comuna = models.CharField(max_length=50)
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_SOLICITUD,
        default='pendiente'
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Solicitud {self.id}: {self.nombre} {self.apellidos} - Estado: {self.estado}"


@receiver(post_migrate)
def create_default_groups_and_permissions(sender, **kwargs):
    """
    Crea roles predeterminados (grupos) y asigna permisos al modelo Solicitud.
    """
    # Crear roles (grupos)
    roles = ['Administrador', 'Vendedor']
    for role in roles:
        group, created = Group.objects.get_or_create(name=role)
        if created:
            print(f'Rol "{role}" creado.')
        else:
            print(f'Rol "{role}" ya existe.')

    # Obtener el ContentType para el modelo Solicitud
    solicitud_content_type = ContentType.objects.get_for_model(Solicitud)

    # Permisos para el grupo Administrador
    admin_permissions = [
        ('list_solicitud', 'Puede listar solicitudes'),
        ('view_solicitud', 'Puede ver detalles de una solicitud'),
        ('change_solicitud', 'Puede cambiar el estado de una solicitud'),
        ('delete_solicitud', 'Puede eliminar solicitudes')
    ]

    admin_group, _ = Group.objects.get_or_create(name='Administrador')
    for codename, name in admin_permissions:
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=solicitud_content_type
        )
        admin_group.permissions.add(permission)
        print(f'Permiso "{name}" asignado al grupo "Administrador".')

    # Permisos para el grupo Vendedor
    vendedor_permissions = [
        ('view_solicitud', 'Puede ver detalles de una solicitud'),
        ('change_solicitud', 'Puede cambiar el estado de una solicitud'),
    ]

    vendedor_group, _ = Group.objects.get_or_create(name='Vendedor')
    for codename, name in vendedor_permissions:
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=solicitud_content_type
        )
        vendedor_group.permissions.add(permission)
        print(f'Permiso "{name}" asignado al grupo "Vendedor".')


@receiver(post_migrate)
def create_default_admin_user(sender, **kwargs):
    """
    Crea un superusuario predeterminado y lo asigna al grupo Administrador.
    """
    admin_email = "admin@gmail.com"
    admin_password = "123456"

    if not User.objects.filter(email=admin_email).exists():
        admin_user = User.objects.create_superuser(
            username="admin",
            email=admin_email,
            password=admin_password,
            first_name="Administrador",
            last_name="Principal"
        )
        admin_group = Group.objects.get(name="Administrador")
        admin_user.groups.add(admin_group)
        print(f'Superusuario predeterminado creado: {admin_email} con contraseña: {admin_password}')
    else:
        print(f'Superusuario predeterminado ya existe: {admin_email}')

