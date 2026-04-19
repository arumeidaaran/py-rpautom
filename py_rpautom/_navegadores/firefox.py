from typing import Union

from requests import Response


def _coletar_metadata_geckodriver(
    nome_navegador: str,
    webdriver_url: str,
    webdriver_plataforma: str,
    header_request: dict[str, str],
    versao_navegador_sem_minor: list[str],
    proxies: dict[str, str] = None,
    autenticacao: Union[None, list] = None,
) -> dict[str, str]:
    from re import search

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

    lista_webdrivers = _tratar_lista_geckodriver(response_http_webdrivers)

    if len(lista_webdrivers) == 0:
        raise RuntimeError(
            'Não encontrado versões para o webdriver do Firefox'
        )

    # Extrai a versão mais recente do geckodriver compatível com o
    # Firefox local a partir da tabela de suporte (Support.md).
    versao_firefox_major = int(
        str(versao_navegador_sem_minor).partition('.')[0]
    )

    # A tabela normalmente vem ordenada do mais novo para o mais antigo,
    # então o primeiro match já é a versão mais recente compatível.
    versao_correspondente = None
    for gecko_versao, min_major, max_major in lista_webdrivers:
        if (
            versao_firefox_major >= min_major
            and versao_firefox_major <= max_major
        ):
            versao_correspondente = gecko_versao
            break

    if versao_correspondente is None:
        # Firefox mais novo do que a tabela cobre: use o mais recente.
        maior_max = max([item[2] for item in lista_webdrivers])
        if versao_firefox_major > maior_max:
            versao_correspondente = lista_webdrivers[0][0]
        else:
            versao_correspondente = lista_webdrivers[-1][0]

    nome_arquivo_zip = (
        f'geckodriver-v{versao_correspondente}-{webdriver_plataforma}.zip'
    )
    url_arquivo_zip = (
        'https://github.com/mozilla/geckodriver/releases/download/'
        f'v{versao_correspondente}/{nome_arquivo_zip}'
    )

    lista_webdrivers_compativeis.append(
        (nome_arquivo_zip, url_arquivo_zip, 0)
    )

    if lista_webdrivers_compativeis == []:
        versao_navegador = '.'.join(
            [str(item) for item in versao_navegador]
        )
        raise SystemError(
            f'Nenhum webdriver para o '
            f'navegador {nome_navegador} com a versão '
            f'{versao_navegador} está disponível no momento.'
        )

    ultimo_webdriver = lista_webdrivers_compativeis[0]
    nome_arquivo_zip = ultimo_webdriver[0]

    versao = search(
        '(v)[0-9].*-',
        nome_arquivo_zip
    )[0].replace('v', '').replace('-', '')

    url_arquivo_zip = ultimo_webdriver[1]
    tamanho = ultimo_webdriver[2]

    metadata: dict[str, str] = {
        'nome_arquivo_zip': nome_arquivo_zip,
        'versao': versao,
        'tamanho': tamanho,
        'url_arquivo_zip': url_arquivo_zip,
    }

    return metadata


def _coletar_nome_webdriver_firefox(nome_navegador: str) -> str:
    if not nome_navegador.upper().__contains__('FIREFOX'):
        raise SystemError(
            f'Navegador {nome_navegador} incorreto para GeckoDriver'
        )

    nome_webdriver = 'geckodriver'        

    return nome_webdriver


def _coletar_metadata_requisicao_geckodriver(
    nome_navegador: str
) -> dict[str, str]:
    if not nome_navegador.upper().__contains__('FIREFOX'):
        raise SystemError(
            f'Navegador {nome_navegador} incorreto para GeckoDriver'
        )

    metadata: dict[str, str] = {
        'url': (
            'https://searchfox.org/firefox-main/'
            'source/testing/geckodriver/doc/Support.md'
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


def _tratar_lista_geckodriver(
    response_http_webdrivers: Response
) -> list[str]:
    from re import DOTALL, IGNORECASE, search, sub

    from requests_html import HTML


    lista_webdrivers = []

    html_string = response_http_webdrivers.content.decode() # type: ignore
    html_string = html_string.replace('&lt;', '<')
    html_string = sub(
        r'<style[^>]*>.*?</style>',
        '',
        html_string,
        flags=DOTALL | IGNORECASE
    )
    html_string = sub(
        r'<code[^>]*class="source-line"[^>]*>',
        '',
        html_string,
        flags=IGNORECASE
    )
    html_string = html_string.replace('</code>', '')
    html_string = html_string.replace(
        '<div role="cell"><div class="cov-strip cov-no-data"></div></div>',
        ''
    )
    html_string = sub(
        r'</div>\s*<div role="row" id="line-\d+"[^>]*class="source-line-with-number">',
        '',
        html_string,
        flags=IGNORECASE
    )
    html_string = sub(
        r'<div role="cell"><div class="blame-strip [^"]+"[^>]*data-blame="[^"]+"[^>]*aria-label="[^"]*hash[^"]*"[^>]*aria-expanded="false"></div></div>',
        '',
        html_string,
        flags=IGNORECASE
    )
    html_string = html_string.replace(
        '<div role="cell" class="line-number" data-line-number="18"></div>',
        ''
    )

    html_string = sub(
        r'<div role="cell" class="line-number" data-line-number="\d+"></div>',
        '',
        html_string,
        flags=IGNORECASE
    )
    # Repara fechamento da tag <th> imediatamente
    #   após seu conteúdo se tag de fechamento estiver faltando 
    html_string = sub(
        r'(<th\b[^>]*>)([^<\n\r]+)(?=(?:\s*<(?:th|td|tr|/tr|/thead|/tbody|/table)))',
        r'\1\2</th>',
        html_string,
        flags=IGNORECASE
    )

    # Repara fechamento da tag <td> imediatamente após seu
    #   conteúdo se tag de fechamento estiver faltando 
    html_string = sub(
        r'(<td\b[^>]*>)([^<\n\r]+)(?=(?:\s*<(?:td|th|tr|/tr|/tbody|/table)))',
        r'\1\2</td>',
        html_string,
        flags=IGNORECASE
    )

    # Repara fechamento da tag <tr> imediatamente após seu conteúdo
    #   se tag de fechamento estiver faltando 
    html_string = sub(
        r'(<tr\b[^>]*>.*?(?:</td>|</th>))(?!\s*</tr>)(?=\s*<(?:tr|/tbody|/thead|/table|$))',
        r'\1</tr>',
        html_string,
        flags=IGNORECASE | DOTALL
    )

    # Fecha todas as tags de células abertas únicas restantes que são
    #   seguidas por uma nova linha/espaço em branco e, em seguida,
    #   uma nova linha/tabela
    html_string = sub(
        r'(<(th|td)\b[^>]*>)([^<\n\r]+)(?=\s*(?:</thead>|</tbody>|</table>))',
        r'\1\3</\2>',
        html_string,
        flags=IGNORECASE
    )

    html_string = sub(
        r'\n\s.\n?',
        '',
        html_string,
        flags=DOTALL
    )
    html_string = sub(r'\s*\n\s*', '', html_string)

    root = HTML(html=html_string)
    tabela_webdrivers = root.find('table')
    tabela_webdrivers = tabela_webdrivers[0]

    total_versoes = tabela_webdrivers.xpath('//table/tr').__len__() 
    if total_versoes == 0:
        raise RuntimeError(
            'Não encontrado versões para o navegador Firefox'
        )    

    # A HTML retornada pelo Searchfox nem sempre forma uma tabela
    # "limpa" (TR/TD). Coletamos o texto em ordem e inferimos os blocos:
    #   geckodriver, python, min_firefox, max_firefox
    tokens = [
        str(item).strip()
        for item in tabela_webdrivers.xpath('.//text()')
        if str(item).strip() != ''
    ]

    versoes_vistas = set()
    for idx in range(0, len(tokens) - 3):
        match_gecko = search(
            r'(?<!\d)(\d+\.\d+\.\d+)(?!\d)',
            tokens[idx]
        )
        if match_gecko is None:
            continue

        gecko_versao = match_gecko.group(1)
        if gecko_versao in versoes_vistas:
            continue

        min_texto = tokens[idx + 2]
        max_texto = tokens[idx + 3]
        min_major = _parse_major_firefox(min_texto)
        max_major = _parse_major_firefox(max_texto)

        lista_webdrivers.append((gecko_versao, min_major, max_major))
        versoes_vistas.add(gecko_versao)

    return lista_webdrivers


def _parse_major_firefox(valor: str) -> int:
    from re import search


    texto = str(valor or '').lower()

    min_default=0
    max_default=9999
    default = None

    if 'n/a' in texto:
        default = min_default
    else:
        match = search(r'(?<![\d.])(\d{2,3})(?![\d.])', texto)

        if match is None:
            default = max_default
    
    if default is None:
        default = int(match.group(1))

    return default
