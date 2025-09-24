from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend de autenticação customizado que permite login com email ou username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica usuário por email ou username
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        try:
            # Tentar encontrar o usuário por email ou username
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
        except User.DoesNotExist:
            # Executar o hasher padrão para proteger contra ataques de tempo
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Se houver múltiplos usuários, tentar por email primeiro
            try:
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username__iexact=username)
                except User.DoesNotExist:
                    return None
        
        # Verificar a senha e se o usuário está ativo
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Recupera um usuário pelo ID
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        return user if self.user_can_authenticate(user) else None