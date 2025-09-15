# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- 🐳 **Suporte completo ao Docker**
  - Dockerfile multi-stage otimizado para produção
  - Configuração Docker Compose com múltiplos perfis
  - Scripts auxiliares para Linux/macOS/Windows
  - Volumes persistentes para dados e logs
  - Configurações predefinidas (básica, performance, light, desenvolvimento)

- 📁 **Organização de saída melhorada**
  - Diretório `output/` dedicado para arquivos de saída
  - Diretório `logs/` para logs da aplicação
  - Suporte a volumes Docker para persistência

- 🛠️ **Scripts de conveniência**
  - `scripts/docker-run.sh` para Linux/macOS/Git Bash
  - `scripts/docker-run.bat` para Windows
  - Perfis predefinidos: basic, performance, light, dev

- 📚 **Documentação expandida**
  - Guia de início rápido (`docs/QUICKSTART.md`)
  - Documentação Docker completa (`docs/DOCKER.md`)
  - README atualizado com seções Docker
  - Exemplos de configuração (`docker-compose.examples.yml`)

### Modificado
- 📝 **Função save_to_json atualizada**
  - Agora salva arquivos no diretório `/app/output` quando executado em Docker
  - Mantém compatibilidade com execução local
  - Criação automática do diretório de saída

- 🏗️ **Estrutura do projeto reorganizada**
  - Adicionado diretório `scripts/` para utilitários
  - Adicionado diretório `docs/` para documentação
  - Arquivos Docker organizados na raiz do projeto

### Técnico
- **Docker Compose Profiles**: Implementação de perfis para diferentes cenários de uso
- **Multi-stage Build**: Otimização da imagem Docker com estágios separados
- **Volume Mounts**: Configuração de volumes para persistência de dados
- **Environment Variables**: Suporte a variáveis de ambiente para configuração
- **Security**: Execução com usuário não-root no container

## [1.0.0] - 2024-XX-XX

### Adicionado
- 🚀 **Implementação inicial do web scraper**
  - Scraping do site Books to Scrape usando Scrapling
  - Suporte a multithreading para performance
  - Paginação automática
  - Sistema de logs com Loguru
  - Barras de progresso com tqdm

- 🔧 **Configuração do projeto**
  - Gerenciamento de dependências com UV
  - Configuração pytest para testes
  - Configuração VS Code para debug
  - Estrutura de projeto organizada

- 📊 **Funcionalidades de extração**
  - Extração de título, preço e disponibilidade dos livros
  - Saída em formato JSON estruturado
  - Tratamento de erros robusto
  - Logging detalhado do processo

### Características Técnicas
- **Python 3.10+**: Versão mínima suportada
- **Scrapling**: Biblioteca moderna para web scraping
- **UV**: Gerenciador de pacotes rápido
- **Concurrent Processing**: Processamento paralelo com ThreadPoolExecutor
- **Structured Logging**: Sistema de logs estruturado com Loguru
