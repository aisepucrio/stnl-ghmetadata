import requests
import os
import json
import multiprocessing
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
class GithubAPI:
    """
    Classe para interagir com a API do GitHub.
    """

    def __init__(self):
        """
        Inicializa a classe com o token de autenticação.
        """

        load_dotenv()

        self.token = os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {'Authorization': f'token {self.token}'}

    def search_repositories_filtered(self, query, sort='stars', order='desc', per_page=10, max_repos=10, **filters):
        """
        Pesquisa repositórios no GitHub e aplica filtros dinamicamente até atingir o número máximo desejado.

        :param query: Termo de busca, incluindo filtros (por exemplo, linguagem, número de estrelas, etc.).
        :param sort: Critério de ordenação (stars, forks, etc.).
        :param order: Ordem (asc para crescente, desc para decrescente).
        :param per_page: Número de repositórios a serem buscados por página.
        :param max_repos: Número máximo de repositórios a serem coletados.
        :param filters: Filtros adicionais como fork, created, pushed, author, keywords, organization, etc.
        :return: Lista de repositórios que correspondem à pesquisa ou None em caso de erro.
        """
        url = f'{self.base_url}/search/repositories'

        # Adicionar filtros extras à query de pesquisa
        filter_query = ' '.join([f'{key}:{value}' for key, value in filters.items()])
        query += f" {filter_query}"

        params = {
            'q': query,
            'sort': sort,
            'order': order,
            'per_page': min(per_page, max_repos),  # Garantir que per_page não exceda max_repos
            'page': 1  # Começar pela primeira página
        }

        all_repos = []
        while len(all_repos) < max_repos:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                repos = response.json().get('items', [])
                if not repos:
                    break  # Se não houver mais repositórios, parar
                # Adicionar repositórios à lista, parando quando atingir o máximo desejado
                all_repos.extend(repos)
                params['page'] += 1  # Ir para a próxima página
            else:
                print(f"Erro {response.status_code}: {response.json().get('message')}")
                break

        # Retornar o número exato de repositórios solicitados
        return all_repos[:max_repos] if all_repos else None

    def get_repo_metadata(self, owner, repo):
        """
        Coleta os metadados de um repositório GitHub, incluindo o link, descrição e contribuidores.
        
        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Dicionário com os metadados do repositório ou None em caso de erro.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            metadata = {
                "name": data.get("name"),
                "owner": data.get("owner", {}).get("login"),
                "organization": self.get_repo_organization(owner, repo),
                "stars": data.get("stargazers_count"),
                "watchers": data.get("watchers_count"),
                "forks": data.get("forks_count"),
                "open_issues": data.get("open_issues_count"),
                "default_branch": data.get("default_branch"),
                "description": data.get("description"),
                "html_url": data.get("html_url"),
                "keywords": self.get_repo_keywords(owner, repo),
                "contributors_count": self.get_contributors_from_html(owner, repo),
                "readme": self.get_repo_readme(owner, repo),
                "labels_count": self.get_repo_labels_count(owner, repo)
            }

            # Checa se há algum dado faltando e imprime mensagens apropriadas
            for key, value in metadata.items():
                if value is None:
                    print(f"Informação faltando: {key} no repositório {repo} ({owner})")
            
            return metadata
        else:
            print(f"Erro {response.status_code}: {response.json().get('message')} para o repositório {repo} ({owner})")
            return None
        
    def get_repo_readme(self, owner, repo):
        """
        Obtém o conteúdo do README de um repositório GitHub.
        
        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Conteúdo do README em texto ou None se não encontrado.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/readme'
        headers = {'Authorization': f'token {self.token}', 'Accept': 'application/vnd.github.v3.raw'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text  # Conteúdo do README
        else:
            print(f"README não encontrado para o repositório {repo} ({owner}).")
            return None

    def get_repo_languages(self, owner, repo):
        """
        Coleta as linguagens de programação utilizadas no repositório.

        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Dicionário com as linguagens utilizadas no repositório ou None em caso de erro.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/languages'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Linguagens não encontradas para o repositório {repo} ({owner}).")
            return None

    def get_repo_contributors(self, owner, repo):
        """
        Obtém o número de contribuidores de um repositório GitHub, usando paginação para garantir que
        todos os contribuidores sejam contabilizados. Se o número for muito grande, faz uma estimativa.

        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Dicionário contendo o número de contribuidores e se é uma estimativa.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/contributors'
        page = 1
        per_page = 100  # O máximo permitido pela API do GitHub
        total_contributors = 0
        max_pages = 10  # Número máximo de páginas a percorrer antes de fazer uma estimativa
        estimation_threshold = 400  # Número de contribuidores após o qual estimamos
        is_estimated = False  # Para rastrear se estamos estimando o valor

        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        while True:
            response = requests.get(url, headers=headers, params={'page': page, 'per_page': per_page})
            if response.status_code == 200:
                contributors = response.json()
                if not contributors:  # Se não houver mais contribuidores, parar
                    break
                total_contributors += len(contributors)
                page += 1  # Ir para a próxima página

                if page > max_pages or total_contributors > estimation_threshold:
                    estimated_contributors = total_contributors / (page - 1) * page
                    is_estimated = True
                    print(f"Estimando o número de contribuidores para o repositório {repo} ({owner}).")
                    return {
                        "contributors_count": int(estimated_contributors),
                        "estimated": is_estimated
                    }
            elif response.status_code == 403:
                print(f"Limite de requisições da API atingido para o repositório {repo} ({owner}).")
                return None
            else:
                print(f"Contribuidores não encontrados para o repositório {repo} ({owner}).")
                return None

        return {
            "contributors_count": total_contributors,
            "estimated": is_estimated
        }
    
    def get_contributors_from_html(self, owner, repo):
        """
        Obtém o número de contribuidores de um repositório GitHub através da página HTML do repositório.
        
        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Número de contribuidores ou None se não encontrado.
        """
        url = f'https://github.com/{owner}/{repo}'
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            # Encontra o elemento com a classe "Counter ml-1" que contém o número de contribuidores
            contributors_element = soup.find('a', {'href': f'/{owner}/{repo}/graphs/contributors'})
            
            if not contributors_element:
                print(f"Contribuidores não encontrados para o repositório {repo} ({owner}).")
                return None

            span_element = contributors_element.find('span', class_='Counter ml-1')
            if span_element and 'title' in span_element.attrs:
                contributors_text = span_element['title']  # Pega o valor do atributo title
                try:
                    return int(contributors_text.replace(',', ''))  # Remove as vírgulas e converte para int
                except ValueError:
                    print(f"Erro ao converter o número de contribuidores para o repositório {repo} ({owner}).")
                    return None
            else:
                print(f"Elemento <span> de contribuidores não encontrado para o repositório {repo} ({owner}).")
                return None
            
        else:
            print(f"Erro ao acessar a página HTML do repositório {repo} ({owner}). Status code: {response.status_code}")
            return None

    def get_repo_organization(self, owner, repo):
        """
        Obtém a organização do repositório, se existir.

        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Nome da organização ou None se não for um repositório de organização.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('organization'):
                return data['organization'].get('login')
        return None
    
    def get_repo_keywords(self, owner, repo):
        """
        Obtém as palavras-chave do repositório.

        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Lista de palavras-chave ou None se não for um repositório de organização.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/topics'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200: 
            return response.json().get('names', [])
        else:
            print(f"Palavras-chave não encontradas para o repositório {repo} ({owner}).")
            return None
    
    def get_repo_labels_count(self, owner, repo):
        """
        Obtém a quantidade de labels de um repositório GitHub.
        
        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Quantidade de labels ou None se não encontrado.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/labels'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return len(response.json())  # Contagem de labels
        else:
            print(f"Labels não encontrados para o repositório {repo} ({owner}).")
            return None

def save_metadata_to_json(metadata, filename='output.json'):
    """
    Salva os metadados coletados em um arquivo JSON.

    :param metadata: Dicionário contendo os metadados do repositório.
    :param filename: Nome do arquivo onde os metadados serão salvos.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        print(f'Metadados salvos em {filename}')
    except IOError as e:
        print(f'Erro ao salvar os metadados: {e}')


def format_languages(languages):
    """
    Formata a lista de linguagens com o total de bytes e percentuais.
    
    :param languages: Dicionário contendo as linguagens e seus bytes.
    :return: Lista de linguagens com bytes e percentual de uso.
    """
    if not languages:
        return None

    total_bytes = sum(languages.values())
    formatted_languages = [
        {
            "language": lang,
            "bytes": bytes_used,
            "percentage": round((bytes_used / total_bytes) * 100, 2)
        }
        for lang, bytes_used in sorted(languages.items(), key=lambda x: x[1], reverse=True)
    ]
    return {
        "total_bytes": total_bytes,
        "languages": formatted_languages,
        "description": "The 'bytes' field represents the total number of bytes of code written in this language, and 'percentage' shows its proportion relative to the total."
    }

def load_config(config_file='configs.json'):
    """
    Carrega as configurações do arquivo JSON.

    :param config_file: Caminho para o arquivo de configuração JSON.
    :return: Dicionário com as configurações carregadas.
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo {config_file} não encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo {config_file}.")
        return None


def process_repo(api, repo, min_contributors=None):
    """
    Processa o repositório para coletar metadados e organiza as linguagens, incluindo um filtro opcional para número mínimo de contribuidores.
    
    :param api: Instância da API do GitHub.
    :param repo: Repositório a ser processado.
    :param min_contributors: Número mínimo de contribuidores para considerar o repositório.
    :return: Dicionário contendo os dados organizados do repositório ou None se não cumprir os critérios.
    """
    owner = repo["owner"]["login"]
    repo_name = repo["name"]

    # Coleta os principais metadados do repositório
    metadata = api.get_repo_metadata(owner, repo_name)

    # Coleta as linguagens utilizadas no repositório
    languages = api.get_repo_languages(owner, repo_name)

    # Verifica se o repositório cumpre o requisito mínimo de contribuidores
    contributors_count = metadata["contributors_count"]
    if contributors_count is None or (min_contributors is not None and contributors_count < min_contributors):
        print(f"Repositório {repo_name} ({owner}) ignorado: número de contribuidores ({contributors_count}) é menor que {min_contributors}.")
        return None

    # Organiza os dados de forma mais clara
    organized_data = {
        "name": metadata["name"],
        "owner": metadata["owner"],
        "organization": metadata["organization"],
        "stars": metadata["stars"],
        "watchers": metadata["watchers"],
        "forks": metadata["forks"],
        "open_issues": metadata["open_issues"],
        "default_branch": metadata["default_branch"],
        "description": metadata["description"] if metadata["description"] else "Descrição não disponível",
        "html_url": metadata["html_url"] if metadata["html_url"] else "Link não disponível",
        "contributors_count": contributors_count,
        "keywords": metadata["keywords"],
        "languages_info": format_languages(languages) if languages else "Linguagens não disponíveis",
        "readme": metadata["readme"] if metadata["readme"] else "README não disponível",
        "labels_count": metadata["labels_count"] if metadata["labels_count"] else "Labels não disponíveis"
    }

    return organized_data

def main():
    """
    Função principal para coletar e salvar metadados de repositórios do GitHub com multithreading.
    """
    # Carrega as configurações do arquivo JSON
    config = load_config()
    if not config:
        return

    # Defina os filtros da pesquisa a partir do arquivo de configuração
    language = config.get("language", "python")
    stars = config.get("stars", ">=500")
    fork = config.get("fork", "true")
    created = config.get("created", None)
    pushed = config.get("pushed", None)
    size = config.get("size", None)
    user = config.get("author", None)
    min_contributors = config.get("min_contributors", 1)
    keywords = config.get("keywords", None)
    organization = config.get("organization", None)

    # Montar a query básica de pesquisa
    query = f"language:{language} stars:{stars}"
    
    if user:
        query += f" user:{user}"
    
    # Adiciona mais filtros à busca
    additional_filters = {}
    if fork:
        additional_filters["fork"] = fork
    if created:
        additional_filters["created"] = created
    if pushed:
        additional_filters["pushed"] = pushed
    if size:
        additional_filters["size"] = size
    if organization:
        query += f" org:{organization}"

    # Se keywords for uma lista, adicionar todas elas
    if keywords:
        if isinstance(keywords, list):
            keywords_query = ' '.join([f"topic:{keyword}" for keyword in keywords])
            query += f" {keywords_query}"
        else:
            query += f" topic:{keywords}"

    # Filtros de ordenação
    number_of_repositories = config.get("number_of_repositories", 20)
    sort = config.get("sort", "stars")
    order = config.get("order", "desc")

    # Define o número de threads a serem utilizadas
    cpu_count = multiprocessing.cpu_count()
    num_threads = config.get("threads", cpu_count // 2)

    # Cria uma instância da API do GitHub
    api = GithubAPI()

    # Busca repositórios de acordo com os filtros e limite de número de repositórios
    repositories = api.search_repositories_filtered(
        query=query, 
        sort=sort, 
        order=order, 
        per_page=100,  # Usar um valor alto para garantir que mais resultados sejam obtidos por página
        max_repos=number_of_repositories, 
        **additional_filters
    )

    if not repositories:
        print("Nenhum repositório encontrado.")
        return

    all_metadata = []

    # Usa ThreadPoolExecutor para executar em múltiplas threads
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(process_repo, api, repo, min_contributors): repo for repo in repositories}

        for future in as_completed(futures):
            try:
                data = future.result()
                if data:
                    all_metadata.append(data)
            except Exception as e:
                repo = futures[future]
                print(f"Erro ao processar o repositório {repo['name']}: {e}")

    save_metadata_to_json(all_metadata)

print("Iniciando a coleta de repositórios do GitHub com filtros...")
main()