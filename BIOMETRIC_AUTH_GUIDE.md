# 🔐 Autenticação Biométrica (WebAuthn) - Guia Completo

## 📱 Visão Geral

O CashFlow Manager agora suporta **autenticação biométrica** usando a tecnologia WebAuthn, permitindo login seguro com:

- 🖐️ **Impressão Digital** (Touch ID / Fingerprint)
- 👤 **Reconhecimento Facial** (Face ID)
- 🔐 **Chaves de Segurança** (YubiKey, etc.)
- 📱 **Autenticadores Móveis**

## 🛠️ Implementação Técnica

### Backend (Django + WebAuthn)

#### 1. **Modelo de Dados**
```python
class WebAuthnCredential(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credential_id = models.CharField(max_length=255, unique=True)
    public_key = models.TextField()
    sign_count = models.PositiveIntegerField(default=0)
    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50)
    transports = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
```

#### 2. **APIs REST**
- `POST /api/webauthn/register/options/` - Opções de registro
- `POST /api/webauthn/register/verify/` - Verificar registro
- `POST /api/webauthn/authenticate/options/` - Opções de autenticação
- `POST /api/webauthn/authenticate/verify/` - Verificar autenticação
- `DELETE /api/webauthn/remove/` - Remover credencial

#### 3. **Biblioteca**
- **webauthn** (2.7.0) - Implementação Python do WebAuthn

### Frontend (JavaScript + WebAuthn API)

#### 1. **Classe BiometricAuth**
```javascript
class BiometricAuth {
    async register() { /* Registrar biometria */ }
    async authenticate() { /* Autenticar */ }
    async remove() { /* Remover */ }
}
```

#### 2. **Integração com Templates**
- **Página de Login**: Botão "Entrar com Biometria"
- **Configurações**: Seção completa de gerenciamento biométrico

## 🚀 Como Usar

### Para Usuários Finais

#### **1. Registrar Biometria**
1. Acesse **Configurações** → **Autenticação Biométrica**
2. Clique em **"Registrar Biometria"**
3. Seu dispositivo pedirá autorização biométrica
4. **Aprove** com impressão digital, rosto ou PIN

#### **2. Login Biométrico**
1. Na página de login, aparecerá o botão **"Entrar com Biometria"**
2. Clique no botão
3. Use sua biometria para fazer login instantâneo

#### **3. Gerenciar Credenciais**
- **Testar**: Verificar se a biometria funciona
- **Remover**: Desativar autenticação biométrica

### Para Desenvolvedores

#### **Registro de Credencial**
```javascript
// 1. Obter opções do servidor
const options = await fetch('/api/webauthn/register/options/')
    .then(r => r.json());

// 2. Criar credencial
const credential = await navigator.credentials.create({
    publicKey: options
});

// 3. Enviar para verificação
await fetch('/api/webauthn/register/verify/', {
    method: 'POST',
    body: JSON.stringify(credential.toJSON())
});
```

#### **Autenticação**
```javascript
// 1. Obter opções
const options = await fetch('/api/webauthn/authenticate/options/')
    .then(r => r.json());

// 2. Obter credencial
const credential = await navigator.credentials.get({
    publicKey: options
});

// 3. Verificar no servidor
await fetch('/api/webauthn/authenticate/verify/', {
    method: 'POST',
    body: JSON.stringify(credential.toJSON())
});
```

## 🔒 Segurança

### **Vantagens da WebAuthn**
- ✅ **Sem Senhas**: Elimina roubo de credenciais
- ✅ **Prova de Presença**: Requer interação física do usuário
- ✅ **Resistente a Phishing**: Vinculado ao domínio
- ✅ **Criptografia Forte**: ECDSA P-256 com COSE
- ✅ **Isolado**: Chaves nunca saem do dispositivo

### **Compatibilidade**
- 🌐 **Navegadores**: Chrome 67+, Firefox 60+, Safari 14+, Edge 18+
- 📱 **iOS**: 14.5+ (Safari)
- 🤖 **Android**: 7.0+ (Chrome)
- 🪟 **Windows**: Hello / YubiKey
- 🍎 **macOS**: Touch ID / Face ID

### **Limitações**
- ⚠️ **HTTPS Obrigatório** em produção
- ⚠️ **Um dispositivo por usuário** (atualmente)
- ⚠️ **Não funciona** em navegadores muito antigos

## 🧪 Testes e Diagnóstico

### **Script de Diagnóstico**
```bash
python diagnose_biometric.py
```

### **Verificações Manuais**
1. **Console do navegador** (F12) para erros JavaScript
2. **Logs do Django** para erros do servidor
3. **Admin Django** (`/admin/core/webauthncredential/`) para ver credenciais

### **Cenários de Teste**
- ✅ Registrar biometria
- ✅ Login biométrico
- ✅ Remover credencial
- ✅ Tentativa de registro duplicado
- ✅ Autenticação com credencial inválida

## 📋 Checklist de Deploy

### **Desenvolvimento**
- [x] Modelo WebAuthnCredential criado
- [x] APIs REST implementadas
- [x] JavaScript client-side implementado
- [x] Templates atualizados
- [x] Migrações aplicadas
- [x] Testes básicos realizados

### **Produção**
- [ ] **HTTPS obrigatório** (WebAuthn não funciona em HTTP)
- [ ] Configurar `VAPID_ADMIN_EMAIL` correto
- [ ] Testar em diferentes dispositivos
- [ ] Verificar compatibilidade de navegadores
- [ ] Monitorar logs de erro

## 🔧 Solução de Problemas

### **"WebAuthn não suportado"**
- Atualize o navegador para versão mais recente
- Use HTTPS (não HTTP localhost)

### **"Credencial já registrada"**
- Cada usuário pode ter apenas uma credencial
- Remova a existente antes de registrar nova

### **"Erro de autenticação"**
- Verifique se a credencial não foi removida
- Tente registrar novamente
- Verifique logs do servidor

### **iOS não funciona**
- Use Safari (não Chrome no iOS)
- iOS 14.5+ necessário
- Certifique-se de que é um PWA instalado

## 📚 Referências

- [WebAuthn Specification](https://www.w3.org/TR/webauthn/)
- [WebAuthn Guide](https://webauthn.guide/)
- [FIDO Alliance](https://fidoalliance.org/)
- [Can I Use WebAuthn?](https://caniuse.com/webauthn)

---

## 🎯 Conclusão

A autenticação biométrica WebAuthn adiciona uma camada extra de segurança e conveniência ao CashFlow Manager, permitindo login sem senha em dispositivos compatíveis. A implementação é completa, segura e pronta para produção com as devidas configurações de HTTPS.