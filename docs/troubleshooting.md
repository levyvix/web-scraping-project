# Solução de Problemas

Guia para resolver problemas comuns e perguntas frequentes.

## Problemas de Instalação

### Python 3.10+ não encontrado

**Sintoma:** Erro ao executar `uv sync` ou comandos Python

**Soluções:**
1. Verifique a versão do Python: `python --version`
2. Instale Python 3.10+ do site oficial
3. Use pyenv para gerenciar versões: `pyenv install 3.10`
4. Certifique-se de que Python está no PATH

### UV não instalado ou não encontrado

**Sintoma:** Comando `uv` não reconhecido

**Soluções:**
```bash
# Instalar UV via pip
pip install uv

# Ou via curl (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verificar instalação
uv --version
```

### Problemas de Dependências

**Sintoma:** Erros durante `uv sync`

**Soluções:**
```bash
# Limpar cache e reinstalar
uv cache clean
uv sync --refresh

# Verificar arquivo uv.lock
# Se corrompido, delete e execute uv sync novamente
rm uv.lock
uv sync
```

## Problemas de Execução

### Erro de Conexão de Rede

**Sintoma:** `ConnectionError` ou timeouts

**Mensagens de erro comuns:**
- `"Failed to fetch first page. Status code: [código]"`
- `"Failed to fetch page [número]. Status code: [código]"`
- `"Failed to fetch detail page for [título]. Status: [código]"`

**Possíveis Causas:**
- Problemas de conectividade
- Site temporariamente indisponível
- Muitas requisições simultâneas
- Rate limiting pelo servidor

**Soluções:**
```bash
# Reduzir número de threads
uv run main.py --threads 5

# Verificar conectividade
ping books.toscrape.com

# Testar com curl
curl -I https://books.toscrape.com/

# Tentar novamente após alguns minutos
# Usar apenas 1 thread para teste
uv run main.py --threads 1 --pages 1
```

### Erro de Parsing HTML

**Sintoma:** Dados incompletos ou erros de extração

**Mensagens de erro comuns:**
- `"No star rating found for book."`
- `"No book URL found in listing."`
- `"No image URL found for book."`
- `"No detail URL for book: [título]"`

**Diagnóstico:**
1. Verifique os logs em `logs/app.log`
2. Confirme se o site não mudou sua estrutura
3. Teste com uma página específica

**Soluções:**
```bash
# Executar com menos páginas para teste
uv run main.py --pages 1 --threads 1

# Verificar logs detalhados
tail -f logs/app.log

# Verificar se o site está acessível
curl -I https://books.toscrape.com/
```

### Problemas de Performance

**Sintoma:** Execução muito lenta

**Otimizações:**
```bash
# Aumentar threads (cuidado com sobrecarga)
uv run main.py --threads 15

# Verificar recursos do sistema
# CPU e memória disponíveis
```

**Sintoma:** Uso excessivo de memória

**Soluções:**
```bash
# Reduzir threads
uv run main.py --threads 5

# Processar menos páginas por vez
uv run main.py --pages 3
```

## Problemas Específicos do Scraping

### Falha na Primeira Página

**Sintoma:** `"Failed to fetch first page"` e aplicação para

**Causa:** A aplicação não consegue acessar a página inicial do site

**Soluções:**
```bash
# Verificar se o site está online
curl -I https://books.toscrape.com/

# Testar conectividade
ping books.toscrape.com

# Verificar proxy/firewall
# Se estiver atrás de proxy corporativo, configure as variáveis de ambiente
export HTTP_PROXY=http://proxy:porta
export HTTPS_PROXY=http://proxy:porta
```

### Páginas Sem Livros

**Sintoma:** `"No books found on page [número]!"` nos logs

**Possíveis Causas:**
- Mudança na estrutura HTML do site
- Página específica com problemas
- Seletores CSS desatualizados

**Diagnóstico:**
```bash
# Verificar página específica manualmente
curl https://books.toscrape.com/catalogue/page-2.html

# Executar com debug para uma página
uv run main.py --pages 1 --threads 1
```

### Erro de Processamento de Detalhes

**Sintoma:** `"Error processing detail page for [título]"` nos logs

**Causa:** Falha ao extrair informações da página de detalhes do livro

**Soluções:**
1. Verificar se a URL de detalhes está correta nos logs
2. Testar acesso manual à URL problemática
3. Reduzir threads para evitar sobrecarga

## Problemas de Dados

### Arquivo JSON corrompido

**Sintoma:** Erro ao abrir `books.json`

**Soluções:**
1. Verifique se o processo terminou corretamente
2. Procure por backups automáticos
3. Execute novamente o scraping

### Dados incompletos

**Sintoma:** Alguns livros sem informações

**Diagnóstico:**
```bash
# Verificar logs para erros específicos
grep "ERROR" logs/app.log

# Contar registros no JSON
python -c "import json; print(len(json.load(open('books.json'))))"
```

**Soluções:**
- Execute novamente com menos threads
- Verifique conectividade de rede
- Analise logs para padrões de erro

## Problemas de Desenvolvimento

### Testes Falhando

**Sintoma:** `pytest` retorna erros

**Diagnóstico:**
```bash
# Executar testes com saída detalhada
uv run pytest -v

# Executar teste específico
uv run pytest tests/test_main/test_specific.py -v
```

**Soluções:**
1. Verifique se todas as dependências estão instaladas
2. Confirme se o ambiente está atualizado: `uv sync --all-groups`
3. Verifique se há conflitos de versão

### Problemas de Linting

**Sintoma:** `ruff` reporta erros

**Soluções:**
```bash
# Formatar código automaticamente
uv run task format

# Verificar problemas específicos
uv run ruff check .

# Corrigir automaticamente quando possível
uv run ruff check . --fix
```

### Debug não funciona

**Sintoma:** VS Code debug não inicia

**Verificações:**
1. Confirme se `.vscode/launch.json` existe
2. Verifique se a extensão Python está instalada
3. Confirme se o interpretador Python está correto

## Perguntas Frequentes (FAQ)

### Q: Posso usar com outros sites?

**A:** O código é específico para Books to Scrape. Para outros sites, você precisará:
- Modificar as URLs base (`base_url` em `main()`)
- Ajustar os seletores CSS/XPath nos métodos de extração
- Adaptar a estrutura de dados no `process_book_listing()` e `process_book_details()`
- Modificar a lógica de paginação em `get_page_url()` e `get_total_pages()`

### Q: Como aumentar a velocidade?

**A:** Algumas opções:
```bash
# Mais threads (cuidado com rate limiting)
uv run main.py --threads 20

# Otimizar código para seu caso específico
# Remover campos desnecessários da extração
```

### Q: O scraping é legal?

**A:** Books to Scrape é um site de teste criado para praticar scraping. Para sites reais:
- Verifique o arquivo robots.txt
- Respeite os termos de uso
- Implemente rate limiting apropriado
- Considere usar APIs quando disponíveis

### Q: Como contribuir com o projeto?

**A:** Consulte o [guia de desenvolvimento](development.md) para:
- Configurar ambiente de desenvolvimento
- Entender a estrutura do código
- Seguir as diretrizes de contribuição

### Q: Por que alguns livros têm rating 0?

**A:** Isso acontece quando:
- O elemento de rating não é encontrado na página
- A classe CSS do rating não segue o padrão esperado
- Erro na extração do texto da classe

**Verificação:**
```bash
# Verificar logs para warnings sobre ratings
grep "No star rating found" logs/app.log
```

### Q: Como interpretar os logs?

**A:** Estrutura dos logs em `logs/app.log`:
- `INFO`: Informações gerais do progresso
- `WARNING`: Problemas não críticos (dados faltantes)
- `ERROR`: Erros que impedem processamento
- `SUCCESS`: Operações completadas com sucesso

**Exemplo de log normal:**
```
2024-01-15 10:30:15 | INFO     | main:main:200 - Starting the scraping process...
2024-01-15 10:30:16 | SUCCESS  | main:main:250 - Done!
```

### Q: O que fazer se o scraping parar no meio?

**A:** Possíveis soluções:
1. Verificar logs para identificar o erro específico
2. Reduzir número de threads: `--threads 5`
3. Processar menos páginas: `--pages 3`
4. Verificar espaço em disco disponível
5. Reiniciar com configurações mais conservadoras

### Q: Onde encontrar mais ajuda?

**A:** Recursos adicionais:
- [Documentação da API](api-reference.md)
- [Guia de uso](usage.md)
- Issues no repositório GitHub
- Logs detalhados em `logs/app.log`

## Gerenciamento de Logs

### Localização e Estrutura

Os logs são armazenados em `logs/app.log` com as seguintes características:
- **Rotação**: Arquivo rotaciona quando atinge 10MB
- **Retenção**: Logs são mantidos por 30 dias
- **Compressão**: Arquivos antigos são comprimidos em ZIP
- **Thread-safe**: Seguro para uso com múltiplas threads

### Comandos Úteis para Logs

```bash
# Ver logs em tempo real
tail -f logs/app.log

# Buscar erros específicos
grep "ERROR" logs/app.log

# Buscar warnings
grep "WARNING" logs/app.log

# Ver últimas 50 linhas
tail -n 50 logs/app.log

# Contar tipos de mensagens
grep -c "INFO" logs/app.log
grep -c "ERROR" logs/app.log
```

### Limpeza de Logs

```bash
# Limpar logs manualmente (se necessário)
rm logs/app.log*

# Os logs serão recriados automaticamente na próxima execução
```

## Reportando Problemas

### Informações Necessárias

Ao reportar um problema, inclua:

1. **Versão do Python**: `python --version`
2. **Versão do UV**: `uv --version`
3. **Sistema Operacional**: Windows/Linux/macOS
4. **Comando executado**: Comando completo usado
5. **Mensagem de erro**: Erro completo com stack trace
6. **Logs**: Conteúdo relevante de `logs/app.log`

### Template de Issue

```
## Descrição do Problema
[Descreva o problema claramente]

## Ambiente
- Python: [versão]
- UV: [versão]
- OS: [sistema operacional]

## Passos para Reproduzir
1. [Primeiro passo]
2. [Segundo passo]
3. [...]

## Comportamento Esperado
[O que deveria acontecer]

## Comportamento Atual
[O que está acontecendo]

## Logs/Erros
```
[Cole aqui os logs relevantes]
```

## Informações Adicionais
[Qualquer informação adicional relevante]
```

## Próximos Passos

Se não encontrou a solução aqui:
1. Consulte a [documentação completa](index.md)
2. Verifique issues existentes no repositório
3. Crie uma nova issue com informações detalhadas
4. Considere contribuir com a solução!
