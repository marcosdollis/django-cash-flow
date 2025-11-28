"""
Script para gerar as chaves VAPID necessárias para Push Notifications
Execute: python generate_vapid_keys.py
"""
from vapid import Vapid

print("Gerando chaves VAPID para Push Notifications...\n")

# Gera as chaves
vapid = Vapid()
vapid.generate_keys()

# Salva as chaves em arquivo
vapid.save_key("private_key.pem")
vapid.save_public_key("public_key.pem")

# Exibe as chaves
private_key = vapid.private_key.to_string().hex()
public_key = vapid.public_key.to_string()

print("=" * 70)
print("CHAVES VAPID GERADAS COM SUCESSO!")
print("=" * 70)
print("\n1. Adicione estas variáveis ao seu arquivo .env:")
print("-" * 70)
print(f"VAPID_PRIVATE_KEY={private_key}")
print(f"VAPID_PUBLIC_KEY={public_key}")
print(f"VAPID_ADMIN_EMAIL=admin@seudominio.com")
print("-" * 70)

print("\n2. No Railway, adicione as mesmas variáveis de ambiente")
print("\n3. As chaves também foram salvas em:")
print("   - private_key.pem")
print("   - public_key.pem")

print("\n⚠️  IMPORTANTE:")
print("   - NÃO commite as chaves privadas no git!")
print("   - Adicione *.pem ao .gitignore")
print("   - Use as mesmas chaves em todos os ambientes (dev, prod)")
print("\n" + "=" * 70)
