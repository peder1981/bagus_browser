# Guia de Segurança - Bagus Browser

## Visão Geral

Este documento descreve as medidas de segurança implementadas no Bagus Browser e as melhores práticas para uso seguro.

## Medidas de Segurança Implementadas

### 1. Criptografia

#### Melhorias Aplicadas
- **Geração de IVs**: Substituído `random.randint()` por `secrets.token_bytes()` para geração criptograficamente segura
- **Validação de Chaves**: Todas as funções de criptografia validam o tamanho das chaves (16, 24 ou 32 bytes)
- **Tratamento de Erros**: Exceções específicas para falhas de criptografia/decriptografia
- **Aviso sobre ECB**: Modo ECB marcado como inseguro, recomenda-se usar CBC

#### Uso Recomendado
```python
from browser.api.aes_helper import encrypt_aes_cbc_no_iv, decrypt_aes_cbc_no_iv

# Gerar chave de 32 bytes (AES-256)
key = secrets.token_bytes(32).hex()[:32]

# Criptografar
encrypted = encrypt_aes_cbc_no_iv(key, "dados sensíveis")

# Decriptografar
decrypted = decrypt_aes_cbc_no_iv(key, encrypted)
```

### 2. Validação de Entrada

#### Username
- Comprimento: 3-32 caracteres
- Caracteres permitidos: `a-zA-Z0-9_-`
- Proteção contra path traversal (`..`, `/`, `\`)
- Validação com regex: `^[a-zA-Z0-9_-]+$`

#### URLs
- Protocolos permitidos: `http://`, `https://`
- Tamanho máximo: 2048 caracteres
- Bloqueio de URLs com credenciais embutidas
- Validação de estrutura com `urlparse`

#### Paths de Arquivo
- Validação com `os.path.realpath()` para prevenir symlink attacks
- Verificação de que diretórios estão em `/tmp/`
- Permissões restritas: `0o700` (apenas owner)

### 3. Execução de JavaScript

#### Proteção contra Injeção
- Scripts devem estar em arquivos JSON no diretório `browser/resources/scripts_block/`
- Validação de estrutura JSON
- Limite de tamanho: 100KB por script
- Validação de regex para matching de URLs
- Decodificação segura de base64

#### Estrutura de Script Seguro
```json
{
  "name": "Nome do Script",
  "url": "^https://exemplo\\.com/.*",
  "active": true,
  "script": "base64_encoded_javascript_here"
}
```

### 4. Gestão de Arquivos

#### Boas Práticas Implementadas
- Uso de `with` statements para garantir fechamento de arquivos
- Validação de tamanho antes de carregar (limites específicos por tipo)
- Permissões restritas em diretórios criados (`0o700`)
- Validação de paths com `os.path.realpath()`

#### Limites de Tamanho
- Scripts JSON: 1MB
- JavaScript decodificado: 100KB
- Lista de bloqueio: 10MB
- Histórico: 10.000 entradas

### 5. Configurações de Navegador

#### Configuração Segura (template_secure.json)

**Desabilitado por Segurança:**
- `JavascriptCanAccessClipboard`: false (protege área de transferência)
- `JavascriptCanOpenWindows`: false (previne popups)
- `LocalContentCanAccessRemoteUrls`: false (isola conteúdo local)
- `LocalContentCanAccessFileUrls`: false (protege sistema de arquivos)
- `HyperlinkAuditingEnabled`: false (privacidade)
- `PluginsEnabled`: false (reduz superfície de ataque)
- `ScreenCaptureEnabled`: false (protege privacidade)
- `AllowRunningInsecureContent`: false (força HTTPS)
- `AllowGeolocationOnInsecureOrigins`: false (protege localização)
- `AllowWindowActivationFromJavaScript`: false (previne phishing)
- `JavascriptCanPaste`: false (protege contra roubo de dados)
- `DnsPrefetchEnabled`: false (privacidade)
- `NavigateOnDropEnabled`: false (previne navegação acidental)
- `ReadingFromCanvasEnabled`: false (protege contra fingerprinting)

**Habilitado para Funcionalidade:**
- `XSSAuditingEnabled`: true (proteção contra XSS)
- `WebRTCPublicInterfacesOnly`: true (protege IP privado)
- `JavascriptEnabled`: true (necessário para web moderna)

### 6. Bloqueio de Conteúdo

#### Interceptor de Requisições
- Lista de domínios bloqueados carregada em `set` para busca O(1)
- Bloqueio de domínios e subdomínios
- Logging de requisições bloqueadas
- Validação de tamanho de URL (max 2048 caracteres)

#### Atualização da Lista de Bloqueio
```bash
wget -O /tmp/{USERNAME}/ad_hosts_block.txt \
  https://raw.githubusercontent.com/naoimportaweb/bagus_browser/refs/heads/main/lists/ad_hosts_block.txt
```

### 7. Armazenamento Criptografado

#### Script de Criação (create.sh)
- Usa LUKS para criptografia de disco
- Geração aleatória com `/dev/urandom`
- Senha fornecida de forma segura (não via linha de comando visível)
- Montagem em `/tmp` com permissões restritas

**IMPORTANTE**: A senha é solicitada interativamente para evitar exposição em logs do sistema.

## Vulnerabilidades Corrigidas

### Críticas
1. ✅ Geração insegura de IVs e chaves (random → secrets)
2. ✅ Injeção de código via JavaScript não validado
3. ✅ Path traversal em username
4. ✅ Exposição de credenciais em URLs

### Altas
5. ✅ Falta de validação de entrada em múltiplos pontos
6. ✅ Gestão inadequada de arquivos (sem context managers)
7. ✅ Configurações inseguras por padrão
8. ✅ Falta de limites de tamanho em dados carregados

### Médias
9. ✅ Logging inadequado de erros
10. ✅ Falta de tratamento de exceções
11. ✅ Performance issues em buscas (O(n) → O(1))

## Recomendações de Uso

### Para Usuários

1. **Use a configuração segura**:
   ```bash
   cp data/template_secure.json ~/bagus/config.json
   ```

2. **Mantenha a lista de bloqueio atualizada**:
   ```bash
   # Adicione ao cron para atualização diária
   0 2 * * * wget -O /tmp/{USERNAME}/ad_hosts_block.txt https://...
   ```

3. **Use senhas fortes** para o volume criptografado (mínimo 20 caracteres)

4. **Não compartilhe** o diretório `/tmp/{USERNAME}` com outros usuários

5. **Feche o browser** quando não estiver em uso para desmontar o volume

### Para Desenvolvedores

1. **Nunca use `eval()` ou `exec()` com dados não confiáveis**

2. **Sempre valide entrada do usuário**:
   ```python
   if not validar_username(username):
       raise ValueError("Username inválido")
   ```

3. **Use context managers para arquivos**:
   ```python
   with open(path, 'r') as f:
       data = f.read()
   ```

4. **Limite tamanhos de dados**:
   ```python
   if os.path.getsize(file_path) > MAX_SIZE:
       raise ValueError("Arquivo muito grande")
   ```

5. **Use `secrets` para geração de valores aleatórios criptográficos**:
   ```python
   import secrets
   token = secrets.token_bytes(32)
   ```

## Auditoria de Segurança

### Checklist de Revisão

- [x] Criptografia usa geradores seguros
- [x] Validação de entrada em todos os pontos
- [x] Paths são validados e sanitizados
- [x] Arquivos são gerenciados com context managers
- [x] Limites de tamanho são aplicados
- [x] Exceções são tratadas adequadamente
- [x] Configurações padrão são seguras
- [x] Logs não expõem dados sensíveis
- [x] Permissões de arquivo são restritas
- [x] URLs são validadas antes de uso

### Testes de Segurança Recomendados

1. **Fuzzing de entrada**: Teste com inputs malformados
2. **Path traversal**: Tente acessar arquivos fora do escopo
3. **Injeção de código**: Tente executar código arbitrário
4. **DoS**: Teste com arquivos muito grandes
5. **XSS**: Teste injeção de scripts em páginas web

## Relatório de Vulnerabilidades

Se você encontrar uma vulnerabilidade de segurança, por favor:

1. **NÃO** abra uma issue pública
2. Entre em contato diretamente com os mantenedores
3. Forneça detalhes técnicos e passos para reproduzir
4. Aguarde confirmação antes de divulgar publicamente

## Atualizações de Segurança

Este documento será atualizado conforme novas medidas de segurança forem implementadas.

**Última atualização**: 2025-01-20
**Versão**: 1.0.0
