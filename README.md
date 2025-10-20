# Bagus Browser

**Browser seguro e focado em privacidade para Linux**

[![Segurança](https://img.shields.io/badge/security-hardened-green.svg)](SECURITY.md)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🔒 Características de Segurança

- ✅ **Armazenamento Criptografado**: Dados do usuário em volume LUKS
- ✅ **Criptografia Forte**: AES-256 com geração segura de IVs
- ✅ **Validação de Entrada**: Proteção contra path traversal e injeção
- ✅ **Bloqueio de Conteúdo**: Lista de domínios maliciosos e rastreadores
- ✅ **Configurações Seguras**: Proteção contra XSS, fingerprinting e vazamento de dados
- ✅ **Isolamento**: Cada usuário tem seu próprio ambiente isolado

## 📋 Requisitos

- **Sistema Operacional**: Linux (apenas)
- **Python**: 3.8 ou superior
- **Dependências do Sistema**:
  - `cryptsetup` (para volumes LUKS)
  - `sudo` (para montagem de volumes)

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/naoimportaweb/bagus_browser.git
cd bagus_browser
```

### 2. Instale as Dependências Python

```bash
pip install -r requirements.txt
```

### 3. Configure o Usuário

```bash
python app.py
```

Na tela de login:
1. Digite um **username** (3-32 caracteres, apenas letras, números, _ ou -)
2. Copie e execute o script mostrado no terminal
3. Informe uma **senha forte** (recomendado: 20+ caracteres)
4. Clique em "Start Browser"

## 🔐 Configuração de Segurança

### Usar Configuração Segura (Recomendado)

```bash
cp data/template_secure.json ~/bagus/config.json
```

Esta configuração desabilita:
- Acesso JavaScript à área de transferência
- Abertura de popups
- Conteúdo inseguro (HTTP em páginas HTTPS)
- Captura de tela
- Geolocalização em origens inseguras
- Canvas fingerprinting

### Atualizar Lista de Bloqueio

```bash
wget -O /tmp/{USERNAME}/ad_hosts_block.txt \
  https://raw.githubusercontent.com/naoimportaweb/bagus_browser/refs/heads/main/lists/ad_hosts_block.txt
```

## 📖 Uso

### Iniciar o Browser

```bash
python app.py
```

### Atalhos de Teclado

- `Ctrl+T`: Nova aba
- `Ctrl+W`: Fechar aba atual
- `Ctrl+Q`: Fechar browser
- `Ctrl+N`: Minimizar janela

### Funcionalidades

- **Navegação Privada**: Todos os dados em volume criptografado
- **Bloqueio de Anúncios**: Lista automática de domínios bloqueados
- **Histórico Local**: Armazenado apenas localmente, nunca sincronizado
- **Scripts Personalizados**: Execute JavaScript em sites específicos
- **Projetos**: Sistema de extensões customizadas

## 🛡️ Segurança

Para informações detalhadas sobre segurança, consulte [SECURITY.md](SECURITY.md).

### Vulnerabilidades Corrigidas

- ✅ Geração insegura de chaves criptográficas
- ✅ Injeção de código JavaScript
- ✅ Path traversal em usernames
- ✅ Exposição de credenciais em URLs
- ✅ Configurações inseguras por padrão
- ✅ Gestão inadequada de arquivos

### Relatório de Vulnerabilidades

Se você encontrar uma vulnerabilidade, **não abra uma issue pública**. Entre em contato diretamente com os mantenedores.

## 📚 Documentação

- [Guia de Segurança](SECURITY.md)
- [Documento Original](https://docs.google.com/document/d/1YSVWXfkrkKDsL_8SF-wrAVpSCQ8WPkduQOpYFXmrw80/edit?usp=sharing)
- [Vídeo Demonstração](https://youtube.com/live/15FHEEycVeg?feature=share)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Siga as práticas de segurança documentadas
2. Adicione testes para novas funcionalidades
3. Mantenha o código limpo e documentado
4. Não comprometa a privacidade do usuário

## ⚠️ Avisos Importantes

1. **Apenas Linux**: Este browser foi projetado especificamente para Linux
2. **Senha Forte**: Use senhas fortes para o volume criptografado
3. **Backup**: Faça backup regular do arquivo `~/.{username}.img`
4. **Não Compartilhe**: Nunca compartilhe seu diretório de usuário

## 📝 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para detalhes.

## 🙏 Agradecimentos

- Comunidade PySide6
- Projeto Chromium
- Mantenedores de listas de bloqueio de anúncios

