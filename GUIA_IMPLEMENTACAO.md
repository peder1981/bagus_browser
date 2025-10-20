# Guia de Implementação - Melhorias de Segurança
## Bagus Browser

Este documento fornece um guia prático para desenvolvedores que desejam entender e manter as melhorias de segurança implementadas.

---

## Índice

1. [Validação de Entrada](#1-validação-de-entrada)
2. [Criptografia Segura](#2-criptografia-segura)
3. [Gestão de Arquivos](#3-gestão-de-arquivos)
4. [Tratamento de Exceções](#4-tratamento-de-exceções)
5. [Configurações Seguras](#5-configurações-seguras)
6. [Limites de Recursos](#6-limites-de-recursos)
7. [Logging Seguro](#7-logging-seguro)
8. [Testes de Segurança](#8-testes-de-segurança)

---

## 1. Validação de Entrada

### 1.1 Validação de Username

**Implementação**:
```python
import re

def validar_username(username):
    """Valida o username para prevenir path traversal e injeção.
    
    Args:
        username: Nome de usuário a ser validado
    
    Returns:
        bool: True se válido, False caso contrário
    """
    # Verifica se não está vazio e tem comprimento adequado
    if not username or len(username) < 3 or len(username) > 32:
        return False
    
    # Permite apenas letras, números, underscore e hífen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False
    
    # Previne path traversal
    if '..' in username or '/' in username or '\\' in username:
        return False
    
    return True
```

**Uso**:
```python
username = input("Digite o username: ")
if not validar_username(username):
    print("Username inválido!")
    return
```

**Testes**:
```python
# Válidos
assert validar_username("user123") == True
assert validar_username("my-user_01") == True

# Inválidos
assert validar_username("../etc") == False
assert validar_username("user@domain") == False
assert validar_username("ab") == False  # Muito curto
assert validar_username("a" * 33) == False  # Muito longo
```

---

### 1.2 Validação de URLs

**Implementação**:
```python
from urllib.parse import urlparse

def validar_url(url):
    """Valida URL para segurança.
    
    Args:
        url: URL a ser validada
    
    Returns:
        tuple: (bool, str) - (válido, mensagem de erro)
    """
    # Verifica se não está vazia
    if not url or not url.strip():
        return False, "URL vazia"
    
    # Verifica tamanho
    if len(url) > 2048:
        return False, "URL muito longa (max 2048 caracteres)"
    
    # Adiciona protocolo se necessário
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        parsed = urlparse(url)
        
        # Valida protocolo
        if parsed.scheme not in ['http', 'https']:
            return False, f"Protocolo não permitido: {parsed.scheme}"
        
        # Previne URLs com credenciais
        if parsed.username or parsed.password:
            return False, "URLs com credenciais não são permitidas"
        
        return True, url
        
    except Exception as e:
        return False, f"URL inválida: {str(e)}"
```

**Uso**:
```python
url = input("Digite a URL: ")
valido, resultado = validar_url(url)
if not valido:
    print(f"Erro: {resultado}")
else:
    url_final = resultado
    # Usar url_final
```

---

### 1.3 Validação de Paths

**Implementação**:
```python
import os

def validar_path_usuario(path, base_dir="/tmp"):
    """Valida que o path está dentro do diretório base.
    
    Args:
        path: Path a ser validado
        base_dir: Diretório base permitido
    
    Returns:
        tuple: (bool, str) - (válido, path_real ou mensagem de erro)
    """
    try:
        # Resolve symlinks e paths relativos
        path_real = os.path.realpath(path)
        base_real = os.path.realpath(base_dir)
        
        # Verifica se está dentro do base_dir
        if not path_real.startswith(base_real + os.sep):
            return False, f"Path fora do escopo: {path_real}"
        
        return True, path_real
        
    except Exception as e:
        return False, f"Erro ao validar path: {str(e)}"
```

**Uso**:
```python
user_path = os.path.join("/tmp", username)
valido, resultado = validar_path_usuario(user_path)
if not valido:
    print(f"Erro: {resultado}")
else:
    path_seguro = resultado
    # Usar path_seguro
```

---

## 2. Criptografia Segura

### 2.1 Geração de Chaves

**❌ NUNCA FAÇA ISSO**:
```python
import random

# INSEGURO - Não use random para criptografia
key = ''.join(random.choice(chars) for _ in range(32))
```

**✅ FAÇA ASSIM**:
```python
import secrets

def gerar_chave_segura(tamanho=32):
    """Gera uma chave criptograficamente segura.
    
    Args:
        tamanho: Tamanho da chave em bytes (16, 24 ou 32)
    
    Returns:
        bytes: Chave segura
    
    Raises:
        ValueError: Se tamanho for inválido
    """
    if tamanho not in [16, 24, 32]:
        raise ValueError(f"Tamanho deve ser 16, 24 ou 32, recebido: {tamanho}")
    
    return secrets.token_bytes(tamanho)
```

---

### 2.2 Criptografia AES-CBC

**Implementação Segura**:
```python
import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

def criptografar_dados(chave, dados):
    """Criptografa dados usando AES-CBC.
    
    Args:
        chave: Chave de criptografia (16, 24 ou 32 bytes)
        dados: Dados a serem criptografados (string)
    
    Returns:
        str: IV + dados criptografados em base64
    """
    # Valida chave
    if len(chave) not in [16, 24, 32]:
        raise ValueError(f"Tamanho de chave inválido: {len(chave)}")
    
    # Gera IV seguro
    iv = secrets.token_bytes(16)
    
    # Converte dados para bytes
    dados_bytes = dados.encode('utf-8')
    
    # Aplica padding
    dados_padded = pad(dados_bytes, 16)
    
    # Criptografa
    cipher = AES.new(chave, AES.MODE_CBC, iv)
    dados_criptografados = cipher.encrypt(dados_padded)
    
    # Retorna IV + dados em base64
    return base64.b64encode(iv + dados_criptografados).decode('utf-8')

def decriptografar_dados(chave, dados_criptografados):
    """Decriptografa dados usando AES-CBC.
    
    Args:
        chave: Chave de criptografia (16, 24 ou 32 bytes)
        dados_criptografados: Dados em base64
    
    Returns:
        str: Dados decriptografados
    """
    # Valida chave
    if len(chave) not in [16, 24, 32]:
        raise ValueError(f"Tamanho de chave inválido: {len(chave)}")
    
    # Decodifica base64
    dados_bytes = base64.b64decode(dados_criptografados)
    
    # Extrai IV (primeiros 16 bytes)
    iv = dados_bytes[:16]
    dados_cript = dados_bytes[16:]
    
    # Decriptografa
    cipher = AES.new(chave, AES.MODE_CBC, iv)
    dados_padded = cipher.decrypt(dados_cript)
    
    # Remove padding
    dados_bytes = unpad(dados_padded, 16)
    
    return dados_bytes.decode('utf-8')
```

---

## 3. Gestão de Arquivos

### 3.1 Leitura de Arquivos

**❌ NUNCA FAÇA ISSO**:
```python
# INSEGURO - Arquivo pode não ser fechado
f = open(path, 'r')
data = f.read()
# Se houver exceção, arquivo não é fechado
```

**✅ FAÇA ASSIM**:
```python
def ler_arquivo_seguro(path, max_size=10*1024*1024):
    """Lê arquivo com validação de segurança.
    
    Args:
        path: Caminho do arquivo
        max_size: Tamanho máximo em bytes
    
    Returns:
        str: Conteúdo do arquivo
    
    Raises:
        ValueError: Se arquivo for muito grande
        FileNotFoundError: Se arquivo não existir
    """
    # Valida que arquivo existe
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    
    # Valida tamanho
    if os.path.getsize(path) > max_size:
        raise ValueError(f"Arquivo muito grande: {os.path.getsize(path)} bytes")
    
    # Lê com context manager
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

---

### 3.2 Escrita de Arquivos

**✅ IMPLEMENTAÇÃO SEGURA**:
```python
def escrever_arquivo_seguro(path, conteudo, criar_dirs=True):
    """Escreve arquivo com validação de segurança.
    
    Args:
        path: Caminho do arquivo
        conteudo: Conteúdo a escrever
        criar_dirs: Se deve criar diretórios
    
    Raises:
        ValueError: Se path for inválido
    """
    # Valida path
    valido, path_real = validar_path_usuario(path)
    if not valido:
        raise ValueError(path_real)
    
    # Cria diretórios se necessário
    if criar_dirs:
        dir_path = os.path.dirname(path_real)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o700)
    
    # Escreve com context manager
    with open(path_real, 'w', encoding='utf-8') as f:
        f.write(conteudo)
```

---

### 3.3 Criação de Diretórios

**✅ IMPLEMENTAÇÃO SEGURA**:
```python
def criar_diretorio_seguro(path, base_dir="/tmp"):
    """Cria diretório com permissões restritas.
    
    Args:
        path: Caminho do diretório
        base_dir: Diretório base permitido
    
    Raises:
        ValueError: Se path for inválido
    """
    # Valida path
    valido, path_real = validar_path_usuario(path, base_dir)
    if not valido:
        raise ValueError(path_real)
    
    # Cria com permissões restritas (apenas owner)
    if not os.path.exists(path_real):
        os.makedirs(path_real, mode=0o700)
```

---

## 4. Tratamento de Exceções

### 4.1 Padrão Recomendado

**❌ NUNCA FAÇA ISSO**:
```python
try:
    # código
except:
    pass  # Silencia todos os erros
```

**✅ FAÇA ASSIM**:
```python
def funcao_robusta(parametro):
    """Função com tratamento robusto de exceções.
    
    Args:
        parametro: Parâmetro da função
    
    Returns:
        resultado: Resultado do processamento
    
    Raises:
        ValueError: Se parametro for inválido
        FileNotFoundError: Se arquivo não existir
        RuntimeError: Para outros erros
    """
    try:
        # Validação de entrada
        if not parametro:
            raise ValueError("Parâmetro não pode ser vazio")
        
        # Lógica principal
        resultado = processar(parametro)
        return resultado
        
    except ValueError as e:
        # Erro de validação - propaga
        print(f"Erro de validação: {e}")
        raise
        
    except FileNotFoundError as e:
        # Arquivo não encontrado - propaga
        print(f"Arquivo não encontrado: {e}")
        raise
        
    except Exception as e:
        # Erro inesperado - loga e propaga
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Falha ao processar: {e}")
```

---

### 4.2 Tratamento em Loops

**✅ IMPLEMENTAÇÃO SEGURA**:
```python
def processar_lista(itens):
    """Processa lista com tratamento de erros por item.
    
    Args:
        itens: Lista de itens a processar
    
    Returns:
        tuple: (sucessos, falhas)
    """
    sucessos = []
    falhas = []
    
    for item in itens:
        try:
            resultado = processar_item(item)
            sucessos.append(resultado)
        except Exception as e:
            print(f"Erro ao processar {item}: {e}")
            falhas.append((item, str(e)))
    
    return sucessos, falhas
```

---

## 5. Configurações Seguras

### 5.1 Configuração Padrão

**Template Seguro** (`template_secure.json`):
```json
{
  "default": {
    "url": "https://duckduckgo.com/"
  },
  "settings": {
    "JavascriptCanAccessClipboard": false,
    "JavascriptCanOpenWindows": false,
    "LocalContentCanAccessRemoteUrls": false,
    "LocalContentCanAccessFileUrls": false,
    "AllowRunningInsecureContent": false,
    "AllowGeolocationOnInsecureOrigins": false,
    "ScreenCaptureEnabled": false,
    "ReadingFromCanvasEnabled": false,
    "XSSAuditingEnabled": true,
    "WebRTCPublicInterfacesOnly": true
  }
}
```

---

### 5.2 Carregamento de Configuração

**✅ IMPLEMENTAÇÃO SEGURA**:
```python
import json

def carregar_configuracao(path):
    """Carrega configuração com validação.
    
    Args:
        path: Caminho do arquivo de configuração
    
    Returns:
        dict: Configuração carregada
    
    Raises:
        FileNotFoundError: Se arquivo não existir
        ValueError: Se JSON for inválido
    """
    try:
        with open(path, 'r') as f:
            config = json.load(f)
        
        # Valida estrutura básica
        if not isinstance(config, dict):
            raise ValueError("Configuração deve ser um objeto JSON")
        
        if "settings" not in config:
            raise ValueError("Configuração deve ter 'settings'")
        
        return config
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido: {e}")
```

---

## 6. Limites de Recursos

### 6.1 Limites Recomendados

```python
# Constantes de limite
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_SCRIPT_SIZE = 1 * 1024 * 1024  # 1MB
MAX_JS_SIZE = 100 * 1024  # 100KB
MAX_URL_LENGTH = 2048
MAX_HISTORY_ENTRIES = 10000
MAX_TABS_RESTORED = 20
MAX_SUGGESTIONS = 50
```

---

### 6.2 Aplicação de Limites

**Tamanho de Arquivo**:
```python
def validar_tamanho_arquivo(path, max_size=MAX_FILE_SIZE):
    """Valida tamanho de arquivo.
    
    Args:
        path: Caminho do arquivo
        max_size: Tamanho máximo em bytes
    
    Returns:
        bool: True se válido
    
    Raises:
        ValueError: Se arquivo for muito grande
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    
    tamanho = os.path.getsize(path)
    if tamanho > max_size:
        raise ValueError(f"Arquivo muito grande: {tamanho} bytes (max: {max_size})")
    
    return True
```

**Tamanho de Lista**:
```python
def limitar_lista(lista, max_items=MAX_HISTORY_ENTRIES):
    """Limita tamanho de lista mantendo itens mais recentes.
    
    Args:
        lista: Lista a limitar
        max_items: Número máximo de itens
    
    Returns:
        list: Lista limitada
    """
    if len(lista) > max_items:
        return lista[-max_items:]
    return lista
```

---

## 7. Logging Seguro

### 7.1 Configuração de Logger

**✅ IMPLEMENTAÇÃO SEGURA**:
```python
import logging

def configurar_logger(nome, arquivo, nivel=logging.INFO):
    """Configura logger com formato seguro.
    
    Args:
        nome: Nome do logger
        arquivo: Caminho do arquivo de log
        nivel: Nível de logging
    
    Returns:
        Logger: Logger configurado
    """
    # Cria logger
    logger = logging.getLogger(nome)
    logger.setLevel(nivel)
    
    # Cria handler
    handler = logging.FileHandler(arquivo)
    handler.setLevel(nivel)
    
    # Formato seguro (sem dados sensíveis)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Adiciona handler
    logger.addHandler(handler)
    
    return logger
```

---

### 7.2 Uso Seguro

**❌ NUNCA LOGUE DADOS SENSÍVEIS**:
```python
# INSEGURO - Não logue senhas, tokens, etc.
logger.info(f"Login com senha: {senha}")
logger.info(f"Token: {token}")
```

**✅ FAÇA ASSIM**:
```python
# SEGURO - Logue apenas informações necessárias
logger.info(f"Login bem-sucedido para usuário: {username}")
logger.info(f"Token gerado (hash: {hash(token)[:8]}...)")
```

---

## 8. Testes de Segurança

### 8.1 Testes de Validação

```python
import unittest

class TestValidacao(unittest.TestCase):
    
    def test_username_valido(self):
        """Testa usernames válidos."""
        self.assertTrue(validar_username("user123"))
        self.assertTrue(validar_username("my-user_01"))
        self.assertTrue(validar_username("abc"))
    
    def test_username_invalido(self):
        """Testa usernames inválidos."""
        self.assertFalse(validar_username("../etc"))
        self.assertFalse(validar_username("user@domain"))
        self.assertFalse(validar_username("ab"))  # Muito curto
        self.assertFalse(validar_username("a" * 33))  # Muito longo
    
    def test_path_traversal(self):
        """Testa proteção contra path traversal."""
        self.assertFalse(validar_username("../../etc"))
        self.assertFalse(validar_username("../passwd"))
        self.assertFalse(validar_username("user/../admin"))
```

---

### 8.2 Testes de Criptografia

```python
class TestCriptografia(unittest.TestCase):
    
    def test_criptografia_decriptografia(self):
        """Testa ciclo completo de criptografia."""
        chave = secrets.token_bytes(32)
        dados = "Dados sensíveis"
        
        # Criptografa
        criptografado = criptografar_dados(chave, dados)
        
        # Decriptografa
        decriptografado = decriptografar_dados(chave, criptografado)
        
        # Verifica
        self.assertEqual(dados, decriptografado)
    
    def test_chave_invalida(self):
        """Testa rejeição de chaves inválidas."""
        with self.assertRaises(ValueError):
            criptografar_dados(b"chave_curta", "dados")
```

---

## Conclusão

Este guia fornece padrões seguros para implementação no Bagus Browser. Sempre:

1. ✅ **Valide** toda entrada do usuário
2. ✅ **Use** `secrets` para criptografia
3. ✅ **Gerencie** arquivos com context managers
4. ✅ **Trate** exceções especificamente
5. ✅ **Configure** segurança por padrão
6. ✅ **Limite** recursos e tamanhos
7. ✅ **Logue** de forma segura
8. ✅ **Teste** funcionalidades de segurança

**Lembre-se**: Segurança não é opcional - é fundamental!
