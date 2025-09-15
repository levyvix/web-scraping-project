# Guia Docker - Web Scraping Project

Este documento fornece informações detalhadas sobre como usar Docker com o projeto de web scraping.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Configurações Disponíveis](#configurações-disponíveis)
- [Uso Básico](#uso-básico)
- [Configurações Avançadas](#configurações-avançadas)
- [Health Check e Monitoramento](#health-check-e-monitoramento)
- [Scripts Auxiliares](#scripts-auxiliares)
- [Volumes e Persistência](#volumes-e-persistência)
- [Troubleshooting](#troubleshooting)

## 🔍 Visão Geral

O projeto utiliza Docker para fornecer um ambiente consistente e isolado para execução do web scraper. A configuração inclui:

- **Dockerfile multi-stage** para builds otimizados
- **Docker Compose** com múltiplas configurações
- **Volumes persistentes** para dados e logs
- **Scripts auxiliares** para facilitar o uso

## 📋 Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) (versão 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (versão 2.0+)

### Verificação da Instalação

```bash
# Verificar versão do Docker
docker --version

# Verificar versão do Docker Compose
docker-compose --version

# Testar instalação
docker run hello-world
```

## ⚙️ Configurações Disponíveis

### 1. Configuração Padrão (Desenvolvimento)

**Arquivo**: `docker-compose.yml` + `docker-compose.override.yml`

```yaml
services:
  scraper:
    build: .
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
      - .:/app/src:ro  # Código fonte montado (desenvolvimento)
    environment:
      - DEBUG=1
```

**Características**:
- Código fonte montado para desenvolvimento
- Modo debug habilitado
- Argumentos personalizáveis
- Modo interativo

### 2. Configuração de Produção

**Comando**: `docker-compose -f docker-compose.yml up scraper`

**Características**:
- Sem montagem de código fonte
- Otimizado para performance
- Sem variáveis de debug

### 3. Alta Performance

**Arquivo**: Profile `performance`

```yaml
scraper-performance:
  command: ["--threads", "20", "--pages", "10"]
  profiles: ["performance"]
```

**Comando**: `docker-compose --profile performance up scraper-performance`

### 4. Testes Leves

**Arquivo**: Profile `light`

```yaml
scraper-light:
  command: ["--threads", "5", "--pages", "1"]
  profiles: ["light"]
```

**Comando**: `docker-compose --profile light up scraper-light`

## 🚀 Uso Básico

### Execução Simples

```bash
# Executar com configurações padrão
docker-compose run --rm scraper

# Executar com argumentos personalizados
docker-compose run --rm scraper --threads 15 --pages 3

# Ver ajuda
docker-compose run --rm scraper --help
```

### Construção da Imagem

```bash
# Construir imagem
docker-compose build scraper

# Forçar reconstrução
docker-compose build --no-cache scraper
```

### Execução em Background

```bash
# Executar em background
docker-compose up -d scraper

# Ver logs
docker-compose logs -f scraper

# Parar serviço
docker-compose down
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

Você pode personalizar o comportamento através de variáveis de ambiente:

```bash
# Criar arquivo .env
echo "PYTHONUNBUFFERED=1" > .env
echo "DEBUG=1" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
echo "CONTAINER_ENV=true" >> .env

# Executar com variáveis personalizadas
docker-compose --env-file .env up scraper
```

### Configuração de Recursos

Para limitar recursos do container:

```yaml
services:
  scraper:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.5'
```

### Rede Personalizada

```yaml
networks:
  scraper_network:
    driver: bridge

services:
  scraper:
    networks:
      - scraper_network
```

## 🏥 Health Check e Monitoramento

O projeto inclui funcionalidades avançadas de health check e monitoramento para ambientes de produção e orquestração de containers.

### Health Check Integrado

O container possui um health check integrado que verifica:

- **Diretórios de saída**: Verificação de escrita em `/app/output` e `/app/logs`
- **Dependências**: Validação de bibliotecas críticas (scrapling, loguru, etc.)
- **Site alvo**: Conectividade com https://books.toscrape.com/
- **Atividade recente**: Verificação de arquivos de saída recentes

#### Configuração do Health Check

```yaml
# docker-compose.yml
services:
  scraper:
    healthcheck:
      test: ["CMD", "python", "healthcheck.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    restart: unless-stopped
```

#### Execução Manual do Health Check

```bash
# Executar health check diretamente
docker-compose exec scraper python healthcheck.py

# Verificar status de saúde do container
docker inspect book-scraper --format='{{.State.Health.Status}}'

# Ver histórico de health checks
docker inspect book-scraper --format='{{range .State.Health.Log}}{{.Start}}: {{.Output}}{{end}}'
```

### Monitoramento Avançado

#### Script de Monitoramento

O projeto inclui um script de monitoramento completo:

```bash
# Monitoramento único (snapshot)
python scripts/monitor.py

# Monitoramento contínuo
python scripts/monitor.py --watch --interval 30

# Verificar apenas logs recentes
python scripts/monitor.py --logs

# Executar apenas health check
python scripts/monitor.py --health

# Monitorar container específico
python scripts/monitor.py --container my-scraper --watch
```

#### Saída do Monitoramento

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "container": {
    "container_name": "book-scraper",
    "status": "running",
    "running": true,
    "health": "healthy",
    "restart_count": 0
  },
  "health": {
    "health_check_available": true,
    "health_data": {
      "status": "healthy",
      "checks": {
        "output_directory": true,
        "logs_directory": true,
        "dependencies": true,
        "target_website": true,
        "recent_activity": true
      }
    }
  },
  "output": {
    "total_output_files": 1,
    "total_log_files": 1,
    "output_files": [
      {
        "name": "books.json",
        "size_bytes": 15420,
        "modified": "2024-01-15T10:25:00"
      }
    ]
  }
}
```

### Shutdown Gracioso

O container suporta shutdown gracioso através de sinais:

- **SIGTERM**: Shutdown gracioso (usado pelo Docker/Kubernetes)
- **SIGINT**: Interrupção (Ctrl+C)
- **SIGHUP**: Reload/restart

#### Funcionalidades do Shutdown Gracioso

- Cancelamento de futures ativas
- Salvamento de dados parciais
- Limpeza de recursos
- Logs estruturados de shutdown
- Exit codes apropriados

```bash
# Testar shutdown gracioso
docker-compose stop scraper  # Envia SIGTERM

# Forçar parada (não recomendado)
docker-compose kill scraper  # Envia SIGKILL
```

### Logging Estruturado

Em ambiente de container, o logging é automaticamente configurado para formato JSON estruturado:

```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "level": "INFO",
  "logger": "main",
  "function": "main",
  "line": 45,
  "message": "Starting scraping process...",
  "module": "main",
  "process": 1,
  "thread": 140234567890
}
```

#### Configuração de Log Level

```bash
# Definir nível de log
docker-compose run -e LOG_LEVEL=DEBUG scraper

# Logs apenas de erro
docker-compose run -e LOG_LEVEL=ERROR scraper
```

### Testes de Health Check

Execute os testes automatizados:

```bash
# Linux/macOS
./scripts/test-health.sh

# Windows
scripts\test-health.bat

# Testes unitários
uv run pytest tests/test_healthcheck.py -v
```

### Integração com Orquestradores

#### Kubernetes

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: scraper
    image: book-scraper:latest
    livenessProbe:
      exec:
        command:
        - python
        - healthcheck.py
      initialDelaySeconds: 30
      periodSeconds: 30
    readinessProbe:
      exec:
        command:
        - python
        - healthcheck.py
      initialDelaySeconds: 5
      periodSeconds: 10
```

#### Docker Swarm

```yaml
version: '3.8'
services:
  scraper:
    image: book-scraper:latest
    healthcheck:
      test: ["CMD", "python", "healthcheck.py"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

## 🛠️ Scripts Auxiliares

### Scripts de Execução

#### Linux/macOS/Git Bash

```bash
# Tornar executável
chmod +x scripts/docker-run.sh

# Usar script
./scripts/docker-run.sh [profile] [argumentos-docker-compose]
```

**Exemplos**:
```bash
# Configuração básica
./scripts/docker-run.sh basic

# Alta performance
./scripts/docker-run.sh performance

# Com argumentos adicionais do Docker Compose
./scripts/docker-run.sh performance --build

# Ver opções disponíveis
./scripts/docker-run.sh examples
```

#### Windows

```cmd
# Executar script
scripts\docker-run.bat [profile] [argumentos-docker-compose]
```

**Exemplos**:
```cmd
# Configuração básica
scripts\docker-run.bat basic

# Alta performance
scripts\docker-run.bat performance

# Ver opções disponíveis
scripts\docker-run.bat examples
```

### Scripts de Build e Teste

#### Script de Build

**Linux/macOS/Git Bash**:
```bash
# Build básico
./scripts/docker-build.sh

# Build com tag específica
./scripts/docker-build.sh -t v1.0.0

# Build sem cache
./scripts/docker-build.sh --no-cache -t dev

# Build multi-plataforma
./scripts/docker-build.sh -p linux/amd64,linux/arm64 -t multi

# Build e push para registry
./scripts/docker-build.sh --push --registry myregistry.com -t prod

# Ver todas as opções
./scripts/docker-build.sh --help
```

**Windows**:
```cmd
# Build básico
scripts\docker-build.bat

# Build com tag específica
scripts\docker-build.bat -t v1.0.0

# Build sem cache
scripts\docker-build.bat --no-cache -t dev

# Ver todas as opções
scripts\docker-build.bat --help
```

#### Script de Teste

**Linux/macOS/Git Bash**:
```bash
# Testes básicos
./scripts/docker-test.sh

# Testes com comparação de performance
./scripts/docker-test.sh -p

# Testar imagem específica
./scripts/docker-test.sh -i myimage:v1.0

# Testes verbosos sem limpeza
./scripts/docker-test.sh -v --no-cleanup

# Ver todas as opções
./scripts/docker-test.sh --help
```

**Windows**:
```cmd
# Testes básicos
scripts\docker-test.bat

# Testes com comparação de performance
scripts\docker-test.bat -p

# Testar imagem específica
scripts\docker-test.bat -i myimage:v1.0

# Ver todas as opções
scripts\docker-test.bat --help
```

#### Script de Performance

```bash
# Teste de performance padrão
./scripts/docker-performance.sh

# Teste personalizado
./scripts/docker-performance.sh -n 5 --threads "10 20" --pages "1 2"

# Salvar resultados em arquivo específico
./scripts/docker-performance.sh -o my_results.json -v

# Ver todas as opções
./scripts/docker-performance.sh --help
```

#### Script de CI Completo

```bash
# Pipeline completo: build + test
./scripts/docker-ci.sh

# Pipeline com performance e push
./scripts/docker-ci.sh -p --push --registry myregistry.com

# Build e push sem testes
./scripts/docker-ci.sh --no-tests --push -t production

# Ver todas as opções
./scripts/docker-ci.sh --help
```

### Testes Executados

Os scripts de teste verificam:

1. **Verificação da Imagem**: Confirma que a imagem Docker existe
2. **Execução Básica**: Testa execução com parâmetros padrão
3. **Passagem de Argumentos**: Valida argumentos customizados (--threads, --pages)
4. **Montagem de Volumes**: Verifica criação de diretórios de teste
5. **Geração de Output**: Confirma criação do arquivo books.json
6. **Geração de Logs**: Verifica criação do arquivo app.log
7. **Execução Não-Root**: Confirma que o container roda como usuário não-root
8. **Comparação de Performance**: Compara execução nativa vs containerizada (opcional)

## 💾 Volumes e Persistência

### Volumes Configurados

| Volume Local | Volume Container | Descrição |
|--------------|------------------|-----------|
| `./output` | `/app/output` | Arquivos de saída (books.json) |
| `./logs` | `/app/logs` | Logs da aplicação |
| `.` | `/app/src` | Código fonte (apenas desenvolvimento) |

### Gerenciamento de Volumes

```bash
# Listar volumes
docker volume ls

# Inspecionar volume
docker volume inspect web-scraping-project_scraper_output

# Limpar volumes não utilizados
docker volume prune
```

### Backup de Dados

```bash
# Backup do diretório output
tar -czf backup-output-$(date +%Y%m%d).tar.gz output/

# Backup dos logs
tar -czf backup-logs-$(date +%Y%m%d).tar.gz logs/
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Permissões de Volume

**Problema**: Erro de permissão ao escrever arquivos

**Solução**:
```bash
# Linux/macOS
sudo chown -R $USER:$USER output/ logs/

# Windows (PowerShell como Administrador)
icacls output /grant Everyone:F /T
icacls logs /grant Everyone:F /T
```

#### 2. Porta Ocupada

**Problema**: Conflito de porta

**Solução**: Modificar `docker-compose.yml`
```yaml
ports:
  - "8081:8080"  # Usar porta diferente
```

#### 3. Memória Insuficiente

**Problema**: Container termina por falta de memória

**Solução**: Aumentar limite de memória
```yaml
deploy:
  resources:
    limits:
      memory: 1G
```

#### 4. Build Falha

**Problema**: Erro durante construção da imagem

**Soluções**:
```bash
# Limpar cache do Docker
docker system prune -a

# Reconstruir sem cache
docker-compose build --no-cache

# Verificar logs detalhados
docker-compose build --progress=plain
```

### Debug e Logs

#### Logs Detalhados

```bash
# Logs em tempo real
docker-compose logs -f scraper

# Logs com timestamps
docker-compose logs -t scraper

# Últimas 100 linhas
docker-compose logs --tail=100 scraper
```

#### Acesso ao Container

```bash
# Executar bash no container
docker-compose run --rm --entrypoint /bin/bash scraper

# Executar comando específico
docker-compose run --rm --entrypoint python scraper --version
```

#### Inspeção da Imagem

```bash
# Listar camadas da imagem
docker history web-scraping-project-scraper

# Inspecionar imagem
docker inspect web-scraping-project-scraper

# Verificar tamanho
docker images web-scraping-project-scraper
```

### Performance

#### Monitoramento de Recursos

```bash
# Estatísticas em tempo real
docker stats

# Uso de recursos específico
docker stats web-scraping-project-scraper
```

#### Otimização

1. **Multi-stage builds**: Já implementado no Dockerfile
2. **Cache de dependências**: UV cache otimizado
3. **Imagem base slim**: Python 3.10-slim utilizado
4. **Usuário não-root**: Configurado para segurança

### Limpeza

```bash
# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune

# Limpeza completa (cuidado!)
docker system prune -a --volumes
```

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Dockerfile](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
