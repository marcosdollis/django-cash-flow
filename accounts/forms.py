from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Company, CompanyMember

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Formulário customizado de criação de usuário"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Digite seu email'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nome'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Sobrenome'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Telefone (opcional)'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nome de usuário'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Formulário customizado de login"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email ou usuário'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })


class CompanyCreationForm(forms.ModelForm):
    """Formulário para criação de empresa"""
    class Meta:
        model = Company
        fields = ['name', 'cnpj', 'phone', 'email', 'address', 'primary_color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da empresa'
            }),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0000-00'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contato@empresa.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Endereço da empresa'
            }),
            'primary_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }


class UserProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do usuário"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }


class UserManagementForm(forms.ModelForm):
    """Formulário para criação e edição de usuários por administradores"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Digite o email'
    }))
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        }),
        required=False,
        help_text='Deixe em branco para manter a senha atual (apenas edição)'
    )
    password2 = forms.CharField(
        label='Confirmação de senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        }),
        required=False
    )
    role = forms.ChoiceField(
        choices=CompanyMember.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Função na empresa'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefone'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.is_editing = kwargs.pop('is_editing', False)
        super().__init__(*args, **kwargs)
        
        if self.is_editing:
            # Se estamos editando, a senha não é obrigatória
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        else:
            # Se estamos criando, a senha é obrigatória
            self.fields['password1'].required = True
            self.fields['password2'].required = True
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 or password2:  # Se alguma senha foi digitada
            if password1 != password2:
                raise forms.ValidationError('As senhas não coincidem.')
        
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        
        if password:  # Se uma nova senha foi fornecida
            user.set_password(password)
        
        if commit:
            user.save()
        return user


class CompanyMemberForm(forms.ModelForm):
    """Formulário para gerenciar membros da empresa"""
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Usuário'
    )
    
    class Meta:
        model = CompanyMember
        fields = ['user', 'role', 'is_active']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if self.company:
            # Excluir usuários que já são membros desta empresa
            existing_members = CompanyMember.objects.filter(
                company=self.company
            ).values_list('user_id', flat=True)
            
            self.fields['user'].queryset = User.objects.exclude(
                id__in=existing_members
            )


class ChangePasswordForm(forms.Form):
    """Formulário para alteração de senha"""
    old_password = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha atual'
        })
    )
    new_password1 = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nova senha'
        })
    )
    new_password2 = forms.CharField(
        label='Confirmação da nova senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Senha atual incorreta.')
        return old_password
    
    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('As novas senhas não coincidem.')
        
        return new_password2
    
    def save(self):
        new_password = self.cleaned_data['new_password1']
        self.user.set_password(new_password)
        self.user.save()
        return self.user