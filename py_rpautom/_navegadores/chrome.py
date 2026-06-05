from requests import Response
from typing import Union


def _coletar_metadata_chromedriver(
    nome_navegador: str,
    webdriver_url: str,
    webdriver_plataforma: str,
    header_request: dict[str, str],
    versao_navegador_sem_minor: list[str],
    proxies: dict[str, str] = None,
    autenticacao: Union[None, list[str, str]] = None,
    divisao_pastas: str = '/',
) -> dict[str, str]:
    from py_rpautom._navegadores.base import _coletar_lista_webdrivers_online

    lista_webdrivers_compativeis = []

    response_http_webdrivers = _coletar_lista_webdrivers_online(
        webdriver_url=webdriver_url,
        header_arg=header_request,
        proxies=proxies,
        autenticacao=autenticacao,
    )

    if response_http_webdrivers.content is None \
    or response_http_webdrivers.content == '':
        raise ValueError(
            (
                'Não foi possível obter a lista de versões '
                'disponíveis do WebDriver. O conteúdo retornado '
                'pelo servidor está vazio ou inválido.'
            )
        )

    lista_webdrivers = _tratar_lista_chromedriver(
        response_http_webdrivers
    )

    if len(lista_webdrivers) == 0:
        raise SystemError(
            (
                'Não foi possível coletar as informações do '
                'webdriver online, verifique sua conexão de rede.'
            )
        )

    for dados_webdriver in lista_webdrivers:
        if (
            dados_webdriver[0]
            .partition(divisao_pastas)[0]
            .__contains__(versao_navegador_sem_minor)
        ) and (
            dados_webdriver[0]
            .partition(divisao_pastas)[-1]
            .__contains__(webdriver_plataforma)
        ):
            lista_webdrivers_compativeis.append(dados_webdriver)

    if lista_webdrivers_compativeis == []:
        raise SystemError(
            f'Nenhum webdriver para o '
            f'navegador {nome_navegador} com a versão '
            f'{versao_navegador_sem_minor}.X está disponível no momento.'
        )

    ultimo_webdriver = lista_webdrivers_compativeis[0]
    nome_arquivo_zip = ultimo_webdriver[0]
    versao = ultimo_webdriver[
        0
    ].partition(divisao_pastas)[0]
    tamanho = ultimo_webdriver[2]
    url_arquivo_zip = ultimo_webdriver[1]

    metadata: dict[str, str] = {
        'nome_arquivo_zip': nome_arquivo_zip,
        'versao': versao,
        'tamanho': tamanho,
        'url_arquivo_zip': url_arquivo_zip,
    }

    return metadata


def _coletar_nome_webdriver_chrome(nome_navegador: str) -> str:
    if not nome_navegador.upper().__contains__('CHROME'):
        raise SystemError(
            f'Navegador {nome_navegador} incorreto para ChromeDriver'
        )

    nome_webdriver = 'chromedriver'        

    return nome_webdriver


def _coletar_metadata_requisicao_chromedriver(
    nome_navegador: str,
) -> dict[str, str]:
    if not nome_navegador.upper().__contains__('CHROME'):
        raise SystemError(
            f'Navegador {nome_navegador} incorreto para ChromeDriver'
        )

    metadata: dict[str, str] = {
        'url': (
            'https://googlechromelabs.github.io/chrome-for-testing/'
            'known-good-versions-with-downloads.json'
        ),
        'headers': {
            'Accept': 'application/xml',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
    }

    return metadata


def _configuracao_silenciosa_chrome() -> tuple[
    tuple[str, ...],
    tuple[str, ...],
]:
    argumentos_silenciosos = (
        '--disable-background-networking',
        '--disable-logging',
        '--log-level=3',
    )
    exclude_switches = ('enable-logging',)

    return argumentos_silenciosos, exclude_switches


def _tratar_lista_chromedriver(
    response_http_webdrivers: Response
) -> list[tuple[str, str, str]]:
    from json import loads


    webdrivers_contents_json = loads(
        response_http_webdrivers.content
    )['versions']

    lista_plataforma_url_webdrivers = []
    for item in webdrivers_contents_json:
        try:
            lista_plataforma_url_webdrivers.append(
                item['downloads']['chromedriver']
            )
        except:
            ...

    if lista_plataforma_url_webdrivers == []:
        raise SystemError(
            'Nenhum webdriver disponível a partir da API JSON.'
        )

    lista_url_webdrivers_json = [
        [item2['url'] for item2 in item]
        for item in lista_plataforma_url_webdrivers
    ]

    lista_url_webdrivers = []
    for item in lista_url_webdrivers_json:
        for item2 in item:
            lista_url_webdrivers.append(item2)

    lista_nome_webdrivers = [
        '/'.join(
            (
                item.split('/')[-3],
                item.split('/')[-1],
            )
        )
        for item in lista_url_webdrivers
    ]

    lista_tamanho_webdrivers = [
        None for item in range(len(lista_nome_webdrivers))
    ]

    lista_webdrivers: list[tuple[str, str, str]] = list(
        zip(
            lista_nome_webdrivers,
            lista_url_webdrivers,
            lista_tamanho_webdrivers,
        )
    )

    return lista_webdrivers
