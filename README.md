
# Repositório de Metadados

## Descrição
Este projeto tem como objetivo coletar e processar metadados de repositórios de código hospedados em plataformas como GitHub e GitLab. Os dados coletados incluem histórico de commits, informações de contribuidores, issues, pull requests, releases e outras informações relevantes. O projeto é ideal para desenvolvedores, analistas e pesquisadores interessados em realizar análises ou auditorias de projetos de código aberto ou privados.

## Funcionalidades
- Extração de detalhes completos dos commits (autor, data, mensagem)
- Coleta de informações de contribuidores e suas estatísticas de contribuição
- Extração de dados sobre issues e pull requests (status, autor, datas)
- Análise de releases e tags
- Suporte para múltiplas plataformas (GitHub, GitLab)
- API simples para integração com outras aplicações
- Exportação de dados em formatos JSON e CSV

## Pré-requisitos
Antes de iniciar, certifique-se de ter as seguintes ferramentas instaladas:
- **Python 3.x**
- **Git**
- Uma conta no GitHub/GitLab (se for necessário autenticação via API)

## Instalação
Siga as etapas abaixo para configurar o projeto localmente:

1. Clone este repositório:
   ```bash
   git clone https://github.com/usuario/repo-metadados.git
   ```

2. Entre na pasta do repositório:
   ```bash
   cd repo-metadados
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso
Para coletar metadados de um repositório GitHub, execute o seguinte comando:

```bash
python obter_metadados.py --repositorio https://github.com/usuario/repositorio.git
```

### Exemplos de Uso:

- Coletar metadados de um repositório específico no GitHub:
  ```bash
  python obter_metadados.py --repositorio https://github.com/exemplo/repo.git
  ```

- Exportar os dados coletados em formato CSV:
  ```bash
  python obter_metadados.py --repositorio https://github.com/exemplo/repo.git --output csv
  ```

## Contribuições
Contribuições são bem-vindas! Se você deseja sugerir melhorias, corrigir bugs ou adicionar novas funcionalidades, siga os passos abaixo:

1. Faça um fork do projeto
2. Crie uma nova branch:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça suas alterações e adicione os commits:
   ```bash
   git commit -m "Minha nova feature"
   ```
4. Envie suas alterações para o GitHub:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request no repositório original

## Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
