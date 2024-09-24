
# Coletor de Metadados de Repositórios GitHub

Este projeto recupera metadados de repositórios do GitHub usando a API do GitHub. O script permite que você pesquise repositórios com critérios específicos, colete metadados e salve os resultados em um arquivo JSON.

## Link do Repositório

Você pode encontrar o repositório no seguinte link:
[GitHub Repository](https://github.com/aisepucrio/stnl-ghmetadata)

## Visão Geral do Script

O script principal utilizado para executar a coleta de metadados é o `collector.py`.

## Exemplos de Metadados Coletados

O script coleta os seguintes tipos de metadados de cada repositório:

- **Nome** do repositório
- **Proprietário** (usuário ou organização)
- **Estrelas** (quantidade de estrelas)
- **Forks** (quantidade de forks)
- **Contribuidores** (quantidade de pessoas que contribuíram)
- **Linguagens** utilizadas no repositório e seus percentuais
- **Branch padrão** (branch principal do repositório)
- **Descrição** do repositório (se disponível)
- **Data do último push** (última vez que houve um commit no repositório)
- **Link** para o repositório no GitHub

## Funcionalidades

- Pesquisa repositórios do GitHub por linguagem, estrelas, data de criação e mais.
- Recupera metadados como nome do repositório, estrelas, forks, contribuidores e linguagens usadas.
- Salva os metadados coletados em um arquivo JSON.

## Filtros Suportados

O script suporta os seguintes filtros principais ao pesquisar por repositórios:

1. **Linguagem**: Filtra pela linguagem de programação (por exemplo, `language:python`).
2. **Estrelas**: Filtra pelo número de estrelas que o repositório possui (por exemplo, `stars:>500`).
3. **Forks**: Filtra pelo número de forks (por exemplo, `forks:>50`).
4. **Data de Criação**: Filtra pela data de criação do repositório (por exemplo, `created:>2020-01-01`).
5. **Último Push**: Filtra pela data do último push (por exemplo, `pushed:>2023-01-01`).
6. **Tamanho**: Filtra pelo tamanho do repositório em KB (por exemplo, `size:100..500`).
7. **Usuário**: Filtra pelo proprietário do repositório (por exemplo, `user:torvalds`).
8. **Arquivado**: Filtra por repositórios arquivados (por exemplo, `archived:true`).

## Uso

1. Clone o repositório do GitHub:

   ```
   git clone https://github.com/aisepucrio/stnl-ghmetadata.git
   ```

2. Instale as dependências necessárias:

   ```
   pip install -r requirements.txt
   ```

3. Configure os filtros editando o arquivo `configs.json` para definir os parâmetros desejados.

4. Execute o script:

   ```
   python collector.py
   ```

5. O script gerará um arquivo JSON contendo os metadados dos repositórios que correspondem aos filtros aplicados.

## Licença

Este projeto é licenciado sob a Licença MIT.
