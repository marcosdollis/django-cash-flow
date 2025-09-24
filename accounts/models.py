from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    """Modelo customizado de usuário"""
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.username
    
    def get_company_role(self, company):
        """Retorna o papel do usuário na empresa especificada"""
        try:
            member = self.companymember_set.get(company=company, is_active=True)
            return member.role
        except CompanyMember.DoesNotExist:
            return None
    
    def is_company_admin(self, company):
        """Verifica se o usuário é admin ou owner da empresa"""
        role = self.get_company_role(company)
        return role in ['owner', 'admin']
    
    def can_manage_users(self, company):
        """Verifica se o usuário pode gerenciar outros usuários"""
        role = self.get_company_role(company)
        return role in ['owner', 'admin']
    
    def can_create_users(self, company):
        """Verifica se o usuário pode criar novos usuários"""
        role = self.get_company_role(company)
        return role in ['owner', 'admin']


class Company(models.Model):
    """Modelo para empresas/organizações"""
    name = models.CharField('Nome da Empresa', max_length=200)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.TextField('Endereço', blank=True)
    
    # Configurações da empresa
    logo = models.ImageField('Logo', upload_to='logos/', blank=True, null=True)
    primary_color = models.CharField('Cor Primária', max_length=7, default='#007bff')
    
    # Relacionamentos
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_companies', verbose_name='Proprietário')
    members = models.ManyToManyField(User, through='CompanyMember', related_name='companies', verbose_name='Membros')
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CompanyMember(models.Model):
    """Modelo para relacionamento entre usuários e empresas"""
    ROLE_CHOICES = [
        ('owner', 'Proprietário'),
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('user', 'Usuário'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    role = models.CharField('Função', max_length=20, choices=ROLE_CHOICES, default='user')
    joined_at = models.DateTimeField('Ingressou em', auto_now_add=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Membro da Empresa'
        verbose_name_plural = 'Membros da Empresa'
        unique_together = ['user', 'company']
    
    def __str__(self):
        return f"{self.user} - {self.company} ({self.get_role_display()})"
