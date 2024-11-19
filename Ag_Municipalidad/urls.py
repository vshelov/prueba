from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from AppSolicitudes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.inicio, name='inicio'),
    path('ingresar/', views.ingresar_solicitud, name='ingresar_solicitud'),
    path('panel_admin/', views.administrador_dashboard, name='administrador_dashboard'),
    path('dashboard_vendedor/', views.vendedor_dashboard, name='vendedor_dashboard'),
    path('panel_admin/crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('listar_solicitudes/', views.listar_solicitudes, name='listar_solicitudes'),
    path('editar_estado/<int:id>/', views.editar_estado_solicitud, name='editar_estado_solicitud'),
    path('eliminar_solicitud/<int:id>/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('detalles_solicitud/<int:id>/', views.detalles_solicitud, name='detalles_solicitud'),
    path('buscar_solicitud/', views.buscar_solicitud, name='buscar_solicitud'),
    path('crear_solicitud/', views.crear_solicitud, name='crear_solicitud'),
    path('panel_admin/listar_usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('perfil/', views.perfil, name='perfil'),
    path('cambiar_contraseña/', views.cambiar_contraseña, name='cambiar_contraseña'),
    path('listar_solicitudes_vendedor/', views.listar_solicitudes_vendedor, name='listar_solicitudes_vendedor'),
    path('perfil_vendedor/', views.perfil_vendedor, name='perfil_vendedor'),
    path('cambiar_contraseña_vendedor/', views.cambiar_contraseña_vendedor, name='cambiar_contraseña_vendedor'),
    
    
    
    
    
    
    
    
    


]
