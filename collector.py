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
        :param token: Token de autenticação do GitHub.
        """

        load_dotenv()

        self.token = os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {'Authorization': f'token {self.token}'}

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

    def get_contributors_count(self, owner, repo):
        """
        Coleta o número de colaboradores de um repositório GitHub. 
        Retorna apenas o número, já que repositórios grandes podem gerar erro ao tentar listar todos.
        
        Se não for possível obter o número exato, retorna uma estimativa (>5000, etc.).
        
        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Número de colaboradores ou uma estimativa em caso de erro.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/contributors?per_page=1'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            contributors_count = response.headers.get('Link', None)
            if contributors_count and 'rel="last"' in contributors_count:
                last_page_url = contributors_count.split('rel="last"')[0].split('<')[-1].split('>')[0]
                last_page = int(last_page_url.split('page=')[-1])
                return last_page
            return 1
        elif response.status_code == 403:
            print("Número de colaboradores muito grande para ser listado via API.")
            # Retorna uma estimativa quando não for possível obter o número exato
            return ">5000"  # Estimativa genérica para grandes repositórios
        else:
            print(f"Erro {response.status_code}: {response.json().get('message')}")
        return None

    def get_repo_commits(self, owner, repo):
        """
        Coleta o número de commits do repositório.
        
        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Número de commits ou None em caso de erro.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/commits'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return len(response.json())
        else:
            print(f"Erro {response.status_code}: {response.json().get('message')}")
            return None

    def get_repo_pulls(self, owner, repo):
        """
        Coleta o número de pull requests abertos.
        
        :param owner: Nome do dono do repositório (usuário ou organização).
        :param repo: Nome do repositório.
        :return: Número de pull requests ou None em caso de erro.
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/pulls'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return len(response.json())
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


def main():
    """
    Função principal para coletar e salvar metadados de um repositório do GitHub.
    """
    owner = "torvalds"  # Exemplo: "torvalds"
    repo = "linux"  # Exemplo: "linux"

    # Cria uma instância da API do GitHub
    api = GithubAPI()
    
    # Coleta os principais metadados do repositório
    metadata = api.get_repo_metadata(owner, repo)

    # Coleta as linguagens utilizadas no repositório
    languages = api.get_repo_languages(owner, repo)

    # Coleta o número de colaboradores
    contributors_count = api.get_contributors_count(owner, repo)

    # Coleta o número de commits
    commits_count = api.get_repo_commits(owner, repo)

    # Coleta o número de pull requests
    pulls_count = api.get_repo_pulls(owner, repo)

    # Organiza os dados de forma mais clara
    organized_data = {
        "name": metadata["name"],
        "owner": metadata["owner"],
        "stars": metadata["stars"],
        "watchers": metadata["watchers"],
        "forks": metadata["forks"],
        "open_issues": metadata["open_issues"],
        "default_branch": metadata["default_branch"],
        "commits_count": commits_count,
        "pull_requests_count": pulls_count,
        "contributors_count": contributors_count,
        "languages_info": format_languages(languages) if languages else None
    }

    # Salva os metadados organizados em um arquivo JSON
    save_metadata_to_json(organized_data)


print("Iniciando a coleta de metadados do repositório...")
main()
