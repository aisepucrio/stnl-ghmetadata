import requests
import os
import json
from dotenv import load_dotenv

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

    def search_repositories(self, query, sort='stars', order='desc', per_page=10):
        """
        Pesquisa repositórios no GitHub com base em filtros.

        :param query: Termo de busca, incluindo filtros (por exemplo, linguagem, número de estrelas, etc.).
        :param sort: Critério de ordenação (stars, forks, etc.).
        :param order: Ordem (asc para crescente, desc para decrescente).
        :param per_page: Número de repositórios a serem retornados.
        :return: Lista de repositórios que correspondem à pesquisa ou None em caso de erro.
        """
        url = f'{self.base_url}/search/repositories'
        params = {
            'q': query,
            'sort': sort,
            'order': order,
            'per_page': per_page
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print(f"Erro {response.status_code}: {response.json().get('message')}")
            return None

    def get_repo_metadata(self, owner, repo):
        """
        Coleta os metadados de um repositório GitHub.
        
        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Dicionário com os metadados do repositório ou None em caso de erro.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data.get("name"),
                "owner": data.get("owner", {}).get("login"),
                "stars": data.get("stargazers_count"),
                "watchers": data.get("watchers_count"),
                "forks": data.get("forks_count"),
                "open_issues": data.get("open_issues_count"),
                "default_branch": data.get("default_branch")
            }
        else:
            print(f"Erro {response.status_code}: {response.json().get('message')}")
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
            print(f"Erro {response.status_code}: {response.json().get('message')}")
            return None


def save_metadata_to_json(metadata, filename='output.json'):
    """
    Salva os metadados coletados em um arquivo JSON.

    :param metadata: Dicionário contendo os metadados do repositório.
    :param filename: Nome do arquivo onde os metadados serão salvos.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f'Metadados salvos em {filename}')
    except IOError as e:
        print(f'Erro ao salvar os metadados: {e}')


def format_languages(languages):
    """
    Formata a lista de linguagens com o total de bytes e percentuais.
    
    :param languages: Dicionário contendo as linguagens e seus bytes.
    :return: Lista de linguagens com bytes e percentual de uso.
    """
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


def main():
    """
    Função principal para coletar e salvar metadados de repositórios do GitHub.
    """
    # Carrega as configurações do arquivo JSON
    config = load_config()
    if not config:
        return

    # Defina os filtros da pesquisa a partir do arquivo de configuração
    language = config.get("language", "python")
    stars = config.get("stars", ">=500")
    query = f"language:{language} stars:{stars}"
    per_page = config.get("per_page", 5)
    sort = config.get("sort", "stars")
    order = config.get("order", "desc")

    # Cria uma instância da API do GitHub
    api = GithubAPI()
    
    # Busca repositórios de acordo com os filtros
    repositories = api.search_repositories(query=query, sort=sort, order=order, per_page=per_page)

    if not repositories:
        print("Nenhum repositório encontrado.")
        return

    # Itera sobre os repositórios encontrados e coleta os metadados
    all_metadata = []
    for repo in repositories:
        owner = repo["owner"]["login"]
        repo_name = repo["name"]

        # Coleta os principais metadados do repositório
        metadata = api.get_repo_metadata(owner, repo_name)

        # Coleta as linguagens utilizadas no repositório
        languages = api.get_repo_languages(owner, repo_name)

        # Organiza os dados de forma mais clara
        organized_data = {
            "name": metadata["name"],
            "owner": metadata["owner"],
            "stars": metadata["stars"],
            "watchers": metadata["watchers"],
            "forks": metadata["forks"],
            "open_issues": metadata["open_issues"],
            "default_branch": metadata["default_branch"],
            "languages_info": format_languages(languages) if languages else None
        }

        all_metadata.append(organized_data)

    # Salva os metadados organizados em um arquivo JSON
    save_metadata_to_json(all_metadata)


print("Iniciando a coleta de repositórios do GitHub com filtros...")
main()
