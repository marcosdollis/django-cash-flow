"""
Script para gerar as chaves VAPID necessárias para Push Notifications
Execute: python generate_vapid_keys.py
"""
import base64
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

print("Gerando chaves VAPID para Push Notifications...\n")

# Gera chave privada ECDSA P-256
private_key = ec.generate_private_key(ec.SECP256R1())

# Extrai chave pública
public_key = private_key.public_key()

# Serializa chave privada em PEM
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Serializa chave pública em PEM
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Salva as chaves
with open("private_key.pem", "wb") as f:
    f.write(private_pem)

with open("public_key.pem", "wb") as f:
    f.write(public_pem)

# Converte para formato base64url (formato VAPID)
public_numbers = public_key.public_numbers()
x = public_numbers.x.to_bytes(32, byteorder='big')
y = public_numbers.y.to_bytes(32, byteorder='big')

# Chave pública VAPID (base64url encoded)
vapid_public_key = base64.urlsafe_b64encode(b'\x04' + x + y).decode('utf-8').rstrip('=')

# Chave privada VAPID (hex)
private_numbers = private_key.private_numbers()
vapid_private_key = hex(private_numbers.private_value)[2:]

print("✅ Chaves VAPID geradas com sucesso!")
print("\n📝 Adicione estas variáveis ao seu arquivo .env:")
print(f"VAPID_PRIVATE_KEY={vapid_private_key}")
print(f"VAPID_PUBLIC_KEY={vapid_public_key}")
print("\n📁 Arquivos salvos:")
print("- private_key.pem (chave privada)")
print("- public_key.pem (chave pública)")
print("\n⚠️  IMPORTANTE: Mantenha a chave privada segura e nunca a compartilhe!")

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
