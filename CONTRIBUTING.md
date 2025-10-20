# Guia de Contribuição - Bagus Browser

Obrigado por considerar contribuir com o Bagus Browser! Este documento fornece diretrizes para contribuir com o projeto.

---

## 📋 Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Posso Contribuir?](#como-posso-contribuir)
3. [Diretrizes de Desenvolvimento](#diretrizes-de-desenvolvimento)
4. [Processo de Pull Request](#processo-de-pull-request)
5. [Padrões de Código](#padrões-de-código)
6. [Segurança](#segurança)
7. [Documentação](#documentação)

---

## Código de Conduta

Este projeto adere a um código de conduta. Ao participar, espera-se que você mantenha este código. Por favor, reporte comportamentos inaceitáveis.

### Nossos Padrões

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

---

## Como Posso Contribuir?

### Reportando Bugs

Antes de criar um bug report:
- Verifique se já não existe uma issue sobre o problema
- Teste com a versão mais recente
- Colete informações sobre o ambiente

Use o template de bug report e inclua:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Ambiente (OS, Python, versões)
- Logs relevantes

### Sugerindo Melhorias

Use o template de feature request e inclua:
- Descrição clara da funcionalidade
- Problema que resolve
- Impacto na segurança/privacidade
- Exemplos de uso

### Reportando Vulnerabilidades de Segurança

**⚠️ IMPORTANTE**: NÃO reporte vulnerabilidades publicamente!

- Entre em contato diretamente com os mantenedores
- Consulte [SECURITY.md](SECURITY.md) para o processo completo
- Aguarde confirmação antes de divulgar

---

## Diretrizes de Desenvolvimento

### Configuração do Ambiente

```bash
# Clone o repositório
git clone https://github.com/peder1981/bagus_browser.git
cd bagus_browser

# Instale dependências
pip install -r requirements.txt

# Configure ambiente de desenvolvimento
python app.py
```

### Estrutura do Projeto

```
bagus_browser/
├── app.py                 # Ponto de entrada
├── browser/               # Código principal
│   ├── api/              # APIs e helpers
│   ├── ui/               # Interface do usuário
│   └── resources/        # Recursos (CSS, scripts)
├── data/                 # Dados e configurações
├── bash/                 # Scripts shell
└── docs/                 # Documentação
```

### Branches

- `main` - Branch principal (produção)
- `develop` - Branch de desenvolvimento
- `feature/nome` - Novas funcionalidades
- `fix/nome` - Correções de bugs
- `security/nome` - Correções de segurança

---

## Processo de Pull Request

### 1. Fork e Clone

```bash
# Fork no GitHub, depois:
git clone https://github.com/seu-usuario/bagus_browser.git
cd bagus_browser
git remote add upstream https://github.com/peder1981/bagus_browser.git
```

### 2. Crie uma Branch

```bash
git checkout -b feature/minha-funcionalidade
```

### 3. Faça suas Mudanças

- Siga os padrões de código
- Adicione testes
- Atualize documentação
- Commit com mensagens claras

### 4. Teste suas Mudanças

```bash
# Execute testes (quando disponíveis)
python -m pytest

# Teste manualmente
python app.py
```

### 5. Commit

Use mensagens de commit descritivas:

```bash
git commit -m "feat: adiciona validação de email"
git commit -m "fix: corrige vazamento de memória em browser_tab"
git commit -m "docs: atualiza guia de instalação"
git commit -m "security: corrige vulnerabilidade XSS"
```

Padrões de commit:
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças na documentação
- `style:` - Formatação de código
- `refactor:` - Refatoração
- `test:` - Adição de testes
- `security:` - Correções de segurança
- `perf:` - Melhorias de performance

### 6. Push e Pull Request

```bash
git push origin feature/minha-funcionalidade
```

Crie um Pull Request no GitHub usando o template.

---

## Padrões de Código

### Python

Siga PEP 8 e as diretrizes do projeto:

```python
# ✅ BOM
def validar_username(username):
    """Valida o username para prevenir path traversal.
    
    Args:
        username: Nome de usuário a ser validado
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if not username or len(username) < 3:
        return False
    return True

# ❌ RUIM
def val(u):
    if not u or len(u)<3:return False
    return True
```

### Validação de Entrada

**SEMPRE valide entrada do usuário:**

```python
# ✅ BOM
import re

def validar_entrada(entrada):
    if not entrada or len(entrada) > 1000:
        raise ValueError("Entrada inválida")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', entrada):
        raise ValueError("Caracteres inválidos")
    
    return entrada

# ❌ RUIM
def processar(entrada):
    # Sem validação!
    return processar_dados(entrada)
```

### Gestão de Arquivos

**SEMPRE use context managers:**

```python
# ✅ BOM
with open(path, 'r') as f:
    data = f.read()

# ❌ RUIM
f = open(path, 'r')
data = f.read()
# Arquivo pode não ser fechado!
```

### Tratamento de Exceções

**Use exceções específicas:**

```python
# ✅ BOM
try:
    data = processar(entrada)
except ValueError as e:
    print(f"Erro de validação: {e}")
    raise
except FileNotFoundError as e:
    print(f"Arquivo não encontrado: {e}")
    raise

# ❌ RUIM
try:
    data = processar(entrada)
except:
    pass  # Silencia todos os erros!
```

### Criptografia

**Use secrets, não random:**

```python
# ✅ BOM
import secrets
key = secrets.token_bytes(32)

# ❌ RUIM
import random
key = ''.join(random.choice(chars) for _ in range(32))
```

---

## Segurança

### Checklist de Segurança

Antes de submeter um PR, verifique:

- [ ] Validei todas as entradas do usuário
- [ ] Usei `secrets` para valores aleatórios
- [ ] Implementei limites de tamanho
- [ ] Usei context managers para arquivos
- [ ] Tratei exceções especificamente
- [ ] Não expus dados sensíveis em logs
- [ ] Validei paths com `os.path.realpath()`
- [ ] Não introduzi injeção de código
- [ ] Não introduzi path traversal

### Consulte a Documentação

- [SECURITY.md](SECURITY.md) - Guia de segurança
- [GUIA_IMPLEMENTACAO.md](GUIA_IMPLEMENTACAO.md) - Padrões seguros

---

## Documentação

### Docstrings

Use docstrings em todas as funções públicas:

```python
def funcao_exemplo(parametro1, parametro2):
    """Descrição breve da função.
    
    Descrição mais detalhada se necessário.
    
    Args:
        parametro1 (tipo): Descrição do parâmetro 1
        parametro2 (tipo): Descrição do parâmetro 2
    
    Returns:
        tipo: Descrição do retorno
    
    Raises:
        ValueError: Quando parametro1 é inválido
        TypeError: Quando parametro2 tem tipo errado
    
    Example:
        >>> funcao_exemplo("valor1", 42)
        resultado
    """
    pass
```

### Atualize a Documentação

Quando fizer mudanças, atualize:

- README.md (se necessário)
- CHANGELOG.md (sempre)
- SECURITY.md (se afetar segurança)
- Documentação de código (docstrings)

---

## Testes

### Escrevendo Testes

```python
import unittest

class TestValidacao(unittest.TestCase):
    def test_username_valido(self):
        """Testa username válido."""
        self.assertTrue(validar_username("user123"))
    
    def test_username_invalido(self):
        """Testa username inválido."""
        self.assertFalse(validar_username("../etc"))
```

### Executando Testes

```bash
# Quando disponível
python -m pytest
python -m pytest tests/test_validacao.py
```

---

## Revisão de Código

### O Que Esperamos

- Código limpo e legível
- Testes adequados
- Documentação atualizada
- Sem vulnerabilidades de segurança
- Conformidade com padrões do projeto

### Processo de Revisão

1. Mantenedores revisarão seu PR
2. Podem solicitar mudanças
3. Faça as mudanças solicitadas
4. PR será mesclado quando aprovado

---

## Perguntas?

- Abra uma issue com a tag `question`
- Consulte a documentação existente
- Entre em contato com os mantenedores

---

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT).

---

**Obrigado por contribuir com o Bagus Browser!** 🎉
