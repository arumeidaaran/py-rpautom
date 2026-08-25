"""Infraestrutura interna da automação web.

Reúne o que ``web_utils`` usa por baixo dos panos: a resolução e o
download do webdriver compatível com o navegador instalado, a
montagem das opções e do serviço do Selenium, a tradução dos tipos de
seletor e das condições de espera, e a busca de elementos, inclusive
dentro de shadow DOM. Escolhe o módulo específico de cada navegador
— ``chrome``, ``edge`` ou ``firefox`` — conforme o caso. Módulo
interno: não faz parte da API pública da biblioteca.
"""


from collections import namedtuple
from functools import partial
from typing import Union

from py_rpautom._navegadores.chrome import (
    _coletar_metadata_chromedriver,
    _coletar_metadata_requisicao_chromedriver,
    _coletar_nome_webdriver_chrome,
    _configuracao_silenciosa_chrome,
)
from py_rpautom._navegadores.edge import (
    _coletar_metadata_edgedriver,
    _coletar_metadata_requisicao_edgedriver,
    _coletar_nome_webdriver_edge,
    _configuracao_silenciosa_edge,
)
from py_rpautom._navegadores.firefox import (
    _coletar_metadata_geckodriver,
    _coletar_metadata_requisicao_geckodriver,
    _coletar_nome_webdriver_firefox,
    _configuracao_silenciosa_firefox,
)
from py_rpautom import python_utils
from requests import Response
from selenium.webdriver.support.expected_conditions import WebDriverOrWebElement
from selenium.webdriver.support.ui import WebDriverWait


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


def _adicionar_argumentos_padrao(
    argumento: Union[tuple[str, ...], None],
    argumentos_padrao: tuple[str, ...],
) -> tuple[str, ...]:
    """Acrescenta argumentos de linha de comando sem sobrescrever os informados.

    Compara pelo nome do argumento, antes do sinal de igual, e só
    adiciona o que ainda não foi informado. É essa comparação que
    garante que os padrões da biblioteca — como o silenciamento de logs
    — não anulem uma configuração explícita de quem chamou
    ``iniciar_navegador``.

    Parâmetros:
        argumento: Argumentos informados pelo usuário. Aceita ``None``.
        argumentos_padrao: Argumentos que a biblioteca deseja garantir.

    Retorna:
        tuple[str, ...]: Argumentos do usuário acrescidos apenas dos
            padrões ainda ausentes.
    """
    argumento = tuple(argumento or ())
    nomes_argumentos = [item.partition('=')[0] for item in argumento]

    for item in argumentos_padrao:
        nome_argumento = item.partition('=')[0]
        if nome_argumento not in nomes_argumentos:
            argumento = argumento + (item,)
            nomes_argumentos.append(nome_argumento)

    return argumento


def _aguardar_elemento_shadowroot(
    wait: WebDriverWait,
    tipo_elemento_shadowroot_escolhido: str,
    elemento_shadowroot: str,
    tipo_elemento_escolhido: str,
    identificador: str,
):
    """Aguarda um elemento que esteja dentro de um shadow DOM.

    Componentes web modernos encapsulam sua estrutura em um shadow DOM,
    invisível às buscas normais do Selenium. Esta função adapta a
    espera do ``WebDriverWait`` para atravessar essa fronteira,
    repetindo a busca até o elemento surgir ou o tempo esgotar.

    Parâmetros:
        wait: Objeto ``WebDriverWait`` já configurado com o tempo
            limite.
        tipo_elemento_shadowroot_escolhido: Estratégia de busca do
            elemento hospedeiro, já convertida para o padrão do Selenium.
        elemento_shadowroot: Seletor do elemento hospedeiro do shadow
            DOM.
        tipo_elemento_escolhido: Estratégia de busca do elemento alvo.
        identificador: Seletor do elemento alvo, dentro do shadow DOM.

    Retorna:
        bool: ``True`` se o elemento foi encontrado no tempo, ``False``
            caso contrário.
    """
    try:
        wait.until(
            partial(
                _buscar_elemento_shadowroot,
                tipo_elemento_shadowroot_escolhido,
                elemento_shadowroot,
                tipo_elemento_escolhido,
                identificador,
            )
        )

        return True
    except Exception:
        return False


def _buscar_elemento_shadowroot(
    tipo_elemento_shadowroot_escolhido: str,
    elemento_shadowroot: str,
    tipo_elemento_escolhido: str,
    identificador: str,
    _navegador,
):
    """Localiza um elemento dentro de um shadow DOM, em uma única tentativa.

    É a condição repetidamente avaliada por
    ``_aguardar_elemento_shadowroot``: obtém a raiz do shadow DOM a
    partir do elemento hospedeiro e procura o alvo lá dentro. Recebe o
    navegador como último parâmetro porque o ``WebDriverWait`` do
    Selenium o injeta nessa posição.

    Parâmetros:
        tipo_elemento_shadowroot_escolhido: Estratégia de busca do
            elemento hospedeiro.
        elemento_shadowroot: Seletor do elemento hospedeiro.
        tipo_elemento_escolhido: Estratégia de busca do elemento alvo.
        identificador: Seletor do elemento alvo.
        _navegador: Instância do navegador, injetada pelo Selenium.

    Retorna:
        WebElement | bool: O elemento encontrado, ou ``False`` quando
            ainda não está disponível.
    """
    try:
        shadowroot = _retornar_shadowroot(
            _navegador,
            tipo_elemento_shadowroot_escolhido,
            elemento_shadowroot,
        )

        elemento = shadowroot.find_element(
            tipo_elemento_escolhido,
            identificador,
        )

        return elemento

    except Exception:
        return False


def _normalizar_exclude_switches(valor_experimento) -> list[str]:
    """Padroniza o valor de ``excludeSwitches`` para o formato de lista.

    O Selenium aceita essa opção como texto simples ou como coleção, e
    tratar os dois casos em cada ponto de uso geraria repetição. Esta
    função converte qualquer uma das formas em lista, permitindo que
    ``_adicionar_exclude_switches`` trabalhe com um formato único.

    Parâmetros:
        valor_experimento: Valor informado, em texto, coleção ou
            ``None``.

    Retorna:
        list[str]: Itens normalizados. Lista vazia quando o valor é
            ``None``.
    """
    if valor_experimento is None:
        return []

    if isinstance(valor_experimento, str):
        return [valor_experimento]

    return list(valor_experimento)


def _adicionar_exclude_switches(
    argumento_experimental: Union[tuple[tuple[str, object], ...], None],
    exclude_switches_padrao: tuple[str, ...],
) -> tuple[tuple[str, object], ...]:
    """Acrescenta chaves a ``excludeSwitches`` preservando as existentes.

    A opção ``excludeSwitches`` desliga recursos internos do navegador,
    como a barra de "controlado por software automatizado" e a saída de
    log. Como é um valor único que precisa acumular itens de origens
    diferentes, esta função mescla os padrões da biblioteca com o que o
    usuário já tinha informado, sem duplicar.

    Parâmetros:
        argumento_experimental: Opções experimentais informadas, em
            pares nome/valor. Aceita ``None``.
        exclude_switches_padrao: Chaves que a biblioteca deseja
            garantir na opção.

    Retorna:
        tuple[tuple[str, object], ...]: Opções experimentais com
            ``excludeSwitches`` já mesclado.
    """
    experimentos = dict(argumento_experimental or ())
    exclude_switches = _normalizar_exclude_switches(
        experimentos.get('excludeSwitches')
    )

    for item in exclude_switches_padrao:
        if item not in exclude_switches:
            exclude_switches.append(item)

    experimentos['excludeSwitches'] = exclude_switches

    return tuple(experimentos.items())


def _adicionar_configuracao_silenciosa(
    options_webdriver,
    argumento: Union[tuple[str, ...], None],
    argumento_experimental: Union[tuple[tuple[str, object], ...], None],
) -> tuple[
    tuple[str, ...],
    tuple[tuple[str, object], ...],
    object,
]:
    """Aplica as opções que silenciam os logs de console do navegador.

    Sem essa configuração, os navegadores despejam mensagens técnicas
    no terminal do robô e escondem a saída da automação. Como cada
    navegador silencia de forma própria — Chrome e Edge por argumentos
    e ``excludeSwitches``, Firefox por nível de log no objeto de
    opções —, esta função identifica o navegador pelas capacidades e
    delega ao módulo correspondente.

    Parâmetros:
        options_webdriver: Objeto de opções do Selenium do navegador em
            uso.
        argumento: Argumentos de linha de comando informados pelo
            usuário.
        argumento_experimental: Opções experimentais informadas pelo
            usuário.

    Retorna:
        tuple: Argumentos, opções experimentais e objeto de opções, já
            com a configuração silenciosa aplicada.
    """
    nome_navegador = str(
        options_webdriver.capabilities.get('browserName', '')
    ).upper()

    argumento_local = tuple(argumento or ())
    argumento_experimental_local = tuple(argumento_experimental or ())
    options_webdriver_local = options_webdriver

    if nome_navegador.__contains__('EDGE'):
        argumentos_padrao, exclude_switches_padrao = (
            _configuracao_silenciosa_edge()
        )
        argumento_local = _adicionar_argumentos_padrao(
            argumento,
            argumentos_padrao,
        )
        argumento_experimental_local = _adicionar_exclude_switches(
            argumento_experimental,
            exclude_switches_padrao,
        )
    elif nome_navegador.__contains__('CHROME'):
        argumentos_padrao, exclude_switches_padrao = (
            _configuracao_silenciosa_chrome()
        )
        argumento_local = _adicionar_argumentos_padrao(
            argumento,
            argumentos_padrao,
        )
        argumento_experimental_local = _adicionar_exclude_switches(
            argumento_experimental,
            exclude_switches_padrao,
        )
    elif nome_navegador.__contains__('FIREFOX'):
        options_webdriver.log.level = _configuracao_silenciosa_firefox()
        options_webdriver_local = options_webdriver

    return (
        argumento_local,
        argumento_experimental_local,
        options_webdriver_local,
    )


def _adicionar_extras(
    options_webdriver,
    argumento,
    extensao,
    argumento_experimental,
    capacidade,
):
    """Aplica ao objeto de opções todas as personalizações do navegador.

    Concentra em um único ponto tudo o que ``iniciar_navegador`` aceita
    de configuração — argumentos, extensões, opções experimentais e
    capacidades — e aplica antes de tudo a configuração silenciosa.
    Cada grupo é opcional: valores vazios são simplesmente ignorados.

    Parâmetros:
        options_webdriver: Objeto de opções do Selenium a ser
            configurado.
        argumento: Argumentos de linha de comando do navegador.
        extensao: Caminhos de extensões ``.crx`` a carregar.
        argumento_experimental: Opções experimentais, em pares
            nome/valor.
        capacidade: Capacidades do webdriver, em pares nome/valor.

    Retorna:
        object: O objeto de opções já configurado.
    """
    (
        argumento,
        argumento_experimental,
        options_webdriver,
    ) = _adicionar_configuracao_silenciosa(
        options_webdriver,
        argumento,
        argumento_experimental,
    )

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
    """Devolve o caminho de instalação padrão do navegador no Windows.

    Evita que o usuário precise informar onde o navegador está
    instalado no caso comum. Os caminhos são fixos e correspondem à
    instalação padrão de cada navegador; instalações fora do lugar
    exigem informar ``caminho_navegador`` em ``iniciar_navegador``.

    Parâmetros:
        nome_navegador: Navegador desejado: 'chrome', 'edge' ou
            'firefox'.

    Retorna:
        str: Caminho do executável do navegador.

    Exceções:
        SystemError: Quando o navegador informado não é suportado.
    """
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
    """Lista os pacotes de webdriver já baixados para uma versão e plataforma.

    Consulta a pasta local de webdrivers em busca de arquivos ``.zip``
    que atendam à versão do navegador e à arquitetura do sistema. É a
    verificação que permite reaproveitar um driver já baixado, evitando
    uma consulta à internet a cada execução do robô.

    Parâmetros:
        caminho_webdriver: Pasta local do webdriver daquele navegador.
        versao_webdriver: Versão do navegador, usada como subpasta.
        plataforma_sistema: Identificador da plataforma (ex.: 'win64').

    Retorna:
        list[str]: Caminhos dos pacotes encontrados. Lista vazia quando
            não há nenhum.
    """
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
    """Consulta o repositório oficial de webdrivers e devolve a resposta HTTP.

    Encapsula a parte instável da resolução do driver: tenta a
    requisição repetidamente, e ao encontrar erro de certificado
    desliga a verificação SSL e tenta de novo — comportamento
    necessário em redes corporativas com inspeção de tráfego, e
    controlável pela variável de ambiente ``WDM_SSL_VERIFY``. Insiste
    até obter sucesso ou esgotar as tentativas.

    Parâmetros:
        webdriver_url: Endereço do repositório a consultar.
        header_arg: Cabeçalhos HTTP exigidos pelo repositório.
        autenticacao: Credenciais de autenticação básica, quando
            necessárias.
        proxies: Proxies por protocolo.
        metodo: Método HTTP: 'GET' traz o conteúdo, 'HEAD' apenas os
            cabeçalhos.

    Retorna:
        Response: Resposta da requisição bem-sucedida.

    Exceções:
        SystemError: Quando nenhuma das tentativas obtém resposta de
            sucesso.
    """
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
    """Reúne as informações do webdriver já presente na máquina.

    É a primeira etapa da resolução do driver: monta o caminho local a
    partir do navegador e da versão, procura um pacote compatível e, se
    encontrar, devolve também o caminho do executável. Quando nada é
    encontrado, os campos voltam como ``None`` — sinal para
    ``baixar_webdriver`` partir para a consulta online.

    Parâmetros:
        nome_navegador: Navegador alvo: 'chrome', 'edge' ou 'firefox'.
        caminho_base_webdriver: Pasta raiz de webdrivers no perfil do
            usuário.
        versao_navegador: Versão do navegador em partes.
        divisao_pastas: Separador usado na montagem dos caminhos.

    Retorna:
        dict[str, str]: Metadados do driver local, com as chaves
            ``nome``, ``caminho``, ``plataforma``, ``versao``,
            ``arquivo_zip``, ``caminho_arquivo_executavel`` e ``tamanho``.

    Exceções:
        SystemError: Quando o navegador informado não é suportado.
        ValueError: Quando um pacote é listado mas seu caminho não pode
            ser determinado.
    """
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
    """Consulta o repositório oficial e monta os dados de download do driver.

    Etapa acionada quando não há driver local compatível. Delega ao
    módulo do navegador a descoberta da versão correta — cada
    fabricante publica seus drivers de forma diferente — e, com o
    resultado, monta os caminhos de destino do pacote e do executável
    dentro da pasta local de webdrivers.

    Parâmetros:
        nome_navegador: Navegador alvo: 'chrome', 'edge' ou 'firefox'.
        caminho_webdriver: Pasta local do webdriver daquele navegador.
        webdriver_plataforma: Identificador da plataforma.
        versao_navegador: Versão do navegador em partes.
        proxies: Proxies por protocolo usados na consulta.
        autenticacao: Credenciais de autenticação básica, quando
            necessárias.
        divisao_pastas: Separador usado na montagem dos caminhos.

    Retorna:
        dict[str, str]: Metadados do driver, incluindo
            ``url_arquivo_zip``, ``arquivo_zip``,
            ``caminho_arquivo_executavel``, ``versao`` e ``tamanho``.

    Exceções:
        SystemError: Quando o navegador informado não é suportado.
    """
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
    """Devolve o tamanho, em bytes, do executável do webdriver.

    Serve para registrar o driver efetivamente em uso e para detectar
    download interrompido — um executável truncado costuma falhar de
    forma confusa na hora de iniciar o navegador. Exige que o arquivo
    exista.

    Parâmetros:
        caminho_webdriver: Caminho do executável do webdriver.

    Retorna:
        int: Tamanho do arquivo em bytes.

    Exceções:
        SystemError: Quando o executável não existe no caminho
            informado.
    """
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
    """Informa ao Selenium onde está o executável do navegador.

    Sem essa definição, o Selenium procura o navegador na instalação
    padrão do sistema. Ajustar o caminho permite usar uma instalação
    portátil ou uma versão específica, mantida à parte justamente para
    não depender das atualizações automáticas do navegador principal.

    Parâmetros:
        options_webdriver: Objeto de opções do Selenium.
        caminho_navegador: Caminho do executável do navegador.

    Retorna:
        object: O objeto de opções com o caminho definido.
    """
    options_webdriver.binary_location = caminho_navegador

    return options_webdriver


def _escolher_tipo_elemento(tipo_elemento):
    """Converte o nome do tipo de seletor na constante ``By`` do Selenium.

    É a camada que permite à biblioteca receber os tipos em texto
    simples — 'CSS_SELECTOR', 'XPATH', 'ID' — em vez de exigir a
    importação de ``By`` no código do usuário. Não diferencia
    maiúsculas de minúsculas. Valores vazios viram ``None``, e nomes
    desconhecidos são devolvidos sem alteração.

    Parâmetros:
        tipo_elemento: Nome do tipo de seletor.

    Retorna:
        str | None: Constante ``By`` correspondente, ``None`` para valor
            vazio, ou o próprio valor informado quando não reconhecido.
    """
    from selenium.webdriver.common.by import By


    if not tipo_elemento:
        tipo_elemento = None
    elif tipo_elemento.upper() == 'CLASS_NAME':
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


def _escolher_comportamento_esperado(
    comportamento_esperado: str,
) -> callable[WebDriverOrWebElement]:
    """Converte o nome de uma condição de espera na função do Selenium.

    Traduz o texto informado em ``aguardar_elemento`` para a condição
    correspondente do módulo ``expected_conditions``, cobrindo todo o
    catálogo do Selenium: presença, visibilidade, clicabilidade, texto
    esperado, mudança de título ou URL, alertas e contagem de janelas.
    É essa tradução que dispensa o usuário de importar o Selenium
    diretamente.

    Parâmetros:
        comportamento_esperado: Nome da condição, sem diferenciar
            maiúsculas.

    Retorna:
        callable: Função de condição do Selenium correspondente.

    Exceções:
        SystemError: Quando a condição informada não está mapeada.
    """
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
    """Sobe o serviço do webdriver e cria a sessão remota do navegador.

    Inicia o processo do driver, conecta-se a ele pelo endereço local
    que ele expõe e abre a URL inicial. O uso de sessão remota
    apontando para o serviço local é o que permite controlar a porta do
    driver e manter a conexão viva ao longo de execuções demoradas.

    Parâmetros:
        service: Objeto ``Service`` do Selenium, já configurado.
        url: Endereço aberto assim que a sessão é criada.
        webdriver_options: Objeto de opções com as personalizações do
            navegador.

    Retorna:
        Remote: Instância do navegador pronta para automação.
    """
    from selenium.webdriver import Remote

    service.start()

    _navegador = Remote(
        command_executor=service.service_url,
        options=webdriver_options,
        keep_alive=True,
    )

    _navegador.get(url)

    return _navegador


def _procurar_elemento(
    seletor: str,
    tipo_elemento: str = 'CSS_SELECTOR',
    elemento_shadowroot: str = None,
    tipo_elemento_shadowroot: str = None,
):
    """Localiza um elemento na página e o traz para o centro da tela.

    É o localizador usado por todas as funções de interação de
    ``web_utils``. Quando informados o hospedeiro e seu tipo, atravessa
    a fronteira do shadow DOM antes de buscar. Diferentemente de
    ``procurar_elemento``, devolve o elemento do Selenium e propaga a
    exceção quando ele não existe.

    Parâmetros:
        seletor: Seletor do elemento procurado.
        tipo_elemento: Tipo do seletor.
        elemento_shadowroot: Seletor do elemento hospedeiro do shadow
            DOM.
        tipo_elemento_shadowroot: Tipo do seletor do hospedeiro.

    Retorna:
        WebElement: Elemento localizado.

    Exceções:
        NoSuchElementException: Quando o elemento não existe na página.
    """
    from py_rpautom.web_utils import _navegador, centralizar_elemento

    arvore_webelemento = _navegador

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    if elemento_shadowroot and tipo_elemento_shadowroot:
        tipo_elemento = _escolher_tipo_elemento(tipo_elemento_shadowroot)
        elemento_raiz = _navegador.find_element(
            tipo_elemento,
            elemento_shadowroot,
        )

        arvore_webelemento = elemento_raiz.shadow_root

    webelemento = arvore_webelemento.find_element(tipo_elemento, seletor)

    centralizar_elemento(seletor, tipo_elemento)

    return webelemento


def _procurar_muitos_elementos(seletor, tipo_elemento='CSS_SELECTOR'):
    """Localiza todos os elementos que casam com o seletor.

    Base de ``contar_elementos`` e ``procurar_muitos_elementos``.
    Devolve os elementos do Selenium, e não seus textos, permitindo que
    quem chamou decida o que extrair de cada um. Nenhuma
    correspondência resulta em lista vazia, sem exceção.

    Parâmetros:
        seletor: Seletor que casa com o conjunto de elementos.
        tipo_elemento: Tipo do seletor.

    Retorna:
        list[WebElement]: Elementos encontrados, na ordem da página.
    """
    from py_rpautom.web_utils import _navegador, centralizar_elemento

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    lista_webelementos = _navegador.find_elements(tipo_elemento, seletor)
    centralizar_elemento(seletor, tipo_elemento)

    # retorna os valores coletados ou uma lista vazia
    return lista_webelementos


def _retornar_webdriver_options(nome_navegador):
    """Cria o objeto de opções correspondente ao navegador informado.

    Cada navegador tem sua própria classe de opções no Selenium, e é
    ela que aceita argumentos, extensões e capacidades. Esta função
    escolhe a classe certa e devolve a instância vazia, que será
    preenchida por ``_adicionar_extras``.

    Parâmetros:
        nome_navegador: Navegador alvo: 'chrome', 'edge' ou 'firefox'.

    Retorna:
        object: Objeto de opções do navegador correspondente.

    Exceções:
        SystemError: Quando o navegador informado não é suportado.
    """
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
    """Monta o objeto de serviço que executa o webdriver.

    O serviço é o processo intermediário entre o Selenium e o
    navegador. Aqui ele é configurado com o executável correto para o
    navegador, a porta desejada e o descarte da saída de log — este
    último responsável por manter o console do robô limpo.

    Parâmetros:
        executavel_webdriver: Caminho do executável do webdriver.
        nome_navegador: Navegador alvo: 'chrome', 'edge' ou 'firefox'.
        porta_webdriver: Porta em que o serviço escutará. ``None`` deixa
            o Selenium escolher.

    Retorna:
        Service: Objeto de serviço pronto para ser iniciado.

    Exceções:
        SystemError: Quando o navegador informado não é suportado.
    """
    from subprocess import DEVNULL

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
        log_output=DEVNULL,
    )

    return service


def _coletar_plataforma_webdriver() -> str:
    """Identifica a plataforma no padrão usado pelos repositórios de driver.

    Combina sistema operacional e arquitetura do processador no
    identificador que os fabricantes usam para nomear os pacotes —
    'win64', 'linux64', 'mac64'. É esse valor que permite escolher, na
    lista publicada, o pacote correto para a máquina.

    Retorna:
        str: Identificador da plataforma.

    Exceções:
        ValueError: Quando o sistema operacional ou a arquitetura não
            estão mapeados.
    """
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
    """Procura o executável do webdriver já descompactado na pasta da versão.

    Confirma que o pacote baixado anteriormente foi de fato extraído e
    está pronto para uso. Um retorno vazio indica que só existe o
    ``.zip``, ou nem isso — caso em que o driver precisa ser baixado ou
    descompactado antes de iniciar o navegador.

    Parâmetros:
        caminho_webdriver: Pasta local do webdriver daquele navegador.
        versao_navegador: Versão do navegador, usada como subpasta.
        divisao_pastas: Separador usado na montagem do caminho.

    Retorna:
        str: Caminho do executável encontrado, ou string vazia quando
            não há nenhum.
    """
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
    """Escolhe o pacote de webdriver mais recente entre os disponíveis.

    Quando há mais de um pacote baixado para a mesma versão do
    navegador, ordena os caminhos e fica com o último — como os nomes
    carregam a versão do driver, a ordenação alfabética coloca a versão
    mais nova no fim.

    Parâmetros:
        lista_webdrivers_locais: Caminhos dos pacotes encontrados.

    Retorna:
        str: Caminho do pacote escolhido.
    """
    lista_webdrivers_locais.sort()
    caminho_webdriver_local = lista_webdrivers_locais[-1]

    return caminho_webdriver_local


def _coletar_versao_webdriver(executavel_webdriver: str) -> str:
    """Pergunta ao próprio executável do webdriver qual é a sua versão.

    Executa o driver com a opção de versão e extrai o número da saída.
    Diferentemente de deduzir a versão pelo nome da pasta, confirma o
    que o binário realmente é — verificação útil quando se suspeita de
    um arquivo trocado ou de um download corrompido.

    Parâmetros:
        executavel_webdriver: Caminho do executável do webdriver.

    Retorna:
        str: Versão informada pelo executável.
    """
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
    """Extrai a versão do webdriver a partir do caminho do arquivo local.

    A pasta imediatamente acima do pacote leva o nome da versão, o que
    permite descobri-la sem executar o binário — mais rápido e sem
    depender de o arquivo ser executável. Normaliza o separador antes,
    já que os caminhos podem chegar em qualquer um dos dois formatos.

    Parâmetros:
        caminho_webdriver_local: Caminho do pacote do webdriver.
        divisao_pastas: Separador de pastas usado no caminho.

    Retorna:
        str: Versão extraída do caminho.
    """
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
    """Remove a última parte do número de versão do webdriver.

    Os fabricantes garantem compatibilidade dentro da mesma linha de
    versão, não em cada revisão. Comparar as versões sem o último
    número é o que permite reaproveitar um driver de revisão próxima em
    vez de baixar um novo a cada atualização menor do navegador.

    Parâmetros:
        versao_webdriver_local: Versão completa do webdriver.

    Retorna:
        str: Versão sem a última parte.
    """
    versao_webdriver_local_sem_minor = '.'.join(
        versao_webdriver_local.split('.')[:-1]
    )

    return versao_webdriver_local_sem_minor


def _coletar_versao_navegador(
    versao_navegador: list[str]
) -> str:
    """Converte a versão do navegador de partes numéricas para texto.

    ``python_utils.coletar_versao_arquivo`` devolve a versão em uma
    tupla de números, enquanto os caminhos e as URLs de download exigem
    o formato com pontos. Esta conversão é a ponte entre os dois, e a
    passagem por inteiro descarta zeros à esquerda e valores em texto.

    Parâmetros:
        versao_navegador: Versão em partes numéricas.

    Retorna:
        str: Versão no formato 'maior.menor.build.revisao'.
    """
    versao_navegador = '.'.join(
        [str(parte_versao) for parte_versao in map(int, versao_navegador)]
    )

    return versao_navegador


def _coletar_versao_navegador_sem_minor(
    versao_navegador: list[str]
) -> str:
    """Devolve a versão do navegador sem a última parte.

    É a versão usada para casar com os pacotes publicados pelos
    fabricantes, que agrupam os drivers por linha de versão e não por
    revisão exata. Sem esse recorte, quase nenhuma correspondência
    seria encontrada na lista online.

    Parâmetros:
        versao_navegador: Versão em partes numéricas.

    Retorna:
        str: Versão em texto, sem a última parte.
    """
    versao_navegador_sem_minor = _coletar_versao_navegador(
        versao_navegador=versao_navegador
    )
    versao_navegador_sem_minor = versao_navegador_sem_minor.rpartition('.')[0]

    return versao_navegador_sem_minor


def _coletar_caminho_base_webdriver():
    """Devolve a pasta ``webdrivers`` dentro do perfil do usuário.

    Centralizar os drivers no perfil do usuário resolve dois problemas:
    dispensa permissão de administrador para gravar e faz com que
    drivers baixados por um robô sirvam a todos os demais da mesma
    máquina.

    Retorna:
        str: Caminho da pasta raiz de webdrivers.
    """
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
    """Monta a pasta específica de um webdriver dentro da pasta raiz.

    Cada navegador ganha sua própria subpasta — ``chromedriver``,
    ``edgedriver``, ``geckodriver`` —, o que mantém separados os
    drivers de navegadores diferentes e permite conviver com várias
    versões de cada um.

    Parâmetros:
        caminho_base_webdriver: Pasta raiz de webdrivers.
        nome_webdriver: Nome do driver, que dá nome à subpasta.

    Retorna:
        str: Caminho absoluto da pasta do driver.
    """
    from pathlib import Path


    caminho_usuario = Path(caminho_base_webdriver) / nome_webdriver

    return str(caminho_usuario.absolute())


def _criar_caminho_webdriver(
    caminho_webdriver: str,
) -> bool:
    """Cria a pasta de webdrivers quando ela ainda não existe.

    Prepara o destino antes do download, criando toda a hierarquia
    necessária. Nunca lança exceção: devolve ``False`` diante de
    qualquer falha, permitindo que ``baixar_webdriver`` emita uma
    mensagem própria sobre a impossibilidade de gravar no perfil do
    usuário.

    Parâmetros:
        caminho_webdriver: Caminho da pasta a ser criada.

    Retorna:
        bool: ``True`` se a pasta foi criada agora; ``False`` se já
            existia ou se a criação falhou.
    """
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


def _retornar_shadowroot(
    _navegador: WebDriverOrWebElement,
    tipo_elemento_raiz: str,
    elemento_raiz: str,
):
    """Devolve a raiz do shadow DOM a partir do elemento hospedeiro.

    Componentes web modernos escondem sua estrutura interna atrás de um
    elemento hospedeiro; a busca por elementos internos só funciona a
    partir da raiz do shadow DOM. Esta função faz essa passagem, que é
    o ponto de entrada para automatizar esse tipo de componente.

    Parâmetros:
        _navegador: Instância do navegador ou elemento a partir do qual
            buscar.
        tipo_elemento_raiz: Tipo do seletor do elemento hospedeiro.
        elemento_raiz: Seletor do elemento hospedeiro.

    Retorna:
        ShadowRoot: Raiz do shadow DOM, na qual novas buscas podem ser
            feitas.
    """
    elemento_raiz = _navegador.find_element(
        tipo_elemento_raiz,
        elemento_raiz,
    )

    return elemento_raiz.shadow_root
