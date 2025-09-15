# Instalação

Este guia fornece instruções detalhadas para instalar e configurar o projeto de web scraping em diferentes sistemas operacionais.

## Pré-requisitos

- Python 3.10 ou superior
- Git (para clonar o repositório)
- UV (gerenciador de pacotes Python rápido)

## Instalação Passo a Passo

### Passo 1: Verificar Python

Primeiro, verifique se você tem Python 3.10+ instalado:

```bash
python --version
# ou
python3 --version
```

Se você não tem Python 3.10+, instale-o:

#### Windows
- Baixe do [python.org](https://www.python.org/downloads/)
- Ou use o Microsoft Store
- Ou use Chocolatey: `choco install python`

#### macOS
- Use Homebrew: `brew install python@3.10`
- Ou baixe do [python.org](https://www.python.org/downloads/)

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.10 python3.10-pip python3.10-venv
```

#### Linux (CentOS/RHEL/Fedora)
```bash
sudo dnf install python3.10 python3.10-pip
# ou para versões mais antigas
sudo yum install python3.10 python3.10-pip
```

### Passo 2: Instalar UV

UV é um gerenciador de pacotes Python extremamente rápido. Instale-o:

#### Método Recomendado (todos os sistemas)
```bash
pip install uv
```

#### Alternativa para Linux/macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Alternativa para Windows (PowerShell)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Passo 3: Clonar o Repositório

```bash
git clone levyvix/web-scraping-project
cd web-scraping-project
```

### Passo 4: Instalar Dependências

```bash
# Sincronizar todas as dependências
uv sync

# Para desenvolvimento (inclui ferramentas de teste e linting)
uv sync --all-groups
```

## Verificação da Instalação

Para verificar se tudo foi instalado corretamente, execute:

```bash
uv run main.py --help
```

Você deve ver a ajuda do comando com todas as opções disponíveis.

## Solução de Problemas de Instalação

### Problemas Comuns

#### Erro: Python 3.10+ não encontrado
**Sintomas:** `python: command not found` ou versão muito antiga
**Soluções:**
- Certifique-se de ter Python 3.10+ instalado
- No Windows, verifique se Python está no PATH
- No Linux/macOS, tente `python3` em vez de `python`
- Reinstale Python seguindo as instruções do Passo 1

#### Erro: UV não encontrado
**Sintomas:** `uv: command not found`
**Soluções:**
- Instale UV usando `pip install uv`
- Reinicie o terminal após a instalação
- No Windows, verifique se Scripts/ está no PATH
- Tente o método de instalação alternativo

#### Problemas de Dependências
**Sintomas:** Falhas durante `uv sync`
**Soluções:**
- Tente `uv sync --refresh` para limpar o cache
- Verifique se o arquivo `uv.lock` não foi corrompido
- Delete `.venv/` e execute `uv sync` novamente
- Verifique sua conexão com a internet

#### Problemas de Permissão (Linux/macOS)
**Sintomas:** `Permission denied` durante instalação
**Soluções:**
- Use `sudo` apenas se necessário
- Considere usar ambientes virtuais
- Verifique permissões do diretório: `ls -la`

#### Problemas de Proxy/Firewall
**Sintomas:** Timeouts ou falhas de conexão
**Soluções:**
- Configure proxy: `uv sync --proxy http://proxy:port`
- Verifique configurações de firewall
- Use rede diferente se possível

#### Problemas Específicos do Windows
**Sintomas:** Erros de codificação ou paths longos
**Soluções:**
- Execute como Administrador se necessário
- Habilite paths longos no Windows
- Use PowerShell em vez do CMD
- Verifique codificação: `chcp 65001`

#### Problemas de Versão do Python
**Sintomas:** Incompatibilidades ou recursos não disponíveis
**Soluções:**
- Verifique: `python --version` deve ser 3.10+
- Use `python3.10` explicitamente se disponível
- Considere usar pyenv para gerenciar versões

### Verificação Avançada

Para diagnóstico mais detalhado:

```bash
# Verificar instalação do Python
python --version
which python

# Verificar instalação do UV
uv --version
which uv

# Verificar dependências instaladas
uv pip list

# Testar importações principais
python -c "import scrapling; print('Scrapling OK')"
python -c "import loguru; print('Loguru OK')"
```

## Instalação para Diferentes Ambientes

### Ambiente de Desenvolvimento
Para contribuir com o projeto:

```bash
# Clone e instale com dependências de desenvolvimento
git clone levyvix/web-scraping-project
cd web-scraping-project
uv sync --all-groups

# Instalar hooks de pre-commit (opcional)
uv run pre-commit install
```

### Ambiente de Produção
Para uso apenas:

```bash
# Clone e instale apenas dependências principais
git clone levyvix/web-scraping-project
cd web-scraping-project
uv sync
```

### Usando Docker (Alternativa)
Se preferir usar Docker:

```bash
# Construir imagem (se Dockerfile disponível)
docker build -t web-scraper .

# Executar container
docker run -v $(pwd)/output:/app/output web-scraper
```

## Configuração Adicional

### Configurar Logs
O projeto criará automaticamente o diretório `logs/`, mas você pode configurar:

```bash
# Verificar se diretório de logs existe
ls -la logs/

# Configurar rotação de logs (opcional)
# Edite utils/logger.py se necessário
```

### Configurar Saída
Por padrão, os dados são salvos em `books.json`:

```bash
# Verificar permissões de escrita
touch books.json
ls -la books.json
```

## Próximos Passos

Após a instalação bem-sucedida:

1. **Teste a instalação:** `uv run main.py --help`
2. **Execute um teste simples:** `uv run main.py --pages 1`
3. **Consulte o [guia de uso](usage.md)** para opções avançadas
4. **Veja [desenvolvimento](development.md)** se quiser contribuir
5. **Consulte [solução de problemas](troubleshooting.md)** se encontrar issues
