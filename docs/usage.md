# Uso

Este guia fornece exemplos práticos e referência completa da interface de linha de comando para o web scraper de livros.

## Início Rápido

### Execução Simples

Para executar o scraping com configurações padrão:

```bash
uv run main.py
```

**O que acontece:**

- Extrai dados de **1 página** (aproximadamente 20 livros)
- Usa **10 threads** para processamento paralelo
- Salva os resultados em `books.json`
- Cria logs detalhados em `logs/app.log`

### Primeira Execução

Recomendamos testar com uma página primeiro:

```bash
# Teste inicial com configurações padrão
uv run main.py

# Verificar se funcionou
ls -la books.json
cat books.json | head -20
```

## Referência Completa da CLI

### Sintaxe

```bash
uv run main.py [--threads THREADS] [--pages PAGES] [--help]
```

### Opções de Comando

| Opção | Tipo | Descrição | Padrão | Exemplo |
|-------|------|-----------|---------|---------|
| `--threads` | int | Número de threads para processamento concorrente | 10 | `--threads 15` |
| `--pages` | int | Número máximo de páginas para extrair | 1 | `--pages 5` |
| `--help` | - | Mostrar ajuda completa e sair | - | `--help` |

### Detalhes das Opções

#### `--threads` (Controle de Concorrência)
- **Função:** Define quantas operações paralelas executar
- **Impacto:** Mais threads = mais rápido, mas maior uso de recursos
- **Recomendações:**
  - **1-5 threads:** Uso conservador, menor impacto no servidor
  - **10-15 threads:** Balanceado (recomendado)
  - **20+ threads:** Alta performance, use com cuidado

#### `--pages` (Controle de Volume)
- **Função:** Limita quantas páginas do site serão processadas
- **Cada página:** Aproximadamente 20 livros
- **Total de livros:** páginas × 20 (aproximadamente)
- **Tempo estimado:** ~30-60 segundos por página (depende das threads)

## Exemplos Práticos

### Cenários de Uso Comum

#### 1. Teste Rápido (Desenvolvimento)
```bash
# Apenas 1 página, poucas threads
uv run main.py --threads 5 --pages 1
```
**Quando usar:** Testando mudanças no código, verificando funcionamento

#### 2. Coleta Moderada (Uso Típico)
```bash
# 5 páginas, threads balanceadas
uv run main.py --threads 10 --pages 5
```
**Quando usar:** Coleta regular de dados, análises pequenas

#### 3. Coleta Extensiva (Análise Completa)
```bash
# Muitas páginas, alta performance
uv run main.py --threads 15 --pages 20
```
**Quando usar:** Análises completas, datasets grandes

#### 4. Modo Conservador (Servidor Sensível)
```bash
# Poucas threads, processamento lento mas seguro
uv run main.py --threads 3 --pages 10
```
**Quando usar:** Evitar sobrecarga do servidor, conexão lenta

#### 5. Máxima Performance
```bash
# Configuração agressiva para máxima velocidade
uv run main.py --threads 25 --pages 50
```
**Quando usar:** Máquina potente, conexão rápida, urgência

### Exemplos com Monitoramento

#### Execução com Acompanhamento de Logs
```bash
# Executar em background e acompanhar logs
uv run main.py --threads 15 --pages 10 &
tail -f logs/app.log
```

#### Execução com Medição de Tempo
```bash
# Medir tempo total de execução
time uv run main.py --threads 20 --pages 5
```

#### Execução com Verificação de Recursos
```bash
# Monitorar uso de CPU/memória durante execução
htop &
uv run main.py --threads 15 --pages 10
```

## Saída de Dados

### Arquivo JSON Principal (`books.json`)

Os dados são salvos em `books.json` com estrutura detalhada para cada livro:

```json
[
  {
    "title": "A Light in the Attic",
    "price": "£51.77",
    "stock_available": "In stock (22 available)",
    "star_rating": 3,
    "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
    "detail_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "upc": "a897fe39b1053632",
    "product_type": "Books",
    "price_excl_tax": "£51.77",
    "price_incl_tax": "£51.77",
    "tax": "£0.00",
    "availability": "In stock (22 available)",
    "number_of_reviews": "0",
    "description": "It's hard to imagine a world without A Light in the Attic...",
    "category": "Poetry"
  }
]
```

#### Campos Disponíveis

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `title` | string | Título do livro | "A Light in the Attic" |
| `price` | string | Preço com símbolo | "£51.77" |
| `stock_available` | string | Status de estoque | "In stock (22 available)" |
| `star_rating` | int | Avaliação (1-5 estrelas) | 3 |
| `image_url` | string | URL da capa | "https://..." |
| `detail_url` | string | URL da página do livro | "https://..." |
| `upc` | string | Código único do produto | "a897fe39b1053632" |
| `product_type` | string | Tipo de produto | "Books" |
| `price_excl_tax` | string | Preço sem impostos | "£51.77" |
| `price_incl_tax` | string | Preço com impostos | "£51.77" |
| `tax` | string | Valor do imposto | "£0.00" |
| `availability` | string | Disponibilidade detalhada | "In stock (22 available)" |
| `number_of_reviews` | string | Número de avaliações | "0" |
| `description` | string | Descrição do livro | "It's hard to imagine..." |
| `category` | string | Categoria do livro | "Poetry" |

### Logs Detalhados (`logs/app.log`)

Os logs incluem informações completas sobre:

#### Informações de Progresso
```
2024-01-15 10:30:15 | INFO | Starting the scraping process...
2024-01-15 10:30:16 | INFO | Found 50 pages of books
2024-01-15 10:30:16 | INFO | Limiting to 5 pages as specified
2024-01-15 10:30:17 | INFO | Processing page 1/5: https://books.toscrape.com/
```

#### Estatísticas de Performance
```
2024-01-15 10:30:20 | INFO | Found 20 books on page 1
2024-01-15 10:30:25 | SUCCESS | Completed processing page 1
2024-01-15 10:35:30 | INFO | Total books collected: 100
```

#### Erros e Avisos
```
2024-01-15 10:30:22 | WARNING | No star rating found for book.
2024-01-15 10:30:23 | ERROR | Error processing detail page for Book Title: Connection timeout
```

### Verificação da Saída

#### Verificar Arquivo JSON
```bash
# Verificar se arquivo foi criado
ls -la books.json

# Ver primeiros livros
head -50 books.json

# Contar total de livros
cat books.json | jq length

# Ver apenas títulos
cat books.json | jq '.[].title'
```

#### Verificar Logs
```bash
# Ver logs em tempo real
tail -f logs/app.log

# Ver apenas erros
grep ERROR logs/app.log

# Ver estatísticas
grep "Total books collected" logs/app.log
```

## Boas Práticas

### Uso Responsável do Web Scraping

#### Configuração de Threads
```bash
# ✅ Recomendado: Balanceado
uv run main.py --threads 10 --pages 5

# ⚠️ Cuidado: Muitas threads podem sobrecarregar
uv run main.py --threads 50 --pages 20

# ✅ Conservador: Para servidores sensíveis
uv run main.py --threads 3 --pages 10
```

#### Respeitar Limites do Servidor
- **Threads moderadas:** 5-15 threads são geralmente seguras
- **Monitorar erros:** Se muitos erros 429/503, reduza threads
- **Pausas entre execuções:** Aguarde entre execuções grandes
- **Horários apropriados:** Evite horários de pico se possível

#### Ética do Web Scraping
- **robots.txt:** O site permite scraping educacional
- **Uso dos dados:** Apenas para fins educacionais/pesquisa
- **Não redistribuir:** Não republique os dados comercialmente
- **Atribuição:** Credite a fonte (books.toscrape.com)

### Otimização de Performance

#### Configurações por Cenário

**Máquina Local (Desenvolvimento):**
```bash
# Configuração balanceada para desenvolvimento
uv run main.py --threads 8 --pages 3
```

**Servidor Potente:**
```bash
# Aproveitar recursos disponíveis
uv run main.py --threads 20 --pages 15
```

**Conexão Lenta:**
```bash
# Reduzir concorrência para conexões instáveis
uv run main.py --threads 5 --pages 10
```

#### Monitoramento Durante Execução

**Acompanhar Progresso:**
```bash
# Terminal 1: Executar scraper
uv run main.py --threads 15 --pages 10

# Terminal 2: Monitorar logs
tail -f logs/app.log | grep -E "(INFO|ERROR|SUCCESS)"
```

**Verificar Recursos do Sistema:**
```bash
# Monitorar CPU e memória
htop

# Monitorar conexões de rede
netstat -an | grep :80
```

### Solução de Problemas Comuns

#### Performance Lenta
```bash
# Aumentar threads gradualmente
uv run main.py --threads 15 --pages 5  # Teste
uv run main.py --threads 20 --pages 5  # Se OK, aumente
```

#### Muitos Erros de Conexão
```bash
# Reduzir threads
uv run main.py --threads 5 --pages 10

# Verificar logs para padrões
grep "ERROR" logs/app.log | tail -20
```

#### Dados Incompletos
```bash
# Verificar se todos os livros foram processados
cat books.json | jq 'map(select(.description == "")) | length'

# Re-executar com menos threads se necessário
uv run main.py --threads 8 --pages 5
```

### Automação e Scripts

#### Script de Coleta Diária
```bash
#!/bin/bash
# daily_scrape.sh
echo "Iniciando coleta diária..."
uv run main.py --threads 10 --pages 5
echo "Coleta concluída em $(date)"
```

#### Backup Automático
```bash
# Fazer backup antes de nova execução
cp books.json "books_backup_$(date +%Y%m%d).json"
uv run main.py --threads 15 --pages 10
```

#### Análise Rápida dos Dados
```bash
# Estatísticas básicas após coleta
echo "Total de livros: $(cat books.json | jq length)"
echo "Categorias únicas: $(cat books.json | jq -r '.[].category' | sort -u | wc -l)"
echo "Preço médio: $(cat books.json | jq -r '.[].price' | sed 's/£//' | awk '{sum+=$1} END {print sum/NR}')"
```

## Próximos Passos

Após dominar o uso básico:

1. **Análise de Dados:** Use os dados coletados para análises
2. **Personalização:** Consulte [desenvolvimento](development.md) para modificar o código
3. **API Reference:** Veja [referência da API](api-reference.md) para entender as funções
4. **Troubleshooting:** Consulte [solução de problemas](troubleshooting.md) para issues específicos
5. **Contribuição:** Contribua com melhorias seguindo o [guia de desenvolvimento](development.md)
