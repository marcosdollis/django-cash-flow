from .models import Company, CompanyMember


def company_context(request):
    """Context processor para dados da empresa"""
    context = {}
    
    if request.user.is_authenticated:
        # Empresa atual da sessão ou primeira empresa do usuário
        current_company_id = request.session.get('current_company_id')
        current_company = None
        user_role = None
        
        try:
            # Obter empresas do usuário
            user_companies = CompanyMember.objects.filter(
                user=request.user, 
                is_active=True
            ).select_related('company')
            
            if current_company_id:
                try:
                    current_company = Company.objects.get(id=current_company_id)
                    # Verificar se o usuário é membro desta empresa
                    if not user_companies.filter(company=current_company).exists():
                        current_company = user_companies.first().company if user_companies else None
                except Company.DoesNotExist:
                    current_company = user_companies.first().company if user_companies else None
            else:
                current_company = user_companies.first().company if user_companies else None
            
            # Obter papel do usuário na empresa atual
            if current_company:
                user_role = request.user.get_company_role(current_company)
                # Salvar empresa atual na sessão
                request.session['current_company_id'] = current_company.id
            
        except Exception:
            # Em caso de erro, obter empresas do usuário de forma mais simples
            user_companies = request.user.companies.filter(
                companymember__is_active=True
            )
            current_company = user_companies.first()
            if current_company:
                user_role = request.user.get_company_role(current_company)
        
        context.update({
            'current_company': current_company,
            'user_companies': user_companies,
            'user_role': user_role,
            'can_manage_users': request.user.can_manage_users(current_company) if current_company else False,
            'is_company_admin': request.user.is_company_admin(current_company) if current_company else False,
        })
    
    return context