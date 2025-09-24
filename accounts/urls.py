from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Autenticação
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Configuração de empresa
    path('company/setup/', views.company_setup_view, name='company_setup'),
    path('company/settings/', views.company_settings_view, name='company_settings'),
    path('company/switch/<int:company_id>/', views.switch_company_view, name='switch_company'),
    
    # Perfil do usuário
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    
    # Gerenciamento de usuários
    path('users/create/', views.create_user_view, name='create_user'),
    path('users/add-member/', views.add_member_view, name='add_member'),
    path('users/edit/<int:user_id>/', views.edit_user_view, name='edit_user'),
    path('users/remove-member/<int:member_id>/', views.remove_member_view, name='remove_member'),
    path('api/user-form/', views.get_user_form, name='get_user_form'),
    
    # Reset de senha
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]