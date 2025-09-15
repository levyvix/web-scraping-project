# 🚀 Guia de Início Rápido

Este guia te ajudará a executar o web scraper em menos de 5 minutos usando Docker.

## ⚡ Início Ultra-Rápido

### 1. Pré-requisitos

Certifique-se de ter Docker instalado:
```bash
docker --version
docker-compose --version
```

### 2. Clone e Execute

```bash
# Clone o repositório
git clone https://github.com/levyvix/web-scraping-project.git
cd web-scraping-project

# Execute o scraper (configuração padrão)
docker-compose run --rm scraper
```

Pronto! Os dados serão salvos em `./output/books.json` e os logs em `./logs/app.log`.

## 🎯 Configurações Rápidas

### Configuração Básica
```bash
# 1 página, 10 threads (padrão)
docker-compose run --rm scraper
```

### Alta Performance
```bash
# 10 páginas, 20 threads
./scripts/docker-run.sh performance
```

### Teste Rápido
```bash
# 1 página, 5 threads
./scripts/docker-run.sh light
```

### Personalizado
```bash
# Seus próprios parâmetros
docker-compose run --rm scraper --threads 15 --pages 3
```

## 📁 Onde Encontrar os Resultados

- **Dados extraídos**: `./output/books.json`
- **Logs da aplicação**: `./logs/app.log`

## 🔧 Scripts de Conveniência

### Linux/macOS/Git Bash
```bash
# Ver todas as opções
./scripts/docker-run.sh examples

# Executar configuração específica
./scripts/docker-run.sh [basic|performance|light|dev]
```

### Windows
```cmd
# Ver todas as opções
scripts\docker-run.bat examples

# Executar configuração específica
scripts\docker-run.bat [basic|performance|light|dev]
```

## 🆘 Problemas Comuns

### Erro de Permissão
```bash
# Linux/macOS
sudo chown -R $USER:$USER output/ logs/
```

### Docker não encontrado
```bash
# Instalar Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Porta ocupada
Modifique as portas no `docker-compose.yml` se necessário.

## 📖 Próximos Passos

- Leia o [README completo](../README.md) para mais detalhes
- Consulte a [documentação Docker](DOCKER.md) para configurações avançadas
- Explore os [exemplos de configuração](../docker-compose.examples.yml)

## 💡 Dicas

1. **Primeira execução**: Pode demorar mais devido ao download das dependências
2. **Desenvolvimento**: Use `./scripts/docker-run.sh dev` para modo desenvolvimento
3. **Produção**: Use `docker-compose -f docker-compose.yml up scraper` sem override
4. **Monitoramento**: Use `docker-compose logs -f scraper` para ver logs em tempo real
