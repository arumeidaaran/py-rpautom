"""Módulo para automação web."""

from collections import namedtuple
from typing import Union
from pathlib import Path

from py_rpautom import desktop_utils as desktop_utils
from py_rpautom import python_utils as python_utils
from py_rpautom._navegadores.base import (
    _aguardar_elemento_shadowroot,
    _aguardar_elemento_shadowroot,
    _aguardar_elemento_shadowroot,
    _coletar_caminho_base_webdriver,
    _coletar_metadata_webdriver_local,
    _coletar_metadata_webdriver_online,
    _escolher_comportamento_esperado,
    _escolher_tipo_elemento,
    _procurar_elemento,
    _procurar_muitos_elementos,
    _criar_caminho_webdriver,
    _webdriver_info,
)

__all__ = [
    'abrir_janela',
    'abrir_pagina',
    'atualizar_pagina',
    'aguardar_elemento',
    'alterar_atributo',
    'autenticar_navegador',
    'baixar_arquivo',
    'baixar_webdriver',
    'centralizar_elemento',
    'capturar_janela_em_imagem',
    'clicar_elemento',
    'coletar_atributo',
    'coletar_id_janela',
    'coletar_nome_navegador_atual',
    'coletar_todas_ids_janelas',
    'contar_elementos',
    'encerrar_navegador',
    'escrever_em_elemento',
    'esperar_pagina_carregar',
    'executar_script',
    'extrair_texto',
    'fechar_janela',
    'fechar_janelas_menos_essa',
    'iniciar_navegador',
    'limpar_campo',
    'maximizar_janela',
    'performar',
    'print_para_pdf',
    'procurar_elemento',
    'procurar_muitos_elementos',
    'requisitar_url',
    'retornar_codigo_fonte',
    'selecionar_elemento',
    'trocar_para',
    'validar_porta',
    'voltar_pagina',
]


def baixar_arquivo(
    url,
    caminho_destino,
    stream=True,
    verificacao_ssl: bool = True,
    autenticacao: Union[None | list] = None,
    header_arg=None,
    tempo_limite: Union[int | float] = 1,
    proxies: dict[str, str] = None,
) -> bool:
    """Baixa um arquivo mediante uma url do arquivo e um
    caminho de destino já com o nome do arquivo a ser gravado.

    Parâmetros:
        url: URL HTTP/HTTPS do arquivo que será baixado.
        caminho_destino: Caminho completo, incluindo nome e extensão, onde
            o arquivo será salvo.
        stream: Define se a requisição será feita em modo stream.
        verificacao_ssl: Define se o certificado SSL será validado.
        autenticacao: Lista com usuário e senha para autenticação HTTP básica.
        header_arg: Dicionário de headers enviado na requisição.
        tempo_limite: Tempo limite, em segundos, para a requisição.
        proxies: Dicionário de proxies usado pelo requests.

    Retorna:
        Retorna booleano, `True` quando a resposta HTTP for 200, `False`
        quando o arquivo for gravado mas a resposta HTTP for diferente de
        200.

    Exceções:
        Repassa exceções de escrita de arquivo e exceções geradas por
        `requisitar_url`.

    Exemplos:
        >>> from pathlib import Path
        >>> destino = Path('nome_arquivo.extensao').absolute()
        >>> baixar_arquivo(
        ...     url='https://example.com/',
        ...     caminho_destino=str(destino),
        ... )
        True
    """
    from shutil import copyfileobj

    caminho_interno_absoluto = python_utils.coletar_caminho_absoluto(
        caminho_destino
    )

    resposta = requisitar_url(
        url=url,
        stream=stream,
        verificacao_ssl=verificacao_ssl,
        autenticacao=autenticacao,
        header_arg=header_arg,
        tempo_limite=tempo_limite,
        proxies=proxies,
    )

    with open(caminho_interno_absoluto, 'wb') as code:
        copyfileobj(resposta.raw, code)

    if resposta.status_code == 200:
        return True

    return False


def baixar_webdriver(
    nome_navegador: str,
    versao_navegador: list[str],
    proxies: dict[str, str] = None,
    autenticacao: Union[None, list] = None,
) -> _webdriver_info:
    """Baixa ou localiza o webdriver compatível com o navegador informado.

    Parâmetros:
        nome_navegador: Nome do navegador. Aceita Chrome, Edge ou Firefox.
        versao_navegador: Lista com os componentes da versão do navegador.
            ex.: ['100', '0', '0', '1']
        proxies: Dicionário de proxies usado nas requisições de metadata e
            download.
        autenticacao: Lista com usuário e senha para autenticação HTTP básica.

    Retorna:
        Retorna `webdriver_info` com metadata do webdriver e caminho do
        executável encontrado ou baixado.

    Exceções:
        SystemError: Não foi possível criar a pasta base do webdriver.

        Repassa exceções das funções de metadata, download e descompactação.

    Exemplos:
        >>> caminho_chrome = (
        ...     r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        ... )
        >>> versao = python_utils.coletar_versao_arquivo(caminho_chrome)
        >>> info = baixar_webdriver(
        ...     nome_navegador='CHROME',
        ...     versao_navegador=versao,
        ... )
    """
    global wdm_ssl_verify

    webdriver_info = namedtuple(
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

    wdm_ssl_verify = python_utils.ler_variavel_ambiente(
        nome_variavel='WDM_SSL_VERIFY',
        variavel_sistema=True,
    )

    webdriver_info.url = None
    webdriver_info.nome = None
    webdriver_info.caminho = None
    webdriver_info.plataforma = None
    webdriver_info.header_request = None
    webdriver_info.versao = None
    webdriver_info.caminho_arquivo_zip = None
    webdriver_info.nome_arquivo_zip = None
    webdriver_info.arquivo_zip = None
    webdriver_info.url_arquivo_zip = None
    webdriver_info.caminho_arquivo_executavel = None
    webdriver_info.tamanho = None

    divisao_pastas = '/'
    validacao_download = False

    caminho_base_webdriver = _coletar_caminho_base_webdriver()

    if not python_utils.caminho_existente(caminho_base_webdriver):
        resultado_caminho_webdriver = _criar_caminho_webdriver(
            caminho_webdriver=caminho_base_webdriver
        )

        if not resultado_caminho_webdriver:
            raise SystemError(
                'Não foi possível criar a pasta base do webdriver '
                'na pasta padrão do usuário.'
            )

    metadata_webdriver_local = _coletar_metadata_webdriver_local(
        nome_navegador = nome_navegador,
        caminho_base_webdriver = caminho_base_webdriver,
        versao_navegador = versao_navegador,
        divisao_pastas = divisao_pastas,
    )

    webdriver_info.url = metadata_webdriver_local['url']
    webdriver_info.nome = metadata_webdriver_local['nome']
    webdriver_info.caminho = metadata_webdriver_local['caminho']
    webdriver_info.plataforma = metadata_webdriver_local['plataforma']
    webdriver_info.header_request = metadata_webdriver_local['header_request']
    webdriver_info.versao = metadata_webdriver_local['versao']
    webdriver_info.caminho_arquivo_zip = metadata_webdriver_local[
        'caminho_arquivo_zip'
    ]
    webdriver_info.nome_arquivo_zip = metadata_webdriver_local[
        'nome_arquivo_zip'
    ]
    webdriver_info.arquivo_zip = metadata_webdriver_local['arquivo_zip']
    webdriver_info.url_arquivo_zip = metadata_webdriver_local[
        'url_arquivo_zip'
    ]
    webdriver_info.caminho_arquivo_executavel = metadata_webdriver_local[
        'caminho_arquivo_executavel'
    ]
    webdriver_info.tamanho = metadata_webdriver_local['tamanho']

    if not webdriver_info.caminho_arquivo_executavel:
        validacao_download = True

    if validacao_download is True:
        metadata_webdriver_online = _coletar_metadata_webdriver_online(
            nome_navegador = nome_navegador,
            caminho_webdriver = webdriver_info.caminho,
            webdriver_plataforma = webdriver_info.plataforma,
            versao_navegador = versao_navegador,
            proxies = proxies,
            autenticacao = autenticacao,
            divisao_pastas = divisao_pastas,
        )

        webdriver_info.url = metadata_webdriver_online['url']
        webdriver_info.nome = metadata_webdriver_online['nome']
        webdriver_info.caminho = metadata_webdriver_online['caminho']
        webdriver_info.plataforma = metadata_webdriver_online['plataforma']
        webdriver_info.header_request = metadata_webdriver_online[
            'header_request'
        ]
        webdriver_info.versao = metadata_webdriver_online['versao']
        webdriver_info.caminho_arquivo_zip = metadata_webdriver_online[
            'caminho_arquivo_zip'
        ]
        webdriver_info.nome_arquivo_zip = metadata_webdriver_online[
            'nome_arquivo_zip'
        ]
        webdriver_info.arquivo_zip = metadata_webdriver_online['arquivo_zip']
        webdriver_info.url_arquivo_zip = metadata_webdriver_online[
            'url_arquivo_zip'
        ]
        webdriver_info.caminho_arquivo_executavel = metadata_webdriver_online[
            'caminho_arquivo_executavel'
        ]
        webdriver_info.tamanho = metadata_webdriver_online['tamanho']

        if python_utils.caminho_existente(
            webdriver_info.caminho_arquivo_zip
        ) is False:
            python_utils.criar_pasta(
                caminho=webdriver_info.caminho_arquivo_zip,
            )

        if wdm_ssl_verify is None:
            wdm_ssl_verify = '1'

        verificacao_ssl = (wdm_ssl_verify).lower() in [
            '1',
            1,
            'true',
            True,
        ]

        validacao_arquivo_zip = False
        contagem = 0

        while validacao_arquivo_zip is False and (contagem < 30):
            try:        
                validacao_arquivo_zip = baixar_arquivo(
                    url=webdriver_info.url_arquivo_zip,
                    caminho_destino=webdriver_info.arquivo_zip,
                    verificacao_ssl=verificacao_ssl,
                    header_arg=webdriver_info.header_request,
                    tempo_limite=1,
                    proxies=proxies,
                    autenticacao=autenticacao,
                )
            except:
                ...

            contagem = contagem + 1

        python_utils.descompactar(
            arquivo=webdriver_info.arquivo_zip,
            caminho_destino=webdriver_info.caminho_arquivo_zip,
        )

        caminho_arquivo_executavel = (
            python_utils.retornar_arquivos_em_pasta(
                caminho=webdriver_info.caminho_arquivo_zip,
                filtro=f'**{divisao_pastas}*.exe',
            )[0]
        )

        if not (
            webdriver_info.caminho_arquivo_executavel ==
            caminho_arquivo_executavel
        ):
            webdriver_info.caminho_arquivo_executavel = (
                caminho_arquivo_executavel
            )

    return webdriver_info


def iniciar_navegador(
    url: str,
    nome_navegador: str,
    options: tuple[str] = None,
    extensoes: tuple[tuple[str]] = None,
    experimentos: tuple[tuple[str, str]] = None,
    capacidades: tuple[tuple[str, str]] = None,
    executavel: str = None,
    caminho_navegador: str = None,
    porta_webdriver: int = None,
    proxies: dict[str, str] = None,
    baixar_webdriver_previamente: bool = True,
):
    """Inicia uma instância automatizada de um navegador.

    Parâmetros:
        url: URL inicial que será aberta no navegador.
        nome_navegador: Nome do navegador. Aceita Chrome, Edge ou Firefox.
        options: Tupla com argumentos adicionados às opções do navegador.
        extensoes: Tupla com caminhos de extensões adicionadas ao navegador.
        experimentos: Tupla com pares de chave e valor para opções
            experimentais do navegador.
        capacidades: Tupla com pares de chave e valor para capacidades do
            navegador.
        executavel: Caminho do executável do webdriver.
        caminho_navegador: Caminho do executável do navegador.
        porta_webdriver: Porta de conexão a ser utilizada. 
        proxies: Dicionário de proxies usado ao baixar o webdriver.
        baixar_webdriver_previamente: Define se o webdriver será baixado
            antes de iniciar o navegador.

    Retorna:
        Retorna booleano, `True` quando o navegador é iniciado e a página
        inicial é aberta.

    Exceções:
        ValueError: `porta_webdriver` precisa ser número inteiro.

        ValueError: O executável do webdriver não foi informado ou não foi
            encontrado.

    Exemplos:
        >>> iniciar_navegador(
        ...     url='https://bing.com',
        ...     nome_navegador='chrome',
        ... )
        True
    """
    from urllib3 import disable_warnings
    from ._navegadores.base import (
        _adicionar_extras,
        _coletar_caminho_padrao_navegador,
        _definir_caminho_navegador,
        _instanciar_webdriver,
        _retornar_webdriver_options,
        _retornar_service,
    )

    global _navegador
    global _service
    global _webdriver_info

    disable_warnings()


    if porta_webdriver is not None:
        if isinstance(porta_webdriver, int) is False:
            raise ValueError(
                'Parâmetro ``porta_webdriver`` precisa ser número e do tipo inteiro.'
            )

    webdriver_info: _webdriver_info = _webdriver_info.__new__(
        _webdriver_info,
        url = None,
        nome = None,
        caminho = None,
        plataforma = None,
        header_request = None,
        versao = None,
        caminho_arquivo_zip = None,
        nome_arquivo_zip = None,
        arquivo_zip = None,
        url_arquivo_zip = None,
        caminho_arquivo_executavel = None,
        tamanho = None,
    )

    if caminho_navegador is None:
        caminho_navegador = _coletar_caminho_padrao_navegador(
            nome_navegador = nome_navegador,
        )

    if baixar_webdriver_previamente is True:
        versao_navegador = python_utils.coletar_versao_arquivo(
            caminho_navegador
        )

        webdriver_info = baixar_webdriver(
            nome_navegador=nome_navegador,
            versao_navegador=versao_navegador,
            autenticacao=None,
            proxies=proxies,
        )

    validacao_executavel = None
    if executavel is None:
        executavel = webdriver_info.caminho_arquivo_executavel

    if executavel is None:
        validacao_executavel = False
    elif not executavel.endswith('.exe'):
        validacao_executavel = False
    else:
        validacao_executavel = True

    if validacao_executavel is not True:
        if baixar_webdriver_previamente is True:
            raise ValueError(
                'Erro ao validar online o executável do webdriver.'
            )

        raise ValueError('Informe o executável do webdriver.')

    if python_utils.caminho_existente(executavel) is False:
        raise ValueError(
            (
                f'O executável do {nome_navegador} não foi '
                f'encontrado no caminho especificado: {executavel}'
            )
        )

    options_webdriver = _retornar_webdriver_options(nome_navegador)
    options_webdriver = _definir_caminho_navegador(
        options_webdriver = options_webdriver,
        caminho_navegador = caminho_navegador,
    )

    options_webdriver = _adicionar_extras(
        options_webdriver=options_webdriver,
        argumento=options,
        extensao=extensoes,
        argumento_experimental=experimentos,
        capacidade=capacidades,
    )
    _service = _retornar_service(
        executavel,
        nome_navegador,
        porta_webdriver,
    )
    _navegador = _instanciar_webdriver(
        service=_service,
        webdriver_options=options_webdriver,
        url=url,
    )

    abrir_pagina(url)

    return True


def autenticar_navegador(
    usuario: str,
    senha: str,
    caminho_janela: dict,
    caminho_usuario: dict,
    caminho_senha: dict,
    caminho_botao_aprovacao: dict,
    pid_aplicacao: int,
    estilo_aplicacao: str = 'uia',
) -> bool:
    """Autentica em pop-ups de credenciais em navegador.

    Parâmetros:
        usuario: Usuário digitado no campo de usuário do pop-up.
        senha: Senha digitada no campo de senha do pop-up.
        caminho_janela: Caminho da janela da janela do pop-up.
        caminho_usuario: Caminho do elemento na janela do campo de usuário.
        caminho_senha: Caminho do elemento na janela do campo de senha.
        caminho_botao_aprovacao: Caminho do elemento na janela do botão de
            confirmação.
        pid_aplicacao: PID do navegador que contém o pop-up.
        estilo_aplicacao: Backend usado pelo do elemento na janela,
            sendo `uia` ou `win32`.

    Retorna:
        Retorna booleano, `True` quando o pop-up é localizado e as credenciais
        são enviadas, `False` quando a janela informada não é localizada.

    Exceções:
        ValueError: `usuario` precisa ser do tipo str.

        ValueError: `senha` precisa ser do tipo str.

        ValueError: `caminho_janela` precisa ser do tipo dict.

        ValueError: `caminho_usuario` precisa ser do tipo dict.

        ValueError: `caminho_senha` precisa ser do tipo dict.

        ValueError: `caminho_botao_aprovacao` precisa ser do tipo dict.

        ValueError: `pid_aplicacao` precisa ser do tipo int.

        ValueError: `estilo_aplicacao` precisa ser do tipo str.

    Exemplos:
        >>> pid_navegador = 39440
        >>> autenticar_navegador(
        ...     usuario='usuario_teste',
        ...     senha='senha_teste',
        ...     caminho_janela={
        ...         'window': {'title': 'Authentication Required'}
        ...     },
        ...     caminho_usuario={
        ...         'window': {
        ...             'title': 'Authentication Required',
        ...             'child_window': {'auto_id': '1001'},
        ...         }
        ...     },
        ...     caminho_senha={
        ...         'window': {
        ...             'title': 'Authentication Required',
        ...             'child_window': {'auto_id': '1002'},
        ...         }
        ...     },
        ...     caminho_botao_aprovacao={
        ...         'window': {
        ...             'title': 'Authentication Required',
        ...             'child_window': {'title': 'OK'},
        ...         }
        ...     },
        ...     pid_aplicacao=pid_navegador,
        ... )
        True
    """
    # Validar o tipo da varivavel
    if isinstance(usuario, str) is False:
        raise ValueError('``usuario`` precisa ser do tipo str.')

    if isinstance(senha, str) is False:
        raise ValueError('``senha`` precisa ser do tipo str.')

    if isinstance(caminho_janela, dict) is False:
        raise ValueError('``caminho_janela`` precisa ser do tipo dict.')

    if isinstance(caminho_usuario, dict) is False:
        raise ValueError('``caminho_usuario`` precisa ser do tipo dict.')

    if isinstance(caminho_senha, dict) is False:
        raise ValueError('``caminho_senha`` precisa ser do tipo dict.')

    if isinstance(caminho_botao_aprovacao, dict) is False:
        raise ValueError(
            '``caminho_botao_aprovacao`` precisa ser do tipo dict.'
        )

    if isinstance(pid_aplicacao, int) is False:
        raise ValueError('``pid_aplicacao`` precisa ser do tipo int.')

    if isinstance(estilo_aplicacao, str) is False:
        raise ValueError('``estilo_aplicacao`` precisa ser do tipo str.')

    desktop_utils.conectar_app(
        pid_aplicacao,
        estilo_aplicacao=estilo_aplicacao,
        tempo_espera=1,
    )

    if (
        desktop_utils.localizar_elemento(
            caminho_campo=caminho_janela,
            estilo_aplicacao=estilo_aplicacao,
        )
        is True
    ):
        desktop_utils.ativar_foco(nome_janela=caminho_janela)

        desktop_utils.digitar(
            caminho_campo=caminho_usuario,
            valor=usuario,
        )
        desktop_utils.digitar(
            caminho_campo=caminho_senha,
            valor=senha,
        )
        desktop_utils.clicar(
            caminho_campo=caminho_botao_aprovacao,
        )

        return True

    return False


def abrir_pagina(url: str):
    """Abre uma página web mediante a URL informada.

    Parâmetros:
        url: URL que será carregada na janela atual.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções caso a página não possa ser aberta.

    Exemplos:
        >>> abrir_pagina(url='https://bing.com')
    """
    global _navegador

    _navegador.get(url)
    esperar_pagina_carregar()


def abrir_janela(url: str = None):
    """Abre uma nova janela/aba do navegador automatizado.

    Parâmetros:
        url: URL carregada na nova janela/aba. Quando `None`, abre uma janela
        vazia conforme comportamento do navegador.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções caso o script de abertura falhe.

    Exemplos:
        >>> abrir_janela()

        >>> abrir_janela(url='https://bing.com')
    """
    _navegador.window_handles
    _navegador.execute_script(f'window.open("{url}")')


def atualizar_pagina():
    """Atualiza a página web atual.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções caso a atualização falhe.

    Exemplos:
        >>> atualizar_pagina()
    """
    global _navegador

    _navegador.refresh()
    esperar_pagina_carregar()


def trocar_para(id, tipo):
    """Troca de contexto da automação web mediante o tipo e o id informados.

    Parâmetros:
        id: Identificador usado na troca de contexto. Para `WINDOW`, é o
            índice da janela na lista de handles. Para `ALERT`, aceita
            `TEXT`, `DISMISS`, `ACCEPT` ou comando de envio de texto.
        tipo: Tipo de contexto. Aceita `FRAME`, `PARENT_FRAME`,
            `NEW_WINDOW`, `WINDOW`, `ALERT`, `ACTIVE_ELEMENT` e
            `DEFAULT_CONTENT`.

    Retorna:
        Retorna `True` quando a troca é concluída, o texto do alerta quando
        `tipo='ALERT'` e `id='TEXT'`, ou `False` quando ocorrer erro.

    Exceções:
        Não levanta exceções.

    Exemplos:
        >>> trocar_para(id=1, tipo='WINDOW')
        True

        >>> trocar_para(id='', tipo='DEFAULT_CONTENT')
        True
    """

    try:
        resultado: bool = True
        if tipo.upper() == 'FRAME':
            _navegador.switch_to.frame(id)
        elif tipo.upper() == 'PARENT_FRAME':
            _navegador.switch_to.parent_frame(id)
        elif tipo.upper() == 'NEW_WINDOW':
            _navegador.switch_to.new_window(id)
        elif tipo.upper() == 'WINDOW':
            _navegador.switch_to.window(_navegador.window_handles[id])
        elif tipo.upper() == 'ALERT':
            if id.upper() == 'TEXT':
                resultado: str = _navegador.switch_to.alert.text
            elif id.upper() == 'DISMISS':
                _navegador.switch_to.alert.dismiss()
            elif id.upper() == 'ACCEPT':
                _navegador.switch_to.alert.accept()
            elif id.upper().__contains__('SEND_KEYS'):
                metodo, valor = id
                _navegador.switch_to.alert.send_keys(valor)
            else:
                _navegador.switch_to.alert.accept()
        elif tipo.upper() == 'ACTIVE_ELEMENT':
            _navegador.switch_to.active_element(id)
        elif tipo.upper() == 'DEFAULT_CONTENT':
            _navegador.switch_to.default_content()

        try:
            esperar_pagina_carregar()
        except:
            ...

        return resultado
    except:
        return False


def coletar_id_janela():
    """Coleta o ID da janela/aba atual do navegador automatizado.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Retorna string com o handle da janela/aba atual.

    Exceções:
        Repassa exceções caso não exista janela ativa.

    Exemplos:
        >>> id_janela = coletar_id_janela()
    """
    id_janela = _navegador.current_window_handle

    return id_janela


def coletar_nome_navegador_atual() -> str:
    """Coleta o nome do navegador atual em manipulação.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Retorna string com o nome do navegador.

    Exceções:
        Repassa exceções caso o navegador não esteja iniciado.

    Exemplos:
        >>> nome = coletar_nome_navegador_atual()
    """
    nome_navegador = _navegador.name

    return nome_navegador


def coletar_todas_ids_janelas():
    """Coleta uma lista de todos os ID's de janelas/abas do navegador.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Retorna lista de strings com os handles das janelas/abas abertas.

    Exceções:
        Repassa exceções caso o navegador não esteja iniciado.

    Exemplos:
        >>> ids = coletar_todas_ids_janelas()
    """
    ids_janelas = _navegador.window_handles

    return ids_janelas


def esperar_pagina_carregar():
    """Espera o carregamento total da página automatizada acontecer.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções caso a espera falhe.

    Exemplos:
        >>> esperar_pagina_carregar()
    """

    estado_pronto = False
    while estado_pronto is False:
        state = _navegador.execute_script('return window.document.readyState')

        if state == 'complete':
            estado_pronto = True


def voltar_pagina():
    """Volta uma posição no histórico do navegador automatizado.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções caso a navegação falhe.

    Exemplos:
        >>> voltar_pagina()
    """
    _navegador.back()

    esperar_pagina_carregar()


def capturar_janela_em_imagem(imagem: Union[str, Path]):
    """Tira uma captura da janela automatizada e salva em imagem PNG.

    Parâmetros:
        imagem: Caminho do arquivo PNG que receberá a captura.

    Retorna:
        Retorna o resultado booleano de `_navegador.save_screenshot`.

    Exceções:
        ValueError: O nome do arquivo precisa terminar com `.png`.

    Exemplos:
        >>> from pathlib import Path
        >>> imagem = Path('janela_teste.png').absolute()
        >>> capturar_janela_em_imagem(imagem)
        True
    """

    imagem_path = Path(imagem).absolute()

    if not str(imagem_path).lower().endswith(".png"):
        raise ValueError(
            'O nome do arquivo precisa terminar com uma extensão `.png`'
        )

    return _navegador.save_screenshot(str(imagem_path))


def centralizar_elemento(seletor, tipo_elemento='CSS_SELECTOR'):
    """Centraliza um elemento informado na janela do navegador automatizado.

    Parâmetros:
        seletor: Seletor do elemento que será centralizado.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções quando o elemento não é encontrado ou quando o tipo
        de seletor não é compatível com o script executado.

    Exemplos:
        >>> centralizar_elemento(
        ...     seletor='button[id="fim"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ... )

        >>> centralizar_elemento(
        ...     seletor='//button[@id="fim"]',
        ...     tipo_elemento='XPATH',
        ... )
    """
    seletor = seletor.replace('"', "'")

    if tipo_elemento.upper() == 'CSS_SELECTOR':
        _navegador.execute_script(
            'document.querySelector("'
            + seletor
            + "\").scrollIntoView({block:  'center'})"
        )
    elif tipo_elemento.upper() == 'XPATH':
        _navegador.execute_script(
            'elemento = document.evaluate("'
            + seletor
            + "\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null)\
            .singleNodeValue; elemento.scrollIntoView({block: 'center'});"
        )


def executar_script(script, args='', assincrono=False):
    """Executa um script Javascript na página automatizada.

    Parâmetros:
        script: Código JavaScript que será executado.
        args: Argumento enviado ao script como `arguments[0]`. Quando vazio,
            nenhum argumento é enviado.
        assincrono: Define se será usado `execute_async_script`.

    Retorna:
        Retorna o valor devolvido pelo JavaScript executado.

    Exceções:
        Repassa exceções caso o script falhe.

    Exemplos:
        >>> executar_script(script='return document.title')
        'Script'

        >>> executar_script(
        ...     script='return arguments[0] + 2',
        ...     args=3,
        ...     assincrono=True,
        ... )
        5
    """
    try:
        _executar_script = _navegador.execute_script
        if assincrono:
            _executar_script = _navegador.execute_async_script

        retultado_executar_script = ''
        if not args == '':
            retultado_executar_script = _executar_script(script, args)
        else:
            retultado_executar_script = _executar_script(script)
    except Exception as erro:
        raise erro

    return retultado_executar_script


def retornar_codigo_fonte():
    """Coleta e retorna o código HTML da página automatizada.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Retorna string com o HTML da página atual.

    Exceções:
        Repassa exceções caso o navegador não esteja iniciado.

    Exemplos:
        >>> retornar_codigo_fonte()
        '''
        <!DOCTYPE html><html lang="en"><head>    <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title></head><body>    </body></html>
        '''
    """
    codigo_fonte = _navegador.page_source

    return codigo_fonte


def aguardar_elemento(
    identificador: Union[str | int],
    tipo_elemento: str = 'CSS_SELECTOR',
    valor: Union[str | tuple | bool] = '',
    comportamento_esperado: str = 'VISIBILITY_OF_ELEMENT_LOCATED',
    tempo: int = 30,
    elemento_shadowroot: str = None,
    tipo_elemento_shadowroot: str = None,
):
    """Aguarda um comportamento esperado acontecer no navegador.

    Parâmetros:
        identificador: Seletor, texto, URL, título, quantidade ou outro valor
            exigido pelo comportamento esperado.
        tipo_elemento: Tipo de seletor usado com `identificador`. Aceita
            `CLASS_NAME`, `CSS_SELECTOR`, `ID`, `LINK_TEXT`, `NAME`,
            `PARTIAL_LINK_TEXT`, `TAG_NAME` e `XPATH`.
        valor: Valor complementar usado por comportamentos que esperam texto,
            atributo ou estado booleano.
        comportamento_esperado: Nome do comportamento do elemento no HTML.
        tempo: Tempo máximo, em segundos, da espera.
        elemento_shadowroot: Seletor do elemento host que contém o
            ShadowRoot.
        tipo_elemento_shadowroot: Tipo de seletor usado para localizar o host
            do ShadowRoot.

    Retorna:
        Retorna booleano, `True` quando a espera é concluída, `False` quando
        ocorre erro ou timeout.

    Exceções:
        Não levanta exceções.

    Exemplos:
        >>> aguardar_elemento(
        ...     identificador='span[id="salvar"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ... )
        False

        >>> aguardar_elemento(
        ...     identificador='button[id="salvar"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ...     comportamento_esperado='ELEMENT_TO_BE_CLICKABLE',
        ... )
        True

        >>> from urllib.parse import quote
        ... html_shadow = '''
        ... <div id="host"></div>
        ... <script>
        ... document.querySelector("#host")
        ...     .attachShadow({mode: "open"})
        ...     .innerHTML = '<button id="interno">OK</button>';
        ... </script>
        ... '''
        >>> abrir_pagina(f'data:text/html,{quote(html_shadow)}')
        ... aguardar_elemento>>> aguardar_elemento(
        ...    identificador='button[id="interno"]',
        ...    tipo_elemento='CSS_SELECTOR',
        ...    elemento_shadowroot='div[id="host"]',
        ...    tipo_elemento_shadowroot='CSS_SELECTOR',
        ...    tempo='5',
        ... )
        True
    """
    from selenium.webdriver.support.ui import WebDriverWait

    _lista_ec_sem_parametro = ['ALERT_IS_PRESENT']
    _lista_ec_com_locator = [
        'ELEMENT_LOCATED_TO_BE_SELECTED',
        'FRAME_TO_BE_AVAILABLE_AND_SWITCH_TO_IT',
        'INVISIBILITY_OF_ELEMENT_LOCATED',
        'PRESENCE_OF_ALL_ELEMENTS_LOCATED',
        'PRESENCE_OF_ELEMENT_LOCATED',
        'VISIBILITY_OF_ALL_ELEMENTS_LOCATED',
        'VISIBILITY_OF_ANY_ELEMENTS_LOCATED',
        'VISIBILITY_OF_ELEMENT_LOCATED',
        'ELEMENT_TO_BE_CLICKABLE',
    ]
    _lista_ec_com_locator_texto = [
        'TEXT_TO_BE_PRESENT_IN_ELEMENT',
        'TEXT_TO_BE_PRESENT_IN_ELEMENT_VALUE',
    ]
    _lista_ec_com_locator_boleano = ['ELEMENT_LOCATED_SELECTION_STATE_TO_BE']
    _lista_ec_com_element_boleano = ['ELEMENT_SELECTION_STATE_TO_BE']
    _lista_ec_com_locator_atributo = ['ELEMENT_ATTRIBUTE_TO_INCLUDE']
    _lista_ec_com_locator_atributo_texto = [
        'TEXT_TO_BE_PRESENT_IN_ELEMENT_ATTRIBUTE'
    ]
    _lista_ec_com_titulo = ['TITLE_CONTAINS', 'TITLE_IS']
    _lista_ec_com_url = ['URL_CHANGES', 'URL_CONTAINS', 'URL_TO_BE']
    _lista_ec_com_pattern = ['URL_MATCHES']
    _lista_ec_com_element = [
        'ELEMENT_TO_BE_SELECTED',
        'INVISIBILITY_OF_ELEMENT',
        'STALENESS_OF',
        'VISIBILITY_OF',
    ]
    _lista_ec_com_ec = ['ALL_OF', 'ANY_OF', 'NONE_OF']
    _lista_ec_com_handle = ['NEW_WINDOW_IS_OPENED']
    _lista_ec_com_int = ['NUMBER_OF_WINDOWS_TO_BE']

    try:
        wait = WebDriverWait(_navegador, tempo)

        tipo_elemento_escolhido = _escolher_tipo_elemento(tipo_elemento)
        tipo_comportamento_esperado = _escolher_comportamento_esperado(
            comportamento_esperado
        )
        complemento = False
        validacao_shadowroot = (
            elemento_shadowroot is not None
            and tipo_elemento_shadowroot is not None
        )
        tipo_elemento_shadowroot_escolhido = None

        if validacao_shadowroot is True:
            tipo_elemento_shadowroot_escolhido = _escolher_tipo_elemento(
                tipo_elemento_shadowroot
            )

        if (identificador == '') and (tipo_elemento == ''):
            if comportamento_esperado in _lista_ec_sem_parametro:
                wait.until(tipo_comportamento_esperado())
            elif comportamento_esperado in _lista_ec_com_handle:
                wait.until(
                    tipo_comportamento_esperado(_navegador.window_handles)
                )
        elif (
            (identificador == '')
            or (tipo_elemento == '')
            or (comportamento_esperado in _lista_ec_com_ec)
        ):
            raise
        else:
            if (comportamento_esperado in _lista_ec_com_locator) or (
                comportamento_esperado in _lista_ec_com_element
            ):
                if validacao_shadowroot is True:
                    _aguardar_elemento_shadowroot(
                        wait = wait,
                        tipo_elemento_shadowroot_escolhido = tipo_elemento_shadowroot_escolhido,
                        elemento_shadowroot = elemento_shadowroot,
                        tipo_elemento_escolhido = tipo_elemento_escolhido,
                        identificador = identificador,
                    )
                else:
                    wait.until(
                        tipo_comportamento_esperado(
                            (
                                tipo_elemento_escolhido,
                                identificador,
                            ),
                        )
                    )

                complemento = True
            elif (
                (comportamento_esperado in _lista_ec_com_locator_texto)
                or (comportamento_esperado in _lista_ec_com_locator_atributo)
                or (comportamento_esperado in _lista_ec_com_locator_boleano)
            ):
                if validacao_shadowroot is True:
                    _aguardar_elemento_shadowroot(
                        wait = wait,
                        tipo_elemento_shadowroot_escolhido = tipo_elemento_shadowroot_escolhido,
                        elemento_shadowroot = elemento_shadowroot,
                        tipo_elemento_escolhido = tipo_elemento_escolhido,
                        identificador = identificador,
                    )
                else:
                    wait.until(
                        tipo_comportamento_esperado(
                            (
                                tipo_elemento_escolhido,
                                identificador,
                            ),
                            valor,
                        )
                    )

                complemento = True
            elif comportamento_esperado in _lista_ec_com_element_boleano:
                if validacao_shadowroot is True:
                    _aguardar_elemento_shadowroot(
                        wait = wait,
                        tipo_elemento_shadowroot_escolhido = tipo_elemento_shadowroot_escolhido,
                        elemento_shadowroot = elemento_shadowroot,
                        tipo_elemento_escolhido = tipo_elemento_escolhido,
                        identificador = identificador,
                    )
                else:
                    wait.until(
                        tipo_comportamento_esperado(
                            _procurar_elemento(
                                tipo_elemento_escolhido,
                                identificador,
                            ),
                            valor,
                        )
                    )

                complemento = True
            elif (
                comportamento_esperado in _lista_ec_com_locator_atributo_texto
            ):
                atributo = valor[0]
                texto = valor[1]
                if validacao_shadowroot is True:
                    _aguardar_elemento_shadowroot(
                        wait = wait,
                        tipo_elemento_shadowroot_escolhido = tipo_elemento_shadowroot_escolhido,
                        elemento_shadowroot = elemento_shadowroot,
                        tipo_elemento_escolhido = tipo_elemento_escolhido,
                        identificador = identificador,
                    )
                else:
                    wait.until(
                        tipo_comportamento_esperado(
                            (
                                tipo_elemento_escolhido,
                                identificador,
                            ),
                            atributo,
                            texto,
                        )
                    )

                complemento = True
            elif (
                (comportamento_esperado in _lista_ec_com_titulo)
                or (comportamento_esperado in _lista_ec_com_url)
                or (comportamento_esperado in _lista_ec_com_pattern)
                or (comportamento_esperado in _lista_ec_com_int)
            ):
                wait.until(tipo_comportamento_esperado(identificador))
            else:
                raise

        if complemento is True:
            if validacao_shadowroot is True:
                centralizar_elemento(
                    elemento_shadowroot,
                    tipo_elemento_shadowroot,
                )
            else:
                centralizar_elemento(identificador, tipo_elemento)

            esperar_pagina_carregar()

        return True
    except:
        return False


def procurar_muitos_elementos(seletor, tipo_elemento='CSS_SELECTOR'):
    """Procura todos os elementos presentes que correspondam ao informado.

    Parâmetros:
        seletor: Seletor usado para localizar os elementos.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.

    Retorna:
        Retorna lista de strings com o texto de cada elemento localizado.

    Exceções:
        Repassa exceções quando a busca ou a centralização falha.

    Exemplos:
        >>> procurar_muitos_elementos(
        ...     seletor='//td[@class='item']',
        ...     tipo_elemento='XPATH',
        ... )
        ['A', 'B']
    """
    # instancia uma lista vazia
    lista_webelementos_str = []

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    lista_webelementos = _procurar_muitos_elementos(seletor, tipo_elemento)
    centralizar_elemento(seletor, tipo_elemento)

    # para cada elemento na lista de webelementos
    for webelemento in lista_webelementos:
        # coleta e salva o texto do elemento
        lista_webelementos_str.append(webelemento.text)

    # retorna os valores coletados ou uma lista vazia
    return lista_webelementos_str


def procurar_elemento(
    seletor: str,
    tipo_elemento: str = 'CSS_SELECTOR',
    elemento_shadowroot: str = None,
    tipo_elemento_shadowroot: str = None,
):
    """Procura um elemento presente que corresponda ao informado.

    Parâmetros:
        seletor: Seletor do elemento procurado.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.
        elemento_shadowroot: Seletor do elemento host que contém o ShadowRoot.
        tipo_elemento_shadowroot: Tipo de seletor usado para localizar o host
            do ShadowRoot. Aceita os tipos 'NONE', 'CLASS_NAME',
            'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 'PARTIAL_LINK_TEXT',
            'TAG_NAME', e 'XPATH'.

    Retorna:
        Retorna booleano, `True` quando o elemento é encontrado, `False`
        quando a busca falha.

    Exceções:
        Não levanta exceções.

    Exemplos:
        >>> procurar_elemento(
        ...     seletor='input[name="enviar"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ... )
        True

        >>> from urllib.parse import quote
        ... html_shadow = '''
        ... <div id="host"></div>
        ... <script>
        ... document.querySelector("#host")
        ...     .attachShadow({mode: "open"})
        ...     .innerHTML = '<button id="interno">OK</button>';
        ... </script>
        ... '''
        >>> abrir_pagina(f'data:text/html,{quote(html_shadow)}')
        >>> procurar_elemento(
        ...     seletor='button[id="interno"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ...     elemento_shadowroot='div[id="host"]',
        ...     tipo_elemento_shadowroot='CSS_SELECTOR',
        ... )
        True
    """

    try:
        tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
        tipo_elemento_shadowroot = _escolher_tipo_elemento(tipo_elemento_shadowroot)
        _procurar_elemento(
            seletor = seletor,
            tipo_elemento = tipo_elemento,
            elemento_shadowroot = elemento_shadowroot,
            tipo_elemento_shadowroot = tipo_elemento_shadowroot,
        )
        centralizar_elemento(seletor, tipo_elemento)

        return True
    except Exception:
        return False


def selecionar_elemento(
    seletor: str,
    valor: str,
    tipo_elemento: str = 'CSS_SELECTOR',
):
    """Seleciona em elemento de seleção um valor pelo texto visível.

    Parâmetros:
        seletor: Seletor do elemento `select`.
        valor: Texto visível da opção que será selecionada.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.

    Retorna:
        Retorna booleano, `True` quando a seleção é concluída.

    Exceções:
        Repassa exceções quando o elemento não existe ou quando o valor
        visível não é encontrado.

    Exemplos:
        >>> selecionar_elemento(
        ... seletor='//select[@id="ufff"]',
        ... valor='afff',
        ... tipo_elemento='XPATH',
        ... )
        True
    """
    from selenium.webdriver.support.ui import Select

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    aguardar_elemento(seletor, tipo_elemento)

    webelemento = _procurar_elemento(
        seletor,
        tipo_elemento,
    )

    Select(webelemento).select_by_visible_text(valor)

    return True


def contar_elementos(seletor, tipo_elemento='CSS_SELECTOR'):
    """Conta todos os elementos presentes que correspondam ao informado.

    Parâmetros:
        seletor: Seletor usado para localizar os elementos.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME',
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.

    Retorna:
        Retorna inteiro com a quantidade de elementos encontrados.

    Exceções:
        Repassa exceções quando a busca ou a centralização falha.

    Exemplos:
        >>> contar_elementos(
        ...     seletor='//table[@id="valor"]',
        ...     tipo_elemento='XPATH',
        ... )
        2
    """
    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    centralizar_elemento(seletor, tipo_elemento)
    elementos = _procurar_muitos_elementos(seletor, tipo_elemento)

    return len(elementos)


def extrair_texto(seletor, tipo_elemento='CSS_SELECTOR'):
    """Extrai o texto de um elemento informado.

    Parâmetros:
        seletor: Seletor do elemento.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.

    Retorna:
        Retorna string com o texto do elemento localizado.

    Exceções:
        Repassa exceções quando o elemento não é encontrado.

    Exemplos:
        >>> extrair_texto(
        ...     seletor='span[id="total"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ... )
        '10,00'
    """
    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    elemento = _procurar_elemento(seletor, tipo_elemento)
    text_element = elemento.text
    centralizar_elemento(seletor, tipo_elemento)

    return text_element


def coletar_atributo(
    seletor: str,
    atributo: str,
    tipo_elemento: str = 'CSS_SELECTOR',
    metodo: str = 'get_attribute',
):
    """Coleta o valor de um atributo ou propriedade CSS de um elemento.

    Parâmetros:
        seletor: Seletor do elemento.
        atributo: Nome do atributo, atributo DOM ou propriedade CSS.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.
        metodo: Método de coleta. Aceita `get_attribute`, `get_dom_attribute`
            e `value_of_css_property`.

    Retorna:
        Retorna o valor coletado do elemento.

    Exceções:
        ValueError: `metodo` precisa ser um dos métodos aceitos.

        Repassa exceções quando o elemento não é encontrado.

    Exemplos:
        >>> coletar_atributo(
        ...     seletor='a[id="link"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ...     atributo='display',
        ...     metodo='value_of_css_property',
        ... )
        'inline'
    """

    lista_metodos = [
        'get_attribute',
        'get_dom_attribute',
        'value_of_css_property',
    ]

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    elemento = _procurar_elemento(seletor, tipo_elemento)

    centralizar_elemento(seletor, tipo_elemento)

    if metodo.lower() == 'get_attribute':
        valor_atributo = elemento.get_attribute(atributo)
    elif metodo.lower() == 'get_dom_attribute':
        valor_atributo = elemento.get_dom_attribute(atributo)
    elif metodo.lower() == 'value_of_css_property':
        valor_atributo = elemento.value_of_css_property(atributo)
    else:
        raise ValueError(
            f'Escolha entre os seguintes métodos: {lista_metodos}'
        )

    return valor_atributo


def alterar_atributo(
    seletor,
    atributo,
    novo_valor,
    tipo_elemento='CSS_SELECTOR',
):
    """Altera uma propriedade de um elemento.

    Parâmetros:
        seletor: Seletor do elemento.
        atributo: Nome da propriedade do elemento que será alterada.
        novo_valor: Novo valor atribuído à propriedade.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.

    Retorna:
        Retorna o valor do atributo após a alteração.

    Exceções:
        Repassa exceções quando o elemento não é encontrado.

    Exemplos:
        >>> alterar_atributo(
        ...     seletor='//input[@id="campo"]',
        ...     tipo_elemento='XPATH',
        ...     atributo='value',
        ...     novo_valor='novo',
        ... )
        'novo'
    """
    seletor = seletor.replace('"', "'")
    tipo_elemento_transformado = _escolher_tipo_elemento(tipo_elemento)
    elemento = _procurar_elemento(seletor, tipo_elemento_transformado)
    centralizar_elemento(seletor, tipo_elemento_transformado)

    if tipo_elemento.upper() == 'XPATH':
        _navegador.execute_script(
            f"""elemento_xpath = document.evaluate(\"{seletor}\",
            document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,
            null).singleNodeValue;elemento.{atributo} = \"{novo_valor}\""""
        )
    elif tipo_elemento.upper() == 'CSS_SELECTOR':
        _navegador.execute_script(
            f"""elemento = document.querySelector(\"{seletor}\");
            elemento.{atributo} = \"{novo_valor}\""""
        )

    valor_atributo = elemento.get_attribute(atributo)

    return valor_atributo


def clicar_elemento(
    seletor: str,
    tipo_elemento: str = 'CSS_SELECTOR',
    com_alerta: bool = False,
    lista_id_alertas: list = ['text'],
    tempo_alerta: int = 30,
    elemento_shadowroot: str = None,
    tipo_elemento_shadowroot: str = None,
):
    """Clica em um elemento informado.

    Parâmetros:
        seletor: Seletor do elemento que receberá o clique.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.
        com_alerta: Define se a função deve tratar alertas após o clique.
        lista_id_alertas: Lista de ações de alerta que será tratada. Recebe 
            o valor padrão `TEXT` caso não seja informado nada.
        tempo_alerta: Tempo máximo, em segundos, para aguardar cada alerta.
        elemento_shadowroot: Seletor do elemento host que contém o ShadowRoot.
        tipo_elemento_shadowroot: Tipo de seletor usado para localizar o host
            do ShadowRoot. Aceita os tipos 'NONE', 'CLASS_NAME',
            'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 'PARTIAL_LINK_TEXT',
            'TAG_NAME', e 'XPATH'.

    Retorna:
        Retorna `True` quando o clique é concluído sem alerta. Quando
        `com_alerta=True`, retorna o último texto coletado do alerta ou string
        vazia quando nenhum alerta for encontrado.

    Exceções:
        Repassa exceções quando o elemento não é encontrado ou quando o
        clique falha.

    Exemplos:
        >>> clicar_elemento(
        ...     seletor='button[id="botao"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ... )
        True

        >>> from urllib.parse import quote
        ... html_shadow = '''
        ... <div id="host"></div>
        ... <script>
        ... document.querySelector("#host")
        ...     .attachShadow({mode: "open"})
        ...     .innerHTML = '<button id="interno">OK</button>';
        ... </script>
        ... '''
        >>> abrir_pagina(f'data:text/html,{quote(html_shadow)}')
        >>> clicar_elemento(
        ...     seletor='button[id="interno"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ...     elemento_shadowroot='div[id="host"]',
        ...     tipo_elemento_shadowroot='CSS_SELECTOR',
        ... )
        True
    """

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    centralizar_elemento(seletor, tipo_elemento)
    elemento = _procurar_elemento(
        seletor = seletor,
        tipo_elemento = tipo_elemento,
        elemento_shadowroot = elemento_shadowroot,
        tipo_elemento_shadowroot = tipo_elemento_shadowroot,
    )
    elemento.click()

    if com_alerta is True:
        definido_pelo = 'USUARIO'
        if lista_id_alertas == []:
            definido_pelo = 'SISTEMA'
            lista_id_alertas = ['TEXT']

        validacao_popup = True
        texto_popup = ''

        while not lista_id_alertas == []:
            if definido_pelo == 'USUARIO':
                valor_id = lista_id_alertas.pop(0)
            else:
                valor_id = lista_id_alertas[0]

            validacao_popup = aguardar_elemento(
                identificador='',
                tipo_elemento='',
                comportamento_esperado='ALERT_IS_PRESENT',
                tempo=tempo_alerta,
            )

            if validacao_popup == True:
                texto_popup: str = trocar_para(
                    id=valor_id,
                    tipo='ALERT',
                )
            else:
                break

        return texto_popup

    esperar_pagina_carregar()

    return True


def validar_porta(ip, porta, tempo_limite=1):
    """Valida se uma porta TCP informada está aberta para conexão.

    Parâmetros:
        ip: Endereço IP ou host que será testado.
        porta: Porta TCP que será testada.
        tempo_limite: Tempo limite, em segundos, para tentar a conexão.

    Retorna:
        Retorna booleano, `True` quando a conexão é aceita, `False` quando a
        porta não responde dentro do tempo limite.

    Exceções:
        Repassa exceções caso a criação do socket falhe.

    Exemplos:
        >>> validar_porta(ip='127.0.0.1', porta='80', tempo_limite=10)
        True
    """
    import socket

    conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conexao.settimeout(tempo_limite)
    retorno_validacao = conexao.connect_ex((ip, porta))

    if retorno_validacao == 0:
        return True

    return False


def escrever_em_elemento(
    seletor, texto, tipo_elemento='CSS_SELECTOR', performar: bool = False
):
    """Digita dentro de um elemento informado.

    Parâmetros:
        seletor: Seletor do elemento que receberá o texto.
        texto: Texto que será digitado.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.
        performar: Define se a digitação será feita com `ActionChains`.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções quando o elemento não é encontrado ou
        quando a digitação falha.

    Exemplos:
        >>> escrever_em_elemento(
        ...     seletor='input[id="campo"]',
        ...     texto='valor',
        ...     tipo_elemento='CSS_SELECTOR',
        ...     performar=True,        
        ... )
    """
    from selenium.webdriver import ActionChains

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)

    try:
        centralizar_elemento(seletor, tipo_elemento)
    except:
        ...

    webelemento = _procurar_elemento(seletor, tipo_elemento=tipo_elemento)

    if performar is False:
        webelemento.send_keys(texto)
    else:
        action = ActionChains(_navegador)
        action.click(webelemento).perform()
        webelemento.clear()
        action.send_keys_to_element(webelemento, texto).perform()

    esperar_pagina_carregar()


def limpar_campo(
    seletor, tipo_elemento='CSS_SELECTOR', performar: bool = False
):
    """Limpa o valor de um campo informado.

    Parâmetros:
        seletor: Seletor do campo que será limpo.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.
        performar: Define se a limpeza será feita com uso real de periféricos.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções quando o elemento não é encontrado ou quando a
        limpeza falha.

    Exemplos:
        >>> limpar_campo(
        ...     seletor='//input[@id="nome"]',
        ...     tipo_elemento='XPATH',
        ...     performar=False,
        ... )
    """
    from selenium.webdriver import ActionChains

    tipo_elemento = _escolher_tipo_elemento(tipo_elemento)
    centralizar_elemento(seletor, tipo_elemento)

    webelemento = _procurar_elemento(seletor, tipo_elemento=tipo_elemento)
    if performar is False:
        webelemento.clear()
    else:
        action = ActionChains(_navegador)
        action.click(webelemento).perform()
        webelemento.clear()
        action.send_keys_to_element(webelemento, '').perform()
        action.reset_actions()

    esperar_pagina_carregar()


def maximizar_janela():
    """Maximiza a janela automatizada.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções caso a janela não possa ser maximizada.

    Exemplos:
        >>> maximizar_janela()
    """

    _navegador.maximize_window()


def performar(acao, seletor, tipo_elemento='CSS_SELECTOR'):
    """Simula uma ação real de mouse em um elemento.

    Parâmetros:
        acao: Ação que será executada. Aceita `CLICK`, `DOUBLE_CLICK` e
            `MOVE_TO_ELEMENT`.
        seletor: Seletor do elemento que receberá a ação.
        tipo_elemento: Tipo de seletor usado. Aceita os tipos 'NONE',
            'CLASS_NAME', 'CSS_SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 
            'PARTIAL_LINK_TEXT', 'TAG_NAME', e 'XPATH'.

    Retorna:
        Retorna booleano, `True` ao final da função.

    Exceções:
        Repassa exceções quando o elemento não é encontrado ou quando a ação
        falha.

    Exemplos:
        >>> performar(
        ...     acao='DOUBLE_CLICK',
        ...     seletor='button[id="seguinte"]',
        ...     tipo_elemento='CSS_SELECTOR',
        ... )
        True
    """
    from selenium.webdriver import ActionChains

    action = ActionChains(_navegador)
    webelemento = _procurar_elemento(seletor, tipo_elemento)

    if acao.upper() == 'CLICK':
        action.click(webelemento).perform()
    elif acao.upper() == 'DOUBLE_CLICK':
        action.double_click(webelemento).perform()
        action = ActionChains(_navegador)
    elif acao.upper() == 'MOVE_TO_ELEMENT':
        action.move_to_element(webelemento).perform()

    return True


def print_para_pdf(
    caminho_arquivo: str,
    escala: float = 1.0,
    paginacao: list[str] = None,
    fundo: bool = None,
    encolher_para_caber: bool = None,
    orientacao: int = None,
):
    """Realiza o print da página atual e salva em um arquivo PDF.

    Parâmetros:
        caminho_arquivo: Caminho do arquivo PDF que será criado.
        escala: Escala usada no print da página.
        paginacao: Lista de páginas ou intervalos que serão impressos.
        fundo: Define se fundos CSS serão impressos.
        encolher_para_caber: Define se a página será ajustada ao tamanho do
            papel.
        orientacao: Índice da orientação da folha. Aceita 0 para portrait e 1
            para landscape.

    Retorna:
        Retorna booleano, `True` quando o PDF é criado, `False` quando ocorre
        erro.

    Exceções:
        Não levanta exceções.

    Exemplos:
        >>> from pathlib import Path
        >>> pdf = Path('pagina_teste.pdf').absolute()
        >>> print_para_pdf(str(pdf))
        True
    """
    # importa recursos do módulo base64
    import base64

    # importa recursos do módulo print_page_options
    from selenium.webdriver.common.print_page_options import PrintOptions

    try:
        # coleta o caminho completo do arquivo informado
        caminho_arquivo_absoluto = python_utils.coletar_caminho_absoluto(
            caminho_arquivo
        )

        # Instancia o objeto de print
        opcoes_print = PrintOptions()

        # caso os parâmetros não sejam None:
        if escala is not None:
            # define a escala
            opcoes_print.scale = escala
        if paginacao is not None:
            # define a paginação
            opcoes_print.page_ranges = paginacao
        if fundo is not None:
            # define o fundo
            opcoes_print.background = fundo
        if encolher_para_caber is not None:
            # define o ajuste de tamanho da página
            opcoes_print.shrink_to_fit = encolher_para_caber
        if orientacao is not None:
            # define a orientação da página
            orientacao_escolhida = opcoes_print.ORIENTATION_VALUES[orientacao]
            opcoes_print.orientation = orientacao_escolhida

        # coleta o hash base64 do print
        cache_base_64 = _navegador.print_page(opcoes_print)

        # inicia o gerenciador de contexto no arquivo de saída
        with open(caminho_arquivo_absoluto, 'wb') as arquivo_saida:
            # grava o hash base64 no arquivo de saida
            arquivo_saida.write(base64.b64decode(cache_base_64))

        # retorna True em caso de sucesso
        return True
    except:
        # retorna False em caso de falha
        return False


def requisitar_url(
    url: str,
    stream: bool = True,
    verificacao_ssl: bool = True,
    autenticacao: Union[None, list] = None,
    header_arg: str = None,
    tempo_limite: Union[int, float] = 1,
    proxies: dict[str, str] = None,
    metodo: str = 'GET',
):
    """Faz uma requisição HTTP e retorna a resposta.

    Parâmetros:
        url: URL requisitada.
        stream: Define se a resposta será baixada em modo stream.
        verificacao_ssl: Define se o certificado SSL será validado.
        autenticacao: Lista com usuário e senha para autenticação HTTP básica.
        header_arg: Dicionário de headers enviado na requisição.
        tempo_limite: Tempo limite, em segundos, para a requisição.
        proxies: Dicionário de proxies usado pela requisição.
        metodo: Método HTTP executado. Aceita `GET` e `HEAD`.

    Retorna:
        Retorna objeto `requests.Response`.

    Exceções:
        SystemError: `metodo` precisa ser `GET` ou `HEAD`.

        Repassa exceções quando a requisição falha.

    Exemplos:
        >>> resposta = requisitar_url(
        ...     url='https://bing.com/',
        ...     metodo='HEAD',
        ... )
    """
    from requests import get, head
    from requests.auth import HTTPBasicAuth


    if not metodo.upper() in ['GET', 'HEAD']:
        raise SystemError('Método não permitido, utilize GET ou HEAD')

    metodo_requisicao = get
    if metodo.upper() == 'HEAD':
        metodo_requisicao = head

    if autenticacao is not None:
        usuario, senha = autenticacao
        autenticacao = HTTPBasicAuth(usuario, senha)
    
    resposta = metodo_requisicao(
        url=url,
        stream=stream,
        verify=verificacao_ssl,
        auth=autenticacao,
        headers=header_arg,
        timeout=tempo_limite,
        proxies=proxies,
    )

    return resposta


def fechar_janela(janela):
    """Fecha uma janela/aba do navegador automatizado.

    Parâmetros:
        janela: Índice da janela/aba.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções caso a janela não exista ou não possa ser fechada.

    Exemplos:
        >>> id_principal = coletar_id_janela()
        >>> fechar_janela(id_principal)
    """
    _navegador.switch_to.window(_navegador.window_handles[janela])
    _navegador.close()


def fechar_janelas_menos_essa(id_janela):
    """Fecha todas as janelas/abas do navegador menos a informada.

    Parâmetros:
        id_janela: identificador da janela/aba que deve permanecer aberta.

    Retorna:
        Não possui retorno.

    Exceções:
        Repassa exceções caso alguma janela não possa ser selecionada ou
            fechada.

    Exemplos:
        >>> id_principal = coletar_id_janela()
        >>> fechar_janelas_menos_essa(id_principal)
    """
    lista_janelas = _navegador.window_handles
    for janela in lista_janelas:
        if janela != id_janela:
            _navegador.switch_to.window(janela)
            _navegador.close()


def encerrar_navegador():
    """Fecha a instância do navegador automatizado.

    Parâmetros:
        Não possui parâmetros.

    Retorna:
        Retorna booleano, `True` quando todas as janelas são fechadas e o
        navegador é encerrado, `False` quando ocorre erro.

    Exceções:
        Não levanta exceções.

    Exemplos:
        >>> encerrar_navegador()
        True
    """
    try:
        for janela in range(0, len(_navegador.window_handles)):
            fechar_janela(janela)
        else:
            _navegador.quit()

        return True
    except:
        return False
