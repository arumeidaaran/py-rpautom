from collections import namedtuple
from typing import Union

from py_rpautom._navegadores.chrome import (
    _coletar_metadata_chromedriver,
    _coletar_metadata_requisicao_chromedriver,
    _coletar_nome_webdriver_chrome,
)
from py_rpautom._navegadores.edge import (
    _coletar_metadata_edgedriver,
    _coletar_metadata_requisicao_edgedriver,
    _coletar_nome_webdriver_edge,
)
from py_rpautom._navegadores.firefox import (
    _coletar_metadata_geckodriver,
    _coletar_metadata_requisicao_geckodriver,
    _coletar_nome_webdriver_firefox,
)
from py_rpautom import python_utils
from requests import Response


_navegadores_permitodos = ['CHROME', 'EDGE', 'FIREFOX']
_webdriver_info = namedtuple(
    'webdriver_info',
    [
        'url',
        'nome',
        'caminho',
        'plataforma',
        'header_request',
        'versao',
        'caminho_arquivo_zip',
        'nome_arquivo_zip',
        'arquivo_zip',
        'url_arquivo_zip',
        'caminho_arquivo_executavel',
        'tamanho',
    ],
)


def _adicionar_extras(
    options_webdriver,
    argumento,
    extensao,
    argumento_experimental,
    capacidade,
):
    if argumento is not None and len(argumento) > 0:
        for item in argumento:
            options_webdriver.add_argument(item)

    if extensao is not None and len(extensao) > 0:
        for item in extensao:
            options_webdriver.add_extension(item)

    if (
        argumento_experimental is not None
        and len(argumento_experimental) > 0
    ):
        for item in argumento_experimental:
            options_webdriver.add_experimental_option(*item)

    if capacidade is not None and len(capacidade) > 0:
        for item in capacidade:
            options_webdriver.set_capability(item[0], item[1])
        options_webdriver.to_capabilities()

    return options_webdriver


def _coletar_caminho_padrao_navegador(
    nome_navegador: str,
) -> str:
    if nome_navegador.upper().__contains__('CHROME'):
        caminho_navegador = (
            'C:/Program Files/Google/Chrome/Application/chrome.exe'
        )
    elif nome_navegador.upper().__contains__('EDGE'):
        caminho_navegador = (
            'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
        )
    elif nome_navegador.upper().__contains__('FIREFOX'):
        caminho_navegador = 'C:/Program Files/Mozilla Firefox/firefox.exe'
    else:
        raise SystemError(
            f' {nome_navegador} não disponível. Escolha uma dessas '
            'opções: Chrome, Edge, Firefox.'
        )

    return caminho_navegador


def _coletar_lista_webdrivers_locais(
    caminho_webdriver: str,
    versao_webdriver: str,
    plataforma_sistema: str,
):
    lista_webdrivers_locais = python_utils.retornar_arquivos_em_pasta(
        caminho=caminho_webdriver,
        filtro=f'{versao_webdriver}\\*{plataforma_sistema}*.zip',
    )

    return lista_webdrivers_locais


def _coletar_lista_webdrivers_online(
    webdriver_url: str,
    header_arg: str,
    autenticacao: Union[None, list] = None,
    proxies: dict[str, str] = None,
    metodo: str = 'GET',
) -> Response:
    from os import environ

    from requests.exceptions import SSLError

    from py_rpautom.web_utils import requisitar_url


    global wdm_ssl_verify

    wdm_ssl_verify = python_utils.ler_variavel_ambiente(
        nome_variavel='WDM_SSL_VERIFY',
        variavel_sistema=True,
    )

    status = 0
    contagem = 0
    tempo_limite = 1

    resposta = None
    if wdm_ssl_verify is None:
        environ['WDM_SSL_VERIFY'] = '1'
        wdm_ssl_verify = '1'

    while not status == 200 and contagem < 60:
        verificacao_ssl = (environ['WDM_SSL_VERIFY']).lower() in [
            '1',
            1,
            'true',
            True,
        ]

        try:
            resposta = requisitar_url(
                webdriver_url,
                stream=True,
                verificacao_ssl=verificacao_ssl,
                autenticacao=autenticacao,
                header_arg=header_arg,
                tempo_limite=tempo_limite,
                proxies=proxies,
                metodo=metodo,
            )
            status = resposta.status_code

            if status in range(200, 300):
                break
            else:
                resposta = requisitar_url(
                    webdriver_url,
                    stream=True,
                    verificacao_ssl=verificacao_ssl,
                    header_arg=header_arg,
                    tempo_limite=tempo_limite,
                )
                status = resposta.status_code
        except SSLError as erro:
            environ['WDM_SSL_VERIFY'] = '0'
            wdm_ssl_verify = '0'
        except Exception as erro:
            ...

        contagem = contagem + 1

    if (
        (not resposta.status_code)
        or (not resposta.status_code in range(200, 300))
    ):
        raise SystemError(
            f'Falha ao acessar a url {webdriver_url}. Revise os dados e tente novamente.'
        )

    return resposta


def _coletar_metadata_webdriver_local(
    nome_navegador: str,
    caminho_base_webdriver: str,
    versao_navegador: list[str],
    divisao_pastas: str = '/'
) -> dict[str, str]:
    if not nome_navegador.upper() in _navegadores_permitodos:
        raise SystemError(
            (
                'Não há WebDriver disponível para o navegador '
                f'"{nome_navegador}". '
                'Os navegadores suportados são: Chrome, Edge e Firefox.'
            )
        )

    metadata_webdriver_local: dict[str, str] = dict()

    webdriver_url = None
    webdriver_nome = None
    webdriver_caminho = None
    webdriver_plataforma = _coletar_plataforma_webdriver()
    webdriver_header_request = None
    webdriver_versao = None
    webdriver_caminho_arquivo_zip = None
    webdriver_nome_arquivo_zip = None
    webdriver_arquivo_zip = None
    webdriver_url_arquivo_zip = None
    webdriver_caminho_arquivo_executavel = None
    webdriver_tamanho = None

    if nome_navegador.upper().__contains__('CHROME'):
        webdriver_nome = _coletar_nome_webdriver_chrome(nome_navegador)
    elif nome_navegador.upper().__contains__('EDGE'):
        webdriver_nome = _coletar_nome_webdriver_edge(nome_navegador)
    elif nome_navegador.upper().__contains__('FIREFOX'):
        webdriver_nome = _coletar_nome_webdriver_firefox(nome_navegador)

    webdriver_caminho = _coletar_caminho_webdriver(
        caminho_base_webdriver = caminho_base_webdriver,
        nome_webdriver=webdriver_nome,
    )

    versao_navegador_str = _coletar_versao_navegador(
        versao_navegador = versao_navegador,
    )

    lista_webdrivers_locais = _coletar_lista_webdrivers_locais(
        caminho_webdriver = webdriver_caminho,
        versao_webdriver = versao_navegador_str,
        plataforma_sistema = webdriver_plataforma,
    )

    if len(lista_webdrivers_locais) > 0:
        webdriver_arquivo_zip = (
            _coletar_caminho_webdriver_local(
                lista_webdrivers_locais=lista_webdrivers_locais,
            )
        )

        if (
            webdriver_arquivo_zip is None
            or webdriver_arquivo_zip == ''
        ):
            raise ValueError(
                'Nenhuma versão local do WebDriver foi '
                'encontrada. Verifique se o WebDriver está '
                'instalado corretamente no sistema.'
            )

        webdriver_caminho_arquivo_zip = webdriver_arquivo_zip.rpartition('\\')[0]
        webdriver_nome_arquivo_zip = webdriver_arquivo_zip.rpartition('\\')[-1]

        webdriver_versao = _coletar_versao_webdriver_local(
            caminho_webdriver_local=webdriver_arquivo_zip,
            divisao_pastas=divisao_pastas,
        )

        webdriver_caminho_arquivo_executavel = coletar_caminho_executavel_webdriver(
            caminho_webdriver = webdriver_caminho,
            versao_navegador = versao_navegador_str,
            divisao_pastas = divisao_pastas,
        )

        webdriver_tamanho = _coletar_tamanho_webdriver_local(
            webdriver_caminho_arquivo_executavel
        )

    metadata_webdriver_local['url'] = webdriver_url
    metadata_webdriver_local['nome'] = webdriver_nome
    metadata_webdriver_local['caminho'] = webdriver_caminho
    metadata_webdriver_local['plataforma'] = webdriver_plataforma
    metadata_webdriver_local['header_request'] = webdriver_header_request
    metadata_webdriver_local['versao'] = webdriver_versao
    metadata_webdriver_local['caminho_arquivo_zip'] = webdriver_caminho_arquivo_zip
    metadata_webdriver_local['nome_arquivo_zip'] = webdriver_nome_arquivo_zip
    metadata_webdriver_local['arquivo_zip'] = webdriver_arquivo_zip
    metadata_webdriver_local['url_arquivo_zip'] = webdriver_url_arquivo_zip
    metadata_webdriver_local['caminho_arquivo_executavel'] = webdriver_caminho_arquivo_executavel
    metadata_webdriver_local['tamanho'] = webdriver_tamanho

    return metadata_webdriver_local


def _coletar_metadata_webdriver_online(
    nome_navegador: str,
    caminho_webdriver: str,
    webdriver_plataforma: str,
    versao_navegador: list[str],
    proxies: dict[str, str] = None,
    autenticacao: Union[None, list[str, str]] = None,
    divisao_pastas: str = '/'
) -> dict[str, str]:
    if not nome_navegador.upper() in _navegadores_permitodos:
        raise SystemError(
            (
                'Não há WebDriver disponível para o navegador '
                f'"{nome_navegador}". '
                'Os navegadores suportados são: Chrome, Edge e Firefox.'
            )
        )

    webdriver_url = None
    webdriver_nome = None
    webdriver_caminho = caminho_webdriver
    webdriver_plataforma = _coletar_plataforma_webdriver()
    webdriver_header_request = None
    webdriver_versao = None
    webdriver_caminho_arquivo_zip = None
    webdriver_nome_arquivo_zip = None
    webdriver_arquivo_zip = None
    webdriver_url_arquivo_zip = None
    webdriver_caminho_arquivo_executavel = None
    webdriver_tamanho = None

    versao_navegador_str = _coletar_versao_navegador(
        versao_navegador = versao_navegador,
    )

    versao_navegador_sem_minor = _coletar_versao_navegador_sem_minor(
        versao_navegador = versao_navegador,
    )

    metadatas: dict[str, str] = dict()
    metadata_webdriver: dict[str, str] = dict()

    if nome_navegador.upper().__contains__('CHROME'):
        metadata_requisicao = _coletar_metadata_requisicao_chromedriver(
            nome_navegador,
        )

        webdriver_url = metadata_requisicao['url']
        webdriver_header_request = metadata_requisicao['headers']

        metadatas = _coletar_metadata_chromedriver(
            nome_navegador=nome_navegador,
            webdriver_url=webdriver_url,
            webdriver_plataforma=webdriver_plataforma,
            header_request=webdriver_header_request,
            versao_navegador_sem_minor=versao_navegador_sem_minor,
            proxies=proxies,
            autenticacao=autenticacao,
            divisao_pastas=divisao_pastas,
        )

        webdriver_nome = _coletar_nome_webdriver_chrome(nome_navegador)

        metadatas['nome_arquivo_zip'] = metadatas[
            'nome_arquivo_zip'
        ].replace(f"{metadatas['versao']}/", '')
    elif nome_navegador.upper().__contains__('EDGE'):
        metadata_requisicao = _coletar_metadata_requisicao_edgedriver(
            nome_navegador=nome_navegador,
            versao_navegador=versao_navegador_str,
            webdriver_plataforma=webdriver_plataforma,
        )

        webdriver_url = metadata_requisicao['url']
        webdriver_header_request = metadata_requisicao['headers']

        metadatas = _coletar_metadata_edgedriver(
            webdriver_url=webdriver_url,
            header_request=webdriver_header_request,
            proxies=proxies,
            autenticacao=autenticacao,
        )

        webdriver_nome = _coletar_nome_webdriver_edge(nome_navegador)
    elif nome_navegador.upper().__contains__('FIREFOX'):
        metadata_requisicao = _coletar_metadata_requisicao_geckodriver(
            nome_navegador,
        )

        webdriver_url = metadata_requisicao['url']
        webdriver_header_request = metadata_requisicao['headers']

        metadatas = _coletar_metadata_geckodriver(
            nome_navegador=nome_navegador,
            webdriver_url=webdriver_url,
            webdriver_plataforma=webdriver_plataforma,
            header_request=webdriver_header_request,
            versao_navegador_sem_minor=versao_navegador_sem_minor,
            proxies=proxies,
            autenticacao=autenticacao,
        )

        webdriver_nome = _coletar_nome_webdriver_firefox(nome_navegador)

    webdriver_versao = metadatas['versao']
    webdriver_nome_arquivo_zip = metadatas['nome_arquivo_zip']
    webdriver_url_arquivo_zip = metadatas['url_arquivo_zip']
    webdriver_tamanho = metadatas['tamanho']

    webdriver_caminho_arquivo_zip = divisao_pastas.join(
        (
            caminho_webdriver,
            versao_navegador_str,
        )
    )

    webdriver_arquivo_zip = divisao_pastas.join(
        (
            webdriver_caminho_arquivo_zip,
            webdriver_nome_arquivo_zip,
        )
    )

    webdriver_caminho_arquivo_executavel = divisao_pastas.join(
        (
            webdriver_caminho_arquivo_zip,
            str(webdriver_nome_arquivo_zip).replace('.zip', '.exe'),
        )
    )

    metadata_webdriver['url'] = webdriver_url
    metadata_webdriver['nome'] = webdriver_nome
    metadata_webdriver['caminho'] = webdriver_caminho
    metadata_webdriver['plataforma'] = webdriver_plataforma
    metadata_webdriver['header_request'] = webdriver_header_request
    metadata_webdriver['versao'] = webdriver_versao
    metadata_webdriver['caminho_arquivo_zip'] = webdriver_caminho_arquivo_zip
    metadata_webdriver['nome_arquivo_zip'] = webdriver_nome_arquivo_zip
    metadata_webdriver['arquivo_zip'] = webdriver_arquivo_zip
    metadata_webdriver['url_arquivo_zip'] = webdriver_url_arquivo_zip
    metadata_webdriver['caminho_arquivo_executavel'] = webdriver_caminho_arquivo_executavel
    metadata_webdriver['tamanho'] = webdriver_tamanho

    return metadata_webdriver


def _coletar_tamanho_webdriver_local(caminho_webdriver: str):
    from pathlib import Path


    executavel_webdriver = Path(caminho_webdriver)

    if not executavel_webdriver.exists():
        raise SystemError(
            'O executável do webdriver contido no '
            f'caminho {executavel_webdriver} não existe.'
        )

    tamanho_webdriver = executavel_webdriver.stat().st_size

    return tamanho_webdriver


def _definir_caminho_navegador(options_webdriver, caminho_navegador: str):
    options_webdriver.binary_location = caminho_navegador

    return options_webdriver


def _escolher_tipo_elemento(tipo_elemento):
    """Escolhe um tipo de elemento 'locator'."""
    from selenium.webdriver.common.by import By


    if tipo_elemento.upper() == 'CLASS_NAME':
        tipo_elemento = By.CLASS_NAME
    elif tipo_elemento.upper() == 'CSS_SELECTOR':
        tipo_elemento = By.CSS_SELECTOR
    elif tipo_elemento.upper() == 'ID':
        tipo_elemento = By.ID
    elif tipo_elemento.upper() == 'LINK_TEXT':
        tipo_elemento = By.LINK_TEXT
    elif tipo_elemento.upper() == 'NAME':
        tipo_elemento = By.NAME
    elif tipo_elemento.upper() == 'PARTIAL_LINK_TEXT':
        tipo_elemento = By.PARTIAL_LINK_TEXT
    elif tipo_elemento.upper() == 'TAG_NAME':
        tipo_elemento = By.TAG_NAME
    elif tipo_elemento.upper() == 'XPATH':
        tipo_elemento = By.XPATH

    return tipo_elemento


def _escolher_comportamento_esperado(comportamento_esperado: str):
    """Escolhe um tipo de comportamento manipulado pelo Selenium."""
    from selenium.webdriver.support import expected_conditions as EC


    if comportamento_esperado.upper() == 'ALERT_IS_PRESENT':
        comportamento_esperado = EC.alert_is_present
    elif comportamento_esperado.upper() == 'ALL_OF':
        comportamento_esperado = EC.all_of
    elif comportamento_esperado.upper() == 'ANY_OF':
        comportamento_esperado = EC.any_of
    elif comportamento_esperado.upper() == 'ELEMENT_ATTRIBUTE_TO_INCLUDE':
        comportamento_esperado = EC.element_attribute_to_include
    elif (
        comportamento_esperado.upper()
        == 'ELEMENT_LOCATED_SELECTION_STATE_TO_BE'
    ):
        comportamento_esperado = EC.element_located_selection_state_to_be
    elif comportamento_esperado.upper() == 'ELEMENT_LOCATED_TO_BE_SELECTED':
        comportamento_esperado = EC.element_located_to_be_selected
    elif comportamento_esperado.upper() == 'ELEMENT_SELECTION_STATE_TO_BE':
        comportamento_esperado = EC.element_selection_state_to_be
    elif comportamento_esperado.upper() == 'ELEMENT_TO_BE_CLICKABLE':
        comportamento_esperado = EC.element_to_be_clickable
    elif comportamento_esperado.upper() == 'ELEMENT_TO_BE_SELECTED':
        comportamento_esperado = EC.element_to_be_selected
    elif (
        comportamento_esperado.upper()
        == 'FRAME_TO_BE_AVAILABLE_AND_SWITCH_TO_IT'
    ):
        comportamento_esperado = EC.frame_to_be_available_and_switch_to_it
    elif comportamento_esperado.upper() == 'INVISIBILITY_OF_ELEMENT':
        comportamento_esperado = EC.invisibility_of_element
    elif comportamento_esperado.upper() == 'INVISIBILITY_OF_ELEMENT_LOCATED':
        comportamento_esperado = EC.invisibility_of_element_located
    elif comportamento_esperado.upper() == 'NEW_WINDOW_IS_OPENED':
        comportamento_esperado = EC.new_window_is_opened
    elif comportamento_esperado.upper() == 'NONE_OF':
        comportamento_esperado = EC.none_of
    elif comportamento_esperado.upper() == 'NUMBER_OF_WINDOWS_TO_BE':
        comportamento_esperado = EC.number_of_windows_to_be
    elif comportamento_esperado.upper() == 'PRESENCE_OF_ALL_ELEMENTS_LOCATED':
        comportamento_esperado = EC.presence_of_all_elements_located
    elif comportamento_esperado.upper() == 'PRESENCE_OF_ELEMENT_LOCATED':
        comportamento_esperado = EC.presence_of_element_located
    elif comportamento_esperado.upper() == 'STALENESS_OF':
        comportamento_esperado = EC.staleness_of
    elif comportamento_esperado.upper() == 'TEXT_TO_BE_PRESENT_IN_ELEMENT':
        comportamento_esperado = EC.text_to_be_present_in_element
    elif (
        comportamento_esperado.upper()
        == 'TEXT_TO_BE_PRESENT_IN_ELEMENT_ATTRIBUTE'
    ):
        comportamento_esperado = EC.text_to_be_present_in_element_attribute
    elif (
        comportamento_esperado.upper() == 'TEXT_TO_BE_PRESENT_IN_ELEMENT_VALUE'
    ):
        comportamento_esperado = EC.text_to_be_present_in_element_value
    elif comportamento_esperado.upper() == 'TITLE_CONTAINS':
        comportamento_esperado = EC.title_contains
    elif comportamento_esperado.upper() == 'TITLE_IS':
        comportamento_esperado = EC.title_is
    elif comportamento_esperado.upper() == 'URL_CHANGES':
        comportamento_esperado = EC.url_changes
    elif comportamento_esperado.upper() == 'URL_CONTAINS':
        comportamento_esperado = EC.url_contains
    elif comportamento_esperado.upper() == 'URL_MATCHES':
        comportamento_esperado = EC.url_matches
    elif comportamento_esperado.upper() == 'URL_TO_BE':
        comportamento_esperado = EC.url_to_be
    elif comportamento_esperado.upper() == 'VISIBILITY_OF':
        comportamento_esperado = EC.visibility_of
    elif (
        comportamento_esperado.upper() == 'VISIBILITY_OF_ALL_ELEMENTS_LOCATED'
    ):
        comportamento_esperado = EC.visibility_of_all_elements_located
    elif (
        comportamento_esperado.upper() == 'VISIBILITY_OF_ANY_ELEMENTS_LOCATED'
    ):
        comportamento_esperado = EC.visibility_of_any_elements_located
    elif comportamento_esperado.upper() == 'VISIBILITY_OF_ELEMENT_LOCATED':
        comportamento_esperado = EC.visibility_of_element_located
    else:
        raise SystemError('comportamento_esperado não mapeado.')

    return comportamento_esperado


def _instanciar_webdriver(
    service,
    url: str,
    webdriver_options=None,
):
    from selenium.webdriver import Remote

    service.start()

    _navegador = Remote(
        command_executor=service.service_url,
        options=webdriver_options,
        keep_alive=True,
    )

    _navegador.get(url)

    return _navegador


def _procurar_elemento(seletor, tipo_elemento='CSS_SELECTOR'):
    from py_rpautom.web_utils import _navegador, centralizar_elemento

    """Procura um elemento presente que corresponda ao informado."""
    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    webelemento = _navegador.find_element(tipo_elemento, seletor)
    centralizar_elemento(seletor, tipo_elemento)

    return webelemento


def _procurar_muitos_elementos(seletor, tipo_elemento='CSS_SELECTOR'):
    """Procura todos os elementos presentes que correspondam ao informado."""
    from py_rpautom.web_utils import _navegador, centralizar_elemento

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    lista_webelementos = _navegador.find_elements(tipo_elemento, seletor)
    centralizar_elemento(seletor, tipo_elemento)

    # retorna os valores coletados ou uma lista vazia
    return lista_webelementos


def _retornar_webdriver_options(nome_navegador):
    from selenium import webdriver

    if nome_navegador.upper().__contains__('CHROME'):
        options_webdriver = webdriver.ChromeOptions()
    elif nome_navegador.upper().__contains__('EDGE'):
        options_webdriver = webdriver.EdgeOptions()
    elif nome_navegador.upper().__contains__('FIREFOX'):
        options_webdriver = webdriver.FirefoxOptions()
    else:
        raise SystemError(
            f' {nome_navegador} não disponível. '
            'Escolha uma dessas opções: Chrome, Edge, Firefox.'
        )

    return options_webdriver


def _retornar_service(
    executavel_webdriver,
    nome_navegador,
    porta_webdriver,
):
    if nome_navegador.upper().__contains__('CHROME'):
        from selenium.webdriver.chrome.service import Service
    elif nome_navegador.upper().__contains__('EDGE'):
        from selenium.webdriver.edge.service import Service
    elif nome_navegador.upper().__contains__('FIREFOX'):
        from selenium.webdriver.firefox.service import Service
    else:
        raise SystemError(
            f' {nome_navegador} não disponível. '
            'Escolha uma dessas opções: Chrome, Edge, Firefox.'
        )

    executavel = python_utils.coletar_caminho_absoluto(
        executavel_webdriver
    )

    service = Service(
        executable_path=executavel,
        port=porta_webdriver,
    )

    return service


def _coletar_plataforma_webdriver() -> str:
    MAPA_PLATAFORMA = {
        "WINDOWS": {
            "X86": "win32",
            "I386": "win32",
            "AMD64": "win64",
            "X64": "win64",
        },
        "LINUX": {
            "X86": "linux32",
            "I386": "linux32",
            "AMD64": "linux64",
            "X64": "linux64",
        },
        "DARWIN": {
            "AMD64": "mac64",
            "X64": "mac64",
            "ARM64": "mac64",
        },
    }

    versao_so = python_utils.coletar_versao_so()

    sistema = versao_so["sistema"].upper()
    maquina = versao_so["machine"].upper()
    versao_sistema = None

    if sistema in MAPA_PLATAFORMA:
        mapa = MAPA_PLATAFORMA[sistema]
        versao_sistema = mapa.get(maquina)
    else:
        raise ValueError("Sistema não suportado")

    if versao_sistema is None:
        raise ValueError("Arquitetura não suportada")

    return versao_sistema


def coletar_caminho_executavel_webdriver(
    caminho_webdriver: str,
    versao_navegador: str,
    divisao_pastas: str,
) -> str:
    lista_executavel_webdriver_local = (
        python_utils.retornar_arquivos_em_pasta(
            caminho=caminho_webdriver,
            filtro=f'{versao_navegador}{divisao_pastas}*.exe',
        )
    )

    caminho_arquivo_executavel = ''
    if len(lista_executavel_webdriver_local) > 0:
        caminho_arquivo_executavel = (
            lista_executavel_webdriver_local[0]
        )

    return caminho_arquivo_executavel


def _coletar_caminho_webdriver_local(
    lista_webdrivers_locais: list[str],
) -> str:
    lista_webdrivers_locais.sort()
    caminho_webdriver_local = lista_webdrivers_locais[-1]

    return caminho_webdriver_local


def _coletar_versao_webdriver(executavel_webdriver: str) -> str:
    import subprocess

    execucao_webdriver = subprocess.Popen(
        [executavel_webdriver, '-V'], stdout=subprocess.PIPE
    )

    versao_webdriver = str(execucao_webdriver.stdout.read())
    versao_webdriver = versao_webdriver.partition(' (')[0]
    versao_webdriver = versao_webdriver.rpartition(' ')[-1]

    return versao_webdriver


def _coletar_versao_webdriver_local(
    caminho_webdriver_local: str,
    divisao_pastas: str
) -> str:
    if not divisao_pastas == '\\':
        caminho_webdriver_local = (
            caminho_webdriver_local.replace('\\', divisao_pastas)
        )

    versao_webdriver_local = caminho_webdriver_local.split(
        divisao_pastas
    )[-2]
    
    return versao_webdriver_local


def _coletar_versao_webdriver_local_sem_minor(
    versao_webdriver_local: str
) -> str:
    versao_webdriver_local_sem_minor = '.'.join(
        versao_webdriver_local.split('.')[:-1]
    )

    return versao_webdriver_local_sem_minor


def _coletar_versao_navegador(
    versao_navegador: list[str]
) -> str:
    versao_navegador = '.'.join(
        [str(parte_versao) for parte_versao in map(int, versao_navegador)]
    )

    return versao_navegador


def _coletar_versao_navegador_sem_minor(
    versao_navegador: list[str]
) -> str:
    versao_navegador_sem_minor = _coletar_versao_navegador(
        versao_navegador=versao_navegador
    )
    versao_navegador_sem_minor = versao_navegador_sem_minor.rpartition('.')[0]

    return versao_navegador_sem_minor


def _coletar_caminho_base_webdriver():
    from pathlib import Path

    caminho_usuario = Path.home()
    caminho_webdriver_raiz = 'webdrivers'

    caminho_webdriver = str(
        caminho_usuario / caminho_webdriver_raiz
    )

    return caminho_webdriver


def _coletar_caminho_webdriver(
    caminho_base_webdriver: str,
    nome_webdriver: str,
) -> str:
    from pathlib import Path


    caminho_usuario = Path(caminho_base_webdriver) / nome_webdriver

    return str(caminho_usuario.absolute())


def _criar_caminho_webdriver(
    caminho_webdriver: str,
) -> bool:
    resultado_caminho_webdriver = False

    try:
        # caso o caminho existir
        if not python_utils.caminho_existente(caminho_webdriver):
            # cria a pasta informada, caso necessário
            #  cria a hierarquia anterior à última pasta
            python_utils.criar_pasta(caminho_webdriver)

            resultado_caminho_webdriver = True
    except Exception as erro:
        resultado_caminho_webdriver = False

    return resultado_caminho_webdriver
