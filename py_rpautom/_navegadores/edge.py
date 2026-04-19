from typing import Union

from requests import Response


def _coletar_nome_webdriver_edge(nome_navegador: str) -> str:
    if not nome_navegador.upper().__contains__('EDGE'):
        raise SystemError(
            f'Navegador {nome_navegador} incorreto para EdgeDriver'
        )

    nome_webdriver = 'edgedriver'        

    return nome_webdriver


def _coletar_metadata_edgedriver(
    webdriver_url: str,
    header_request: dict[str, str],
    proxies: dict[str, str] = None,
    autenticacao: Union[None, list] = None,
) -> dict[str, str]:
    from py_rpautom._navegadores.base import _coletar_lista_webdrivers_online

    response_http_webdrivers = _coletar_lista_webdrivers_online(
        webdriver_url=webdriver_url,
        header_arg=header_request,
        proxies=proxies,
        autenticacao=autenticacao,
        metodo='HEAD',
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

    nome_arquivo_zip = webdriver_url.split('/')[-1]
    versao = webdriver_url.split('/')[-2]
    tamanho = response_http_webdrivers.headers['Content-Length']
    url_arquivo_zip = webdriver_url

    metadata: dict[str, str] = {
        'nome_arquivo_zip': nome_arquivo_zip,
        'versao': versao,
        'tamanho': tamanho,
        'url_arquivo_zip': url_arquivo_zip,
    }

    return metadata


def _coletar_metadata_requisicao_edgedriver(
    nome_navegador: str,
    versao_navegador: str,
    webdriver_plataforma: str,
) -> dict[str, str]:
    if not nome_navegador.upper().__contains__('EDGE'):
        raise SystemError(
            f'Navegador {nome_navegador} incorreto para EdgeDriver'
        )

    metadata: dict[str, str] = {
        'url': (
            f'https://msedgedriver.microsoft.com/{versao_navegador}/'
            f'edgedriver_{webdriver_plataforma}.zip'
        ),
        'headers': {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            'Cache-Control': 'max-age=0',
            "User-Agent": "Mozilla/5.0"
        }
    }

    return metadata


def _tratar_lista_edgedriver(
    response_http_webdrivers: Response
) -> list[tuple[str, str, str]]:
    from xml.etree.ElementTree import fromstring


    root = fromstring(response_http_webdrivers.content)

    tag_nome_webdriver = '*//Name'
    tag_url_webdriver = '*//Url'
    tag_tamanho_webdriver = '*//Size'

    lista_nome_webdrivers = [
        item.text for item in root.findall(tag_nome_webdriver)
    ]

    if tag_url_webdriver is None:
        lista_url_webdrivers = [
            None for item in range(len(lista_nome_webdrivers))
        ]
    else:
        lista_url_webdrivers = [
            item.text for item in root.findall(tag_url_webdriver)
        ]

    if tag_tamanho_webdriver is None:
        lista_tamanho_webdrivers = [
            None for item in range(len(lista_nome_webdrivers))
        ]
    else:
        lista_tamanho_webdrivers = [
            item.text for item in root.findall(tag_tamanho_webdriver)
        ]

    lista_webdrivers: list[tuple[str, str, str]] = list(
        zip(
            lista_nome_webdrivers,
            lista_url_webdrivers,
            lista_tamanho_webdrivers,
        )
    )

    return lista_webdrivers
