from django.urls import path
from . import views
from .views import buscar_itens
from .views import atualizar_status_localizacao
urlpatterns = [
        path('', views.homepage, name="homepage"),         # Inclui as urls do app blog
        path('login', views.login, name="login"),           # Inclui as urls do app blog
        path('cadastroUsuario', views.cadastroUsuario, name='cadastroUsuario'),
        path('profile', views.profile, name="profile"),       # Inclui as urls do app blog
        path('faq', views.faq, name="faq"),                 # Inclui as urls do app blog
        path('welcomeHomepage', views.welcomeHomepage, name="welcomeHomepage"),   # Inclui as urls do app blog
        path('itens', views.itens, name="itens"),           # Inclui as urls do app blog
        path('adicionar_inventario', views.adicionar_inventario, name="adicionar_inventario"),   # Inclui as urls do app blog
        path('buscar', buscar_itens, name='buscar_itens'),
        path('excluir_inventario/', views.excluir_inventario, name='excluir_inventario'),
        path('update-item/', views.update_item, name='update_item'),
        path('excluir-item/', views.excluir_inventario, name='excluir_inventario'),
        path('update-sala/', views.update_sala, name='update_sala'),
        path('excluir-sala/', views.excluir_sala, name='excluir_sala'),
        path('adicionar-salas/', views.adicionar_salas, name='adicionar_salas'),
        path('buscar-itens-sala', views.buscar_itens_sala, name='buscar_itens_sala'),
        path('salas', views.salas, name='salas'),
        path('buscar-salas', views.buscar_salas, name='buscar_salas'),
        path('logout/', views.logout, name='logout'),
        path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
        path('editar_usuario/', views.editar_usuario, name='editar_usuario'),
        path('excluir_usuario/', views.excluir_usuario, name='excluir_usuario'),

#URLS da api mobile
        #URLS da api mobile
        path('api/login/', views.api_login, name='api_login'),
        path('api/salas/', views.get_salas, name='api_get_salas'),
        path('api/inventarios/', views.get_inventarios, name='api_get_inventarios'),
        path('api/add_inventario/', views.add_inventario, name='api_add_inventario'),
        path('api/delete_inventario/', views.delete_inventario, name='api_delete_inventario'),
        path('api/editar_inventario/', views.editar_inventario, name='api_editar_inventario'),
        path('api/add_sala/', views.add_sala, name='api_add_sala'),
        path('api/inventarios-por-sala/', views.get_inventarios_por_sala, name='api_inventarios-por-sala'),
        path('api/delete_sala', views.delete_sala, name='api_delete_sala'),
        path('api/editar_sala', views.editar_sala, name='api_editar_sala'),
        path('api/cadastro/', views.register_user, name="api_cadastro_user"),
        path('api/user_dados', views.user_data, name='api_user_dados'),
        path('api/update_user_data', views.update_user_data, name='update_user_data'),
        path('api/get_user_room/', views.get_user_room, name='api_get_user_room'),
        path('api/atualizar-status/', atualizar_status_localizacao, name='atualizar_status_localizacao'),
]