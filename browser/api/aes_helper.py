import os, uuid, base64, json, sys, hashlib, secrets

#https://medium.com/@sachadehe/encrypt-decrypt-data-between-python-3-and-javascript-true-aes-algorithm-7c4e2fa3a9ff
#https://encryption-decryption.mojoauth.com/aes-256-encryption--javascript-in-browser/

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def chave_randomica(tamanho):
    """Gera uma chave aleatória criptograficamente segura.
    
    Args:
        tamanho: Tamanho da chave em bytes (deve ser 16, 24 ou 32 para AES)
    
    Returns:
        String aleatória segura do tamanho especificado
    
    Raises:
        ValueError: Se o tamanho não for válido para AES
    """
    if tamanho not in [16, 24, 32]:
        raise ValueError(f"Tamanho de chave inválido: {tamanho}. Deve ser 16, 24 ou 32 bytes.")
    
    # Usa secrets.token_bytes para geração criptograficamente segura
    return secrets.token_bytes(tamanho).hex()[:tamanho]

def encrypt_aes_cbc_no_iv(key, raw):
    """Encripta dados usando AES-CBC com IV gerado automaticamente.
    
    Args:
        key: Chave de criptografia (16, 24 ou 32 bytes)
        raw: Dados a serem criptografados
    
    Returns:
        IV concatenado com dados criptografados em base64
    
    Raises:
        ValueError: Se a chave tiver tamanho inválido
    """
    if len(key) not in [16, 24, 32]:
        raise ValueError(f"Tamanho de chave inválido: {len(key)}. Deve ser 16, 24 ou 32 bytes.")
    
    # Gera IV criptograficamente seguro
    iv = secrets.token_bytes(16)
    iv_str = iv.hex()[:16]
    return iv_str + encrypt_aes_cbc(key, iv_str, raw)
def encrypt_aes_cbc(key, iv, raw):
    """Encripta dados usando AES-CBC.
    
    Args:
        key: Chave de criptografia
        iv: Vetor de inicialização (16 bytes)
        raw: Dados a serem criptografados
    
    Returns:
        Dados criptografados em base64
    
    Raises:
        ValueError: Se os parâmetros forem inválidos
        TypeError: Se os tipos de dados forem incorretos
    """
    try:
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(iv, str):
            iv = iv.encode('utf-8')
        
        if len(key) not in [16, 24, 32]:
            raise ValueError(f"Tamanho de chave inválido: {len(key)}")
        if len(iv) != 16:
            raise ValueError(f"IV deve ter 16 bytes, recebido: {len(iv)}")
        
        if isinstance(raw, str):
            raw = raw.encode('utf-8')
        
        raw_padded = pad(raw, 16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(raw_padded)
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Erro na criptografia: {str(e)}")
def decrypt_aes_cbc_no_iv(key, enc):
    iv = enc[:16];
    enc = enc[16:];
    return decrypt_aes_cbc(key, iv, enc);

def decrypt_aes_cbc(key, iv, enc):
    """Decripta dados usando AES-CBC.
    
    Args:
        key: Chave de criptografia
        iv: Vetor de inicialização (16 bytes)
        enc: Dados criptografados em base64
    
    Returns:
        Dados decriptografados
    
    Raises:
        ValueError: Se os parâmetros forem inválidos ou decriptografia falhar
    """
    try:
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(iv, str):
            iv = iv.encode('utf-8')
        
        if len(key) not in [16, 24, 32]:
            raise ValueError(f"Tamanho de chave inválido: {len(key)}")
        if len(iv) != 16:
            raise ValueError(f"IV deve ter 16 bytes, recebido: {len(iv)}")
        
        enc_bytes = base64.b64decode(enc)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(enc_bytes)
        raw = unpad(decrypted, 16).decode('utf-8')
        return raw
    except Exception as e:
        raise ValueError(f"Erro na decriptografia: {str(e)}")

def encrypt_aes_ecb(key, raw):
    """AVISO: ECB não é recomendado para uso em produção.
    Use encrypt_aes_cbc para segurança adequada.
    
    Args:
        key: Chave de criptografia
        raw: Dados a serem criptografados
    
    Returns:
        Dados criptografados em base64
    """
    try:
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        if len(key) not in [16, 24, 32]:
            raise ValueError(f"Tamanho de chave inválido: {len(key)}")
        
        raw_bytes = str(raw).encode('utf-8')
        raw_padded = pad(raw_bytes, 16)
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted = cipher.encrypt(raw_padded)
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Erro na criptografia ECB: {str(e)}")

def decrypt_aes_ecb(key, enc):
    """AVISO: ECB não é recomendado para uso em produção.
    Use decrypt_aes_cbc para segurança adequada.
    
    Args:
        key: Chave de criptografia
        enc: Dados criptografados em base64
    
    Returns:
        Dados decriptografados
    """
    try:
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        if len(key) not in [16, 24, 32]:
            raise ValueError(f"Tamanho de chave inválido: {len(key)}")
        
        enc_bytes = base64.b64decode(enc)
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(enc_bytes)
        raw = unpad(decrypted, 16).decode('utf-8')
        return raw
    except Exception as e:
        raise ValueError(f"Erro na decriptografia ECB: {str(e)}")
