# Referência da API

Esta seção fornece documentação técnica completa das funções e classes principais do projeto, gerada automaticamente a partir do código fonte.

## Visão Geral

O projeto de web scraping é estruturado em módulos principais que trabalham em conjunto para extrair dados de livros do site Books to Scrape. A documentação abaixo é gerada automaticamente a partir dos docstrings do código.

## Módulo Principal

::: main
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Módulo de Utilitários

### Logger

::: utils.logger
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

## Estrutura de Dados

### Formato dos Dados de Livros

Os dados extraídos seguem a seguinte estrutura:

```python
{
    "title": str,                    # Título do livro
    "price": str,                    # Preço formatado (ex: "£51.77")
    "stock_available": str,          # Status de estoque
    "star_rating": int,              # Avaliação em estrelas (1-5)
    "image_url": str,                # URL da imagem do livro
    "detail_url": str,               # URL da página de detalhes
    "upc": str,                      # Código UPC único
    "product_type": str,             # Tipo do produto
    "price_excl_tax": str,           # Preço sem impostos
    "price_incl_tax": str,           # Preço com impostos
    "tax": str,                      # Valor do imposto
    "availability": str,             # Disponibilidade detalhada
    "number_of_reviews": str,        # Número de avaliações
    "description": str,              # Descrição completa
    "category": str                  # Categoria do livro
}
```

## Exemplos de Uso

### Uso Básico via CLI

```bash
# Scraping básico (1 página, 10 threads)
uv run main.py

# Scraping personalizado
uv run main.py --threads 15 --pages 5

# Ver ajuda com todas as opções
uv run main.py --help
```

### Uso Programático

```python
from main import main, process_book_details, get_total_pages, save_to_json
from scrapling.fetchers import Fetcher

# Executar scraping com parâmetros personalizados
main(max_workers=15, max_pages=3)

# Exemplo de uso individual das funções
base_url = "https://books.toscrape.com/"
page = Fetcher.get(base_url, stealthy_headers=True)

# Obter número total de páginas
total_pages = get_total_pages(page, base_url)
print(f"Total de páginas: {total_pages}")

# Processar detalhes de um livro específico
book_data = {
    "title": "Example Book",
    "detail_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
}
enhanced_data = process_book_details(book_data)
print(f"Título: {enhanced_data['title']}")
print(f"Descrição: {enhanced_data['description']}")

# Salvar dados em JSON
books_data = [enhanced_data]
save_to_json(books_data, "my_books.json")
```

### Integração com Logging

```python
from utils.logger import logger

# O logger está pré-configurado e pronto para uso
logger.info("Iniciando processo personalizado")
logger.warning("Aviso importante")
logger.error("Erro encontrado")

# Exemplo de uso em uma função personalizada
def custom_scraping_function():
    logger.info("Iniciando scraping personalizado")
    try:
        # Seu código aqui
        result = some_operation()
        logger.success("Operação concluída com sucesso")
        return result
    except Exception as e:
        logger.error(f"Erro durante o scraping: {e}")
        raise
```

### Exemplo de Processamento de Avaliações

```python
from main import extract_star_rating
from scrapling.fetchers import Fetcher

# Exemplo de extração de avaliação de um livro
url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
page = Fetcher.get(url, stealthy_headers=True)
book_element = page.find("article.product_page")

if book_element:
    rating = extract_star_rating(book_element)
    print(f"Avaliação: {rating} estrelas")
```

## Tratamento de Erros

O projeto implementa tratamento robusto de erros:

- **Erros de Rede**: Logs detalhados e continuação do processamento
- **Parsing de HTML**: Validação de elementos antes da extração
- **Threading**: Tratamento de exceções em threads individuais
- **File I/O**: Verificação de permissões e tratamento de erros de escrita

## Performance e Concorrência

### Características de Performance

- **Threading**: Uso de `concurrent.futures.ThreadPoolExecutor` para processamento paralelo
- **Pool de Threads**: Configurável via parâmetro `max_workers`
- **Progress Tracking**: Barras de progresso com `tqdm` para feedback visual
- **Processamento em Lote**: Separação entre extração de listagens e detalhes

### Otimizações Implementadas

- Headers stealth para evitar bloqueios
- Reutilização de conexões HTTP
- Processamento paralelo de páginas e detalhes
- Logging estruturado para debugging

## Próximos Passos

- Consulte o [guia de desenvolvimento](development.md) para contribuir
- Veja [solução de problemas](troubleshooting.md) para issues comuns
- Confira os [exemplos de uso](usage.md) para casos práticos
