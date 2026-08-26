"""Módulo para automação de aplicações desktop."""

# importa recursos do módulo pywinauto em nível global
from typing import Union

from pywinauto import Application

__all__ = [
    'ativar_foco',
    'botao_esta_marcado',
    'capturar_imagem',
    'capturar_propriedade_elemento',
    'capturar_texto',
    'clicar',
    'coletar_arvore_elementos',
    'coletar_dado_selecionado',
    'coletar_dados_selecao',
    'coletar_situacao_janela',
    'conectar_app',
    'digitar',
    'encerrar_app',
    'esta_com_foco',
    'esta_visivel',
    'fechar_janela',
    'iniciar_app',
    'janela_existente',
    'localizar_diretorio_em_treeview',
    'localizar_elemento',
    'maximizar_janela',
    'minimizar_janela',
    'mover_mouse',
    'restaurar_janela',
    'retornar_janelas_disponiveis',
    'selecionar_aba',
    'selecionar_em_campo_lista',
    'selecionar_em_campo_selecao',
    'selecionar_menu',
    'simular_clique',
    'simular_digitacao',
]


def _aplicacao(estilo_aplicacao: str = 'win32') -> Application:
    """Inicia e retorna um objeto do tipo Application da \
        biblioteca pywinauto e define APP e \
        ESTILO_APLICACAO como constantes globais.

    Parameters:
        estilo_aplicacao: Estilo de aplicação a ser manipulado, sendo \
            'win32' e 'uia' os valores aceitos.

    Returns:
        Retorna o objeto do tipo Application manipulável.

    Examples:
        ...
    """

    # define app como global
    global APP
    global ESTILO_APLICACAO

    ESTILO_APLICACAO = estilo_aplicacao

    # instancia o objeto application
    APP = Application(backend=ESTILO_APLICACAO)

    # retorna o objeto application instanciado
    return APP


def _conectar_app(
    pid: int,
    tempo_espera: int = 60,
    estilo_aplicacao: str = 'win32',
) -> int:
    """Torna um processo do sistema já existente como um objeto do tipo \
        Application manipulável.

    Parameters:
        pid: PID do processo existente.
        tempo_espera: Tempo limite em segundos para o início do processo.
        estilo_aplicacao: Estilo de aplicação a ser manipulado, sendo \
            'win32' e 'uia' os valores aceitos.

    Returns:
        Retorna int, sendo o PID do processo manipulado.

    Examples:
        ...
    """

    # define app como global
    global APP
    global ESTILO_APLICACAO

    ESTILO_APLICACAO = estilo_aplicacao

    # instancia o objeto application
    APP = _aplicacao(estilo_aplicacao=ESTILO_APLICACAO)

    # inicia o processo de execução do aplicativo passado como parâmetro
    app_conectado: Application = APP.connect(
        process=pid,
        timeout=tempo_espera,
        backend=estilo_aplicacao,
    )

    # retorna o objeto Application atrelado ao PID informado
    return app_conectado


def _localizar_elemento(
    caminho_campo: dict,
) -> Application:
    """Retorna se o caminho de elementos informado existe no objeto do \
        tipo Application sendo manipulado.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna booleano, `True` caso o caminho do elemento na aplicação \
            exista, `False` caso o caminho do elemento na aplicação \
            não exista.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.

    Examples:
        ...
    """

    # importa app para o escopo da função
    global APP

    # inicializa APP para uma variável interna
    app_interno = APP

    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    validacao_fim_dicio = False
    app_mais_interno = app_interno
    while validacao_fim_dicio is False:
        parametros = {
            'title': None,
            'control_type': None,
            'auto_id': None,
            'best_match': None,
            'session': None,
            'child_window': None,
        }

        validacao_janela = False
        if caminho_campo.keys().__contains__('window'):
            caminho_campo = caminho_campo['window']
            validacao_janela = True

        for argumento in (
            'title',
            'control_type',
            'auto_id',
            'best_match',
            'session',
            'child_window',
        ):
            if caminho_campo.keys().__contains__(argumento):
                parametros[argumento] = caminho_campo[argumento]

        if validacao_janela is True:
            acao = 'window'
        else:
            acao = 'child_window'

        comando = (
            f'app_mais_interno.{acao}('
            'title = parametros["title"], '
            'auto_id = parametros["auto_id"], '
            'control_type = parametros["control_type"],'
            'best_match = parametros["best_match"],'
            ')'
        )

        app_mais_interno = eval(comando)

        if parametros['session'] is not None:
            app_mais_interno = app_mais_interno[parametros['session']]

        if parametros['child_window'] is not None:
            caminho_campo = parametros['child_window']
        else:
            validacao_fim_dicio = True

    return app_mais_interno


def ativar_foco(nome_janela: str) -> bool:
    """Ativa a janela de um objeto do tipo `Application` deixando-a com foco.

    Parameters:
        nome_janela: O nome de uma janela já manipulável.

    Returns:
        Retorna booleano, `True` caso o foco tenha sucesso, \
        `False` caso o foco não tenha sucesso.

    Examples:
        >>> ativar_foco(nome_janela='Untitled - Notepad')
        True

        >>> ativar_foco(nome_janela='aaaaa')
        False
    """

    # importa app para o escopo da função
    global APP

    try:
        # inicializa APP para uma variável interna
        app_interno = APP

        # ativa a janela informada
        app_interno.window(title=nome_janela).set_focus()

        # retorna verdadeiro confirmando a execução da ação
        return True
    except:
        return False


def botao_esta_marcado(
    caminho_campo: dict,
    opcao_verificacao: str = 'IS_CHECKED',
) -> bool:
    """Verifica se o estado de um botão está como marcado ou não.

    Parameters:
        caminho_campo: Caminho do elemento. Precisa ser do tipo dict.
        opcao_verificacao: O nome do estado do elemento que se quer \
            verificar. Aceita as opções IS_CHECKED, GET_CHECK_STATE \
            e GET_SHOW_STATE em tipo string.

    Returns:
        Retorna booleano, `True` caso o botão estiver marcado, \
        `False` caso o botão não estiver marcado.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.

        ValueError: `opcao_verificacao` precisa ser do tipo str.

        ValueError: \
            Valores permitidos para `opcao_verificacao`: \
            get_check_state, GET_SHOW_STATE, is_checked.

    """

    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    if isinstance(opcao_verificacao, str) is False:
        raise ValueError('`opcao_verificacao` precisa ser do tipo str.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_campo)
    app_interno.exists()

    marcado = True
    if opcao_verificacao.upper() == 'IS_CHECKED':
        return app_interno.is_checked() == marcado
    elif opcao_verificacao.upper() == 'GET_CHECK_STATE':
        return app_interno.get_check_state() == marcado
    elif opcao_verificacao.upper() == 'GET_SHOW_STATE':
        return app_interno.get_show_state() == marcado
    else:
        raise ValueError(
            'Valores permitidos para `opcao_verificacao`: '
            'get_check_state, GET_SHOW_STATE, is_checked.'
        )


def capturar_imagem(caminho_campo: dict, coordenadas: tuple = None) -> bytes:
    r"""
    Captura uma imagem do estado atual do elemento
    informado e retorna a imagem em bytes.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação
            sendo manipulada.
        coordenadas: fixar valor da posição do elemento. Aceita as
            posições na seguinte ordem: esquerda, cima, direita, baixo.

    Returns:
        Retorna o valor da imagem em tipo bytes.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.

        ValueError: `coordenadas` precisa ser do tipo tuple.

        ValueError: `coordenadas` precisa conter 4 posições.

    Examples:
        >>> imagem = capturar_imagem(
        ...     caminho_campo=arvore_do_elemento,
        ...     coordenadas=(
        ...         posicao_esquerda,
        ...         posicao_cima,
        ...         posicao_direita,
        ...         posicao_baixo,
        ...     ),
        ... )
        >>> isinstance(imagem, bytes)
        True
    """

    # Validar o tipo da varivavel
    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    # Validar o tipo da varivavel
    if (isinstance(coordenadas, tuple) is False) and (coordenadas is not None):
        raise ValueError('`coordenadas` precisa ser do tipo tuple.')

    # Capturar o caminho do campo
    app_interno = _localizar_elemento(caminho_campo=caminho_campo)

    if coordenadas is not None:
        # Validar a quantidade de dados
        if not len(coordenadas) == 4:
            raise ValueError('`coordenadas` precisa conter 4 posições.')

        (
            posicao_esquerda,
            posicao_cima,
            posicao_direita,
            posicao_baixo,
        ) = coordenadas

        posicao_total = capturar_propriedade_elemento(
            caminho_campo=caminho_campo
        )['rectangle']

        posicao_total.left = posicao_esquerda
        posicao_total.right = posicao_direita
        posicao_total.top = posicao_cima
        posicao_total.bottom = posicao_baixo

        # Salvar imagem no caminho solicitado
        imagem_bytes: bytes = app_interno.capture_as_image(
            rect=posicao_total
        ).tobytes()
    else:
        # Salvar imagem no caminho solicitado
        imagem_bytes: bytes = app_interno.capture_as_image().tobytes()

    return imagem_bytes


def capturar_propriedade_elemento(
    caminho_campo: dict,
) -> dict[str, Union[str, int, bool, list]]:
    """Captura as propriedades do elemento informado.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna um dicionário contendo string na chave, e um dos valores \
            a seguir como valor: str, int, bool ou list.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.

    Examples:
        >>> capturar_propriedade_elemento(
        ...     caminho_campo={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...             'child_window': {
        ...                 'title': 'DesktopWindowXamlSource',
        ...                 'best_match': 'Windows.UI.Composition.DesktopWindowContentBridge2',
        ...                 'child_window': {
        ...                     'best_match': 'Windows.UI.Input.InputSite.WindowClass2',
        ...                 }
        ...             }
        ...         }
        ...     }
        ... )
        {'class_name': 'Windows.UI.Input.InputSite.WindowClass', 'friendly_class_name': 'Windows.UI.Input.InputSite.WindowClass', 'texts': [''], 'control_id': 0, 'rectangle': <RECT L961, T562, R961, B562>, 'is_visible': True, 'is_enabled': True, 'control_count': 0, 'style': 1342177280, 'exstyle': 0, 'user_data': 0, 'context_help_id': 0, 'fonts': [<LOGFONTW 'MS Shell Dlg' -13>], 'client_rects': [<RECT L0, T0, R0, B0>], 'is_unicode': True, 'menu_items': [], 'automation_id': ''}
    """

    # Validar o tipo da varivavel
    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    # Capturar o caminho do campo
    app_interno = _localizar_elemento(caminho_campo=caminho_campo)

    # Capturar propriedade do campo
    dado = app_interno.get_properties()

    return dado


def capturar_texto(caminho_campo: dict) -> list[str]:
    """Captura o texto de um elemento dentro de um objeto do tipo Application.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna uma lista de strings, sendo o valor capturado do elemento \
            informado.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.


    Examples:
        >>> capturar_texto(
        ...     caminho_campo={
        ...         'window': {
        ...             'title': 'Windows Powershell Main Window',
        ...             'child_window': {
        ...                 'title': 'Windows Powershell Main Menu',
        ...                 'child_window': {
        ...                     'title': 'File',
        ...                 }
        ...             }
        ...         }
        ...     },
        ... )
        ['File']
    """

    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_campo)
    app_interno.exists()

    # captura o texto do campo localizado
    valor_capturado: list = app_interno.texts()

    # retorna o valor capturado
    return valor_capturado


def clicar(
    caminho_campo: dict,
    performar: bool = False,
    indice: int = None,
) -> bool:
    """Clica em um elemento dentro de um objeto do tipo Application.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.
        performar: Ativa clique físico direto no elemento informado.

    Returns:
        Retorna `True` caso chegue ao final do clique.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.
        ValueError: `performar` precisa ser do tipo boleano.'
        ValueError: `indice` precisa ser do tipo int.


    Examples:
        >>> clicar(
        ...     caminho_campo={
        ...         'window': {
        ...             'title': 'Windows Powershell Main Window',
        ...             'child_window': {
        ...                 'title': 'Windows Powershell Main Menu',
        ...                 'child_window': {
        ...                     'title': 'File',
        ...                 }
        ...             }
        ...         }
        ...     },
        ...     indice=0,
        ...     performar=True,
        ... )
        True
    """

    # localiza o elemento até o final da árvore de parantesco do app
    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    if isinstance(performar, bool) is False:
        raise ValueError('`performar` precisa ser do tipo boleano.')

    if isinstance(indice, int) is False and indice is not None:
        raise ValueError('`indice` precisa ser do tipo int.')

    app_interno = _localizar_elemento(caminho_campo)
    app_interno.exists()

    if indice is not None:
        app_interno = app_interno.children()[indice]

    # digita o valor no campo localizado
    if performar is True:
        app_interno.click_input()
    else:
        app_interno.click()

    # retorna o valor capturado e tratado
    return True


def coletar_arvore_elementos(caminho_elemento: dict) -> list[str]:
    """Lista um elemento dentro de um objeto do tipo Application e retorna \
        o valor coletado.

    Parameters:
        caminho_elemento: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna uma lista de strings, sendo o valor capturado do elemento \
            informado.

    Raises:
        ValueError: `caminho_elemento` precisa ser do tipo dict.

    Examples:
        >>> coletar_arvore_elementos(
        ...     caminho_elemento={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...             'child_window': {
        ...                 'title': 'DesktopWindowXamlSource',
        ...                 'best_match': 'Windows.UI.Composition.DesktopWindowContentBridge2',
        ...                 'child_window': {
        ...                     'best_match': 'Windows.UI.Input.InputSite.WindowClass2',
        ...                 }
        ...             }
        ...         }
        ...     }
        ... )
        ['Control Identifiers:', '', "Windows.UI.Input.InputSite.WindowClass - ''    (L1898, T603, R1898, B603)", "['Windows.UI.Input.InputSite.WindowClass']", 'child_window(class_name="Windows.UI.Input.InputSite.WindowClass")', '']
    """

    # importa recursos do módulo io
    import io

    # importa recursos do módulo Path
    from contextlib import redirect_stdout

    if isinstance(caminho_elemento, dict) is False:
        raise ValueError('`caminho_elemento` precisa ser do tipo dict.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_elemento)
    app_interno.exists()

    conteudoStdOut = io.StringIO()
    with redirect_stdout(conteudoStdOut):
        app_interno.print_control_identifiers()

    valor = conteudoStdOut.getvalue()
    valor_dividido = valor.split('\n')

    # retorna o valor capturado e tratado
    return valor_dividido


def coletar_dado_selecionado(caminho_campo: dict) -> str:
    """Coleta a opção atualmente selecionada em um elemento de seleção de \
        um objeto do tipo Application.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna uma string, sendo o valor capturado do elemento informado.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.

    Examples:
        >>> coletar_dado_selecionado(
        ...     caminho_campo={
        ...         'window': {
        ...             'title': 'Character Map',
        ...             'child_window': {
        ...                 'title': 'Font :',
        ...                 'control_type': 'ComboBox',
        ...                 'auto_id': '105',
        ...             }
        ...         }
        ...     },
        ... )
        'Arial'
    """

    # define estático como falso para trabalhar com elemento dinâmico
    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_campo)
    app_interno.exists()

    # captura o texto do campo localizado
    valor_capturado: str = app_interno.selected_text()

    # retorna o valor capturado
    return valor_capturado


def coletar_dados_selecao(caminho_campo: dict) -> str:
    """Coleta todas as opções disponíveis para seleção em um elemento de \
        seleção de um objeto do tipo Application.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna uma string, sendo o valor capturado do elemento informado.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.

    Examples:
        ...
    """

    # define estático como falso para trabalhar com elemento dinâmico
    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_campo)
    app_interno.exists()

    # captura o texto do campo localizado
    valor_capturado: str = app_interno.item_texts()

    # retorna o valor capturado
    return valor_capturado


def coletar_situacao_janela(caminho_janela: dict) -> str:
    """Coleta a situação do estado atual de uma janela de um objeto do tipo Application.

    Parameters:
        caminho_janela: Caminho da janela na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna uma string, sendo um dos valores a seguir: 'normal', 'minimizado', 'maximizado' e 'não identificado'.

    Raises:
        ValueError: `caminho_janela` precisa ser do tipo dict.

    Examples:
        #### Validação com a janela restaurada no momento da execução do comando
        >>> coletar_situacao_janela(
        ...     caminho_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        'normal'

        #### Validação com a janela maximizada no momento da execução do comando
        >>> coletar_situacao_janela(
        ...     caminho_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        'maximizado'

        #### Validação com a janela minimizaa no momento da execução do comando
        >>> coletar_situacao_janela(
        ...     caminho_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        'minimizado'
    """

    # importa app para o escopo da função
    global APP

    if isinstance(caminho_janela, dict) is False:
        raise ValueError('`caminho_janela` precisa ser do tipo dict.')

    # inicializa APP para uma variável interna
    app_interno = APP

    situacao = ''
    # coleta a situacao atual da janela
    app_interno = _localizar_elemento(caminho_janela)
    app_interno.exists()
    situacao_temp = app_interno.get_show_state()

    # 1 - Normal
    # 2 - Minimizado
    # 3 - Maximizado
    # Caso não encontre as situações normal, ninimizado e
    #   maximizado, define um valor padrão.
    if situacao_temp == 1:
        situacao = 'normal'
    elif situacao_temp == 2:
        situacao = 'minimizado'
    elif situacao_temp == 3:
        situacao = 'maximizado'
    else:
        situacao = 'não identificado'

    # retorna a situação da janela
    return situacao


def conectar_app(
    pid: int,
    tempo_espera: int = 60,
    estilo_aplicacao: str = 'win32',
) -> int:
    """Torna um processo do sistema já existente como um objeto do tipo \
        Application manipulável.

    Parameters:
        pid: PID do processo existente.
        tempo_espera: Tempo limite em segundos para o início do processo.
        estilo_aplicacao: Estilo de aplicação a ser manipulado, sendo \
            'win32' e 'uia' os valores aceitos.

    Returns:
        Retorna int, sendo o PID do processo manipulado.

    Examples:
        >>> conectar_app(
        ...     pid=notepad_pid,
        ...     tempo_espera=10,
        ...     estilo_aplicacao='win32',
        ... )
        33144
    """

    # define app como global
    global APP
    global ESTILO_APLICACAO

    ESTILO_APLICACAO = estilo_aplicacao

    # instancia o objeto application
    APP = _aplicacao(estilo_aplicacao=ESTILO_APLICACAO)

    # inicia o processo de execução do aplicativo passado como parâmetro
    app_conectado: Application = _conectar_app(
        pid=pid,
        tempo_espera=tempo_espera,
        estilo_aplicacao=ESTILO_APLICACAO,
    )

    # coleta o PID da aplicação instanciada
    processo_app: int = app_conectado.process

    # retorna o PID coletado
    return processo_app


def digitar(
    caminho_campo: dict,
    valor: str,
) -> str:
    """Digita em um elemento dentro de um objeto do tipo Application.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.
        valor: O valor a ser digitado.

    Returns:
        Retorna str, sendo o valor do campo após a inserção do valor \
            informado.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.


    Examples:
        >>> digitar(
        ...     caminho_campo={
        ...         'window': {
        ...             'title': 'Character Map',
        ...             'child_window': {
        ...                 'control_type': 'Edit',
        ...                 'auto_id': '104',
        ...             }
        ...         }
        ...     },
        ...     valor='ABCDE',
        ... )
        "['ABCDE']"
    """

    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_campo)
    app_interno.exists()

    # digita o valor no campo localizado
    app_interno.set_edit_text(
        text=valor,
    )

    # trata o valor capturado conforme o tipo do valor de entrada
    valor_retornado = str(capturar_texto(caminho_campo))

    # retorna o valor capturado e tratado
    return valor_retornado


def encerrar_app(
    pid: int,
    forcar: bool = False,
    tempo_espera: int = 60,
) -> bool:
    """Encerra um processo do sistema de um objeto do tipo Application \
        sendo manipulado.

    Parameters:
        pid: PID do processo existente.
        forcar: Força o encerramento do processo.
        tempo_espera: Tempo limite em segundos para a tentativa de \
            encerramento do processo.

    Returns:
        Retorna booleano, `True` caso o processo seja encerrado \
            com sucesso, `False` caso o processo não seja \
            encerrado com sucesso

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.


    Examples:
        >>> encerrar_app(
        ...     pid=39440,
        ...     forcar=True,
        ...     tempo_espera=10,
        ... )
        True
    """

    # importa app para o escopo da função
    global APP

    # conecta a aplicação correspondente ao PID informado
    app_interno: Application = _conectar_app(
        pid=pid,
        tempo_espera=tempo_espera,
        estilo_aplicacao=ESTILO_APLICACAO,
    )

    # encerra o aplicativo em execução
    app_interno.kill(soft=not forcar)

    # retorna o objeto application com o processo encerrado
    return True


def esta_com_foco(nome_janela: str) -> bool:
    """Verifica se a janela de um objeto do tipo Application está com foco.

    Parameters:
        nome_janela: O nome de uma janela já manipulável.

    Returns:
        Retorna booleano, `True` caso a janela estiver com foco, \
        `False` caso a janela não estiver com foco.

    Examples:
        #### Validação sem foco na janela no momento da execução do comando
        >>> esta_com_foco(
        ...     nome_janela='Untitled - Notepad',
        ... )
        False

        #### Validação com foco na janela no momento da execução do comando
        >>> esta_com_foco(
        ...     nome_janela='Untitled - Notepad',
        ... )
        True
    """

    # importa app para o escopo da função
    global APP

    # inicializa APP para uma variável interna
    app_interno = APP

    # retorna a situacao atual de foco da janela
    return app_interno.window(title=nome_janela).has_focus()


def esta_visivel(nome_janela: dict) -> str:
    """Verifica se a janela de um objeto do tipo Application está visível.

    Parameters:
        nome_janela: Caminho da janela na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna uma string, sendo um dos valores a seguir: 'visivel', \
            'não visível', e 'não identificado'.

    Examples:
        #### Validação com a janela restaurada no momento da execução do comando
        >>> esta_visivel(
        ...     nome_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        'visivel'

        #### Validação com a janela minimizada no momento da execução do comando
        >>> esta_visivel(
        ...     nome_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        'não visível'
    """

    # coleta a situação atual da janela
    situacao = coletar_situacao_janela(nome_janela)

    # define visível para situação 'maximizado' ou 'normal'
    if situacao == 'maximizado' or situacao == 'normal':
        situacao = 'visivel'
    # define não visível para situação 'minimizado'
    elif situacao == 'minimizado':
        situacao = 'não visível'
    # Caso não encontre as situações normal, ninimizado e maximizado
    else:
        # define um valor padrão
        situacao = 'não identificado'

    # retorna a situação da janela
    return situacao


def fechar_janela(caminho_janela: dict) -> bool:
    """Encerra uma janela de um objeto do tipo Application sendo manipulado.

    Parameters:
        caminho_janela: Caminho da janela na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna booleano, `True`.

    Raises:
        ValueError: `caminho_janela` precisa ser do tipo dict.

    Examples:
        >>> fechar_janela(
        ...     caminho_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        True
    """

    # importa app para o escopo da função
    global APP

    if isinstance(caminho_janela, dict) is False:
        raise ValueError('`caminho_janela` precisa ser do tipo dict.')

    # inicializa APP para uma variável interna
    app_interno = _localizar_elemento(
        caminho_campo=caminho_janela,
    )
    app_interno.exists()

    # fecha a janela informada
    app_interno.close()

    # retorna verdadeiro confirmando a execução da ação
    return True


def iniciar_app(
    executavel: str,
    estilo_aplicacao: str = 'win32',
    esperar: tuple = (),
    inverter: bool = False,
    ocioso: bool = False,
) -> int:
    """Inicia um processo do sistema de um objeto do tipo Application  sendo manipulado.

    Parameters:
        executavel: Caminho da aplicação a ser manipulada.
        estilo_aplicacao: Estilo de aplicação a ser manipulado, sendo \
            'win32' e 'uia' os valores aceitos.
        esperar: Define, em uma tupla, a condição esperada pela \
            aplicação, sendo o primeiro valor a condição esperada nos \
            valores 'exists', 'visible', 'enabled', 'ready', ou 'active', \
            e o segundo valor o tempo limite de espera em segundos.
        inverter: `True` Aguarda a inicialização da aplicação \
            ficar na condição informada, `False` aguarda a inicialização \
            da aplicação ficar diferente da condição informada.
        ocioso: Define se deve aguardar a inicialização da \
            aplicação sair do ocioso. `True` para aguardar, \
            `False` para não aguardar.

    Returns:
        Retorna int, sendo o PID do processo manipulado.

    Examples:
        >>> executavel = (
        ...     r'C:\\Program Files\\WindowsApps'
        ...     r'\\Microsoft.WindowsNotepad_11.2410.21.0_x64__8wekyb3d8bbwe'
        ...     r'\\Notepad\\Notepad.exe'
        ... )
        >>> pid = iniciar_app(
        ...     executavel=executavel,
        ...     estilo_aplicacao='uia',
        ...     esperar=('ready', 10),
        ...     ocioso=False,
        ...     inverter=True,
        ... )
        >>> isinstance(pid, int)
        True
    """

    # define app como global
    global APP
    global ESTILO_APLICACAO

    ESTILO_APLICACAO = estilo_aplicacao

    # instancia o objeto application
    APP = _aplicacao(estilo_aplicacao=ESTILO_APLICACAO)

    # inicia o processo de execução do aplicativo passado como parâmetro
    APP.start(
        cmd_line=executavel,
        wait_for_idle=ocioso,
    )

    esperar_por = tempo_espera = None
    # verifica se foi passado algum parâmetro para esperar, caso não:
    if esperar == ():
        # aguarda a inicialização da aplicação ficar pronta em até 10 segundos
        esperar_por = 'ready'
        tempo_espera = 10
    else:
        esperar_por, tempo_espera = esperar

    if inverter is False:
        # aguarda a inicialização da aplicação ficar na condição informada
        APP.window().wait(
            wait_for=esperar_por,
            timeout=tempo_espera,
            retry_interval=None,
        )
    else:
        # aguarda a inicialização da aplicação não ficar na condição informada
        APP.window().wait_not(
            wait_for_not=esperar_por,
            timeout=tempo_espera,
            retry_interval=None,
        )

    # coleta o PID da aplicação instanciada
    processo_app: int = APP.process

    # retorna o PID coletado
    return processo_app


def janela_existente(pid: int, nome_janela: str) -> bool:
    """Verifica se a janela de um objeto do tipo Application existe.

    Parameters:
        nome_janela: O nome de uma janela já manipulável.
        pid: PID do processo existente.

    Returns:
        Retorna booleano, `True` caso a janela da aplicação exista, \
            `False` caso a janela da aplicação não exista.

    Examples:
        >>> janela_existente(
        ...     pid=39440,
        ...     nome_janela='Untitled - Notepad',
        ... )
        True
    """

    # coleta a situação atual da janela
    lista_janelas = retornar_janelas_disponiveis(pid)

    # verifica se o nome da janela informada corresponde à alguma janela na lista
    for janela in lista_janelas:
        # caso o nome da janela seja o mesmo da janela atual da lista
        if janela == nome_janela:
            # retorna True
            return True

    # retorna False caso nenhuma janela tenha correspondido
    return False


def localizar_diretorio_em_treeview(
    caminho_janela: dict,
    caminho_diretorio: str,
) -> bool:
    """Localiza um diretório, seguindo a árvore de diretórios informada, \
        dentro de um objeto TreeView do tipo Application.

    Parameters:
        caminho_janela: Caminho da janela na estrutura da aplicação \
            sendo manipulada.
        caminho_diretorio: Caminho da estrutura de diretórios a ser localizada.

    Returns:
        Retorna booleano, `True` caso a localização tenha sucesso, \
            `False` caso a localização não tenha sucesso.

    Raises:
        ValueError: `caminho_janela` precisa ser do tipo dict.

    Examples:
        ...
    """

    try:
        if isinstance(caminho_janela, dict) is False:
            raise ValueError('`caminho_janela` precisa ser do tipo dict.')

        # localiza e armazena o elemento conforme informado
        app_interno = _localizar_elemento(caminho_janela)
        app_interno.exists()

        # seleciona o caminho informado na janela do tipo TreeView
        app_interno.TreeView.get_item(caminho_diretorio).click()

        # clica em Ok para confirmar
        app_interno.OK.click()

        # retorna verdadeiro caso processo seja feito com sucesso
        return True
    except:
        return False


def localizar_elemento(
    caminho_campo: dict,
    estilo_aplicacao: str = 'win32',
) -> bool:
    """Retorna se o caminho de elementos informado existe no objeto do \
        tipo Application sendo manipulado.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.
        estilo_aplicacao: Estilo de aplicação a ser manipulado, sendo \
            'win32' e 'uia' os valores aceitos.

    Returns:
        Retorna booleano, `True` caso o caminho do elemento na aplicação \
            exista, `False` caso o caminho do elemento na aplicação \
            não exista.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.

    Examples:
        >>> localizar_elemento(
        ...     caminho_campo={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...             'child_window': {
        ...                 'title': 'DesktopWindowXamlSource',
        ...                 'best_match': 'Windows.UI.Composition.DesktopWindowContentBridge2',
        ...                 'child_window': {
        ...                     'best_match': 'Windows.UI.Input.InputSite.WindowClass2',
        ...                 }
        ...             }
        ...         }
        ...     },
        ...     estilo_aplicacao='win32',
        ... )
        True
    """

    # importa app para o escopo da função
    global APP

    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    # inicializa APP para uma variável interna
    app_interno = _localizar_elemento(
        caminho_campo=caminho_campo,
    )
    app_interno.exists()

    return app_interno.exists()


def maximizar_janela(caminho_janela: dict) -> bool:
    """Maximiza a janela de um objeto do tipo Application.

    Parameters:
        caminho_janela: Caminho da janela na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna booleano, `True` caso a ação de maximizar tenha sucesso, \
        `False` caso a ação de maximizar não tenha sucesso.

    Raises:
        TypeError: `caminho_janela` precisa ser do tipo dict.

    Examples:
        >>> maximizar_janela(
        ...     caminho_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        True
    """

    # importa app para o escopo da função
    global APP

    if isinstance(caminho_janela, dict) is False:
        raise ValueError('`caminho_janela` precisa ser do tipo dict.')

    try:
        # localiza o elemento até o final da árvore de parantesco do app
        app_interno = _localizar_elemento(caminho_janela)
        app_interno.exists()

        # maximiza a janela informada
        app_interno.maximize()

        # retorna verdadeiro confirmando a execução da ação
        return True
    except:
        return False


def minimizar_janela(caminho_janela: dict) -> bool:
    """Miniminiza a janela de um objeto do tipo Application.

    Parameters:
        caminho_janela: Caminho da janela na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna booleano, `True` caso a ação de miniminizar tenha sucesso, \
        `False` caso a ação de miniminizar não tenha sucesso.

    Raises:
        TypeError: `caminho_janela` precisa ser do tipo dict.

    Examples:
        >>> minimizar_janela(
        ...     caminho_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        True
    """

    # importa app para o escopo da função
    global APP

    if isinstance(caminho_janela, dict) is False:
        raise ValueError('`caminho_janela` precisa ser do tipo dict.')

    try:
        # localiza o elemento até o final da árvore de parantesco do app
        app_interno = _localizar_elemento(caminho_janela)
        app_interno.exists()

        # miniminiza a janela informada
        app_interno.minimize()

        # retorna verdadeiro confirmando a execução da ação
        return True
    except:
        return False


def mover_mouse(eixo_x: int, eixo_y: int) -> bool:
    """Move o mouse para o ponto das coordenadas X e Y informadas.

    Parameters:
        eixo_x: valor int para a posição de coordenada X.
        eixo_y: valor int para a posição de coordenada Y.

    Returns:
        Retorna booleano, `True` caso tenha sucesso ao mover o mouse, \
        `False` caso não tenha sucesso ao mover o mouse.

    Raises:
        ValueError: Coordenadas precisam ser do tipo inteiro .

    Examples:
        >>> mover_mouse(eixo_x=961, eixo_y=562,)
        True
    """

    # importa recursos do módulo mouse
    from pywinauto.mouse import move

    if (not isinstance(eixo_x, int)) or (not isinstance(eixo_y, int)):
        raise ValueError('Coordenadas precisam ser do tipo inteiro .')

    try:
        move(coords=(eixo_x, eixo_y))

        return True
    except:
        return False


def restaurar_janela(caminho_janela: dict) -> bool:
    """Restaura a janela de um objeto do tipo Application.

    Parameters:
        caminho_janela: Caminho da janela na estrutura da aplicação \
            sendo manipulada.

    Returns:
        Retorna booleano, `True` caso a ação de restaurar tenha sucesso, \
        `False` caso a ação de restaurar não tenha sucesso.

    Raises:
        TypeError: `caminho_janela` precisa ser do tipo dict.

    Examples:
        >>> restaurar_janela(
        ...     caminho_janela={
        ...         'window': {
        ...             'title': 'Untitled - Notepad',
        ...         }
        ...     }
        ... )
        True
    """

    # importa app para o escopo da função
    global APP

    if isinstance(caminho_janela, dict) is False:
        raise ValueError('`caminho_janela` precisa ser do tipo dict.')

    try:
        # localiza o elemento até o final da árvore de parantesco do app
        app_interno = _localizar_elemento(caminho_janela)
        app_interno.exists()

        # restaura a janela informada
        app_interno.restore()

        # retorna verdadeiro confirmando a execução da ação
        return True
    except:
        return True


def retornar_janelas_disponiveis(
    pid: int,
    estilo_aplicacao: str = 'win32',
) -> list[str]:
    """Retorna as janelas disponíveis em um objeto do tipo \
        Application manipulável.

    Parameters:
        pid: PID do processo existente.
        estilo_aplicacao: Estilo de aplicação a ser manipulado, sendo \
            'win32' e 'uia' os valores aceitos.

    Returns:
        Retorna uma lista de strings, sendo o valor capturado do PID \
            informado.

    Examples:
        >>> retornar_janelas_disponiveis(
        ...     pid=24728,
        ...     estilo_aplicacao='uia'
        ... )
    """

    # importa app para o escopo da função
    global APP
    global ESTILO_APLICACAO

    ESTILO_APLICACAO = estilo_aplicacao

    # instancia o objeto application
    APP = _aplicacao(estilo_aplicacao=ESTILO_APLICACAO)

    # conecta a aplicação correspondente ao PID informado
    tempo_espera = 60
    app_interno: Application = _conectar_app(
        pid=pid,
        tempo_espera=tempo_espera,
        estilo_aplicacao=ESTILO_APLICACAO,
    )

    # coleta as janelas disponíveis
    lista_janelas = app_interno.windows()

    # instancia uma lista vazia
    lista_janelas_str = []
    # para cada janela na lista de janelas
    for janela in lista_janelas:
        # coleta e salva o nome da janela
        lista_janelas_str.append(janela.texts()[0])

    # retorna uma lista das janelas coletadas
    return lista_janelas_str


def selecionar_aba(caminho_campo: dict, item: Union[str, int]) -> bool:
    """Seleciona uma aba em um conjunto de abas de um objeto do tipo \
        Application manipulável.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.
        item: Valor em int ou em str da aba a ser selecionada.

    Returns:
        Retorna booleano, `True` caso a aba seja selecionada com sucesso, \
        `False` caso a aba não seja selecionada com sucesso.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.
        ValueError: `item` precisa ser do tipo int ou str.

    Examples:
        ...
    """

    from pywinauto.controls.common_controls import TabControlWrapper

    # define estático como falso para trabalhar com elemento dinâmico
    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    if isinstance(item, str) is False and isinstance(item, int) is False:
        raise ValueError('`item` precisa ser do tipo int ou str.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_campo)
    app_interno.exists()

    try:
        # seleciona o item informado
        app_interno = TabControlWrapper(app_interno)
        app_interno.select(item).click_input()

        return True
    except:
        return False


def selecionar_em_campo_lista(
    caminho_campo: dict,
    item: int,
    selecionar: bool = True,
    performar: bool = False,
) -> bool:
    """Seleciona um dado em um elemento de lista em um objeto do \
        tipo Application.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.
        item: Valor em int da opção no campo de seleção \
            a ser selecionada.
        selecionar: Ativa seleção física direto no elemento informado.
        performar: Ativa clique físico direto no elemento informado.

    Returns:
        Retorna booleano, `True` caso a opção no campo de seleção seja \
            selecionada com sucesso, `False` caso a opção no campo de \
            seleção não seja selecionada com sucesso.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.
        ValueError: `item` precisa ser do tipo int.
        ValueError: `selecionar` precisa ser do tipo bool.
        ValueError: `performar` precisa ser do tipo bool.

    Examples:
        ...
    """

    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    if isinstance(item, int) is False:
        raise ValueError('`item` precisa ser do tipo int.')

    if isinstance(selecionar, bool) is False:
        raise ValueError('`selecionar` precisa ser do tipo bool.')

    if isinstance(performar, bool) is False:
        raise ValueError('`performar` precisa ser do tipo bool.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_campo)

    try:
        # seleciona o item informado
        if performar is True:
            app_interno.select(item=item, select=selecionar).click_input()
        else:
            app_interno.select(item=item, select=selecionar)

        return True
    except:
        return False


def selecionar_em_campo_selecao(caminho_campo: dict, item: str) -> str:
    """Seleciona uma opção em um elemento de seleção em um objeto do \
        tipo Application.

    Parameters:
        caminho_campo: Caminho do elemento na estrutura da aplicação \
            sendo manipulada.
        item: Valor em str da opção no campo de seleção \
            a ser selecionada.

    Returns:
        Retorna str, sendo o valor capturado do elemento informado após \
            a opção selecionada.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.
        ValueError: `item` precisa ser do tipo int.
        ValueError: `selecionar` precisa ser do tipo bool.
        ValueError: `performar` precisa ser do tipo bool.

    Examples:
        >>> selecionar_em_campo_selecao(
        ...     caminho_campo={
        ...         'window': {
        ...             'title': 'Character Map',
        ...             'child_window': {
        ...                 'title': 'Font :',
        ...                 'control_type': 'ComboBox',
        ...                 'auto_id': '105',
        ...             }
        ...         }
        ...     },
        ...     item='Arial'
        ... )
        'Arial'
    """

    # define estático como falso para trabalhar com elemento dinâmico
    if isinstance(caminho_campo, dict) is False:
        raise ValueError('`caminho_campo` precisa ser do tipo dict.')

    # localiza o elemento até o final da árvore de parantesco do app
    app_interno = _localizar_elemento(caminho_campo)
    app_interno.exists()

    # seleciona o item informado
    app_interno.select(item).click_input()

    # captura o texto do campo localizado
    valor_capturado = coletar_dado_selecionado(caminho_campo)

    # retorna o valor capturado
    return valor_capturado


def selecionar_menu(caminho_janela: dict, caminho_menu: str) -> bool:
    """Seleciona um item de menu conforme o caminho informado em um objeto \
        do tipo Application.

    Parameters:
        caminho_janela: Caminho da janela na estrutura da aplicação \
            sendo manipulada.
        caminho_menu: Caminho do menu na estrutura da aplicação \
            sendo manipulada. Deve ser informado no formato \
            'Menu1->Menu2->Menu3'.

    Returns:
        Retorna booleano, `True` caso a ação de selecionar o menu \
            tenha sucesso, `False` caso a ação de selecionar o menu \
            não tenha sucesso.

    Raises:
        TypeError: `caminho_janela` precisa ser do tipo dict.

    Raises:
        ValueError: `caminho_campo` precisa ser do tipo dict.
        ValueError: `item` precisa ser do tipo int.
        ValueError: `selecionar` precisa ser do tipo bool.
        ValueError: `performar` precisa ser do tipo bool.

    Examples:
        ...
    """

    # importa app para o escopo da função
    if isinstance(caminho_janela, dict) is False:
        raise ValueError('`caminho_janela` precisa ser do tipo dict.')

    try:
        # localiza o elemento até o final da árvore de parantesco do app
        app_interno = _localizar_elemento(caminho_janela)
        app_interno.exists()

        # percorre e clica no menu informado
        app_interno.menu_select(caminho_menu)

        # retorna verdadeiro confirmando a execução da ação
        return True
    except:
        return False


def simular_clique(
    botao: str,
    eixo_x: int,
    eixo_y: int,
    tipo_clique: str = 'unico',
) -> bool:
    """Simula clique físico do mouse conforme coordenadas X e Y informadas.

    Parameters:
        botao: valor str para o lado do botão a ser simulado. \
            Aceita valores 'ESQUERDO' e 'DIREITO'.
        eixo_x: valor int para a posição de coordenada X.
        eixo_y: valor int para a posição de coordenada Y.
        tipo_clique: valor str para o tipo de clique a ser simulado. \
            Aceita valores 'UNICO' e 'DUPLO'.

    Returns:
        Retorna booleano, `True` caso tenha sucesso ao simular o clique, \
        `False` caso não tenha sucesso ao simular o clique.

    Raises:
        ValueError: Informe um botão válido: esquerdo, direito.
        ValueError: Tipo de clique inválido, escolha entre único e duplo.
        ValueError: Coordenadas precisam ser do tipo inteiro .

    Examples:
        >>> simular_clique(
        ...     botao='ESQUERDO',
        ...     eixo_x=valor_eixo_x,
        ...     eixo_y=valor_eixo_y,
        ...     tipo_clique='UNICO',
        ... )
        True
    """

    # importa recursos do módulo mouse
    from pywinauto.mouse import click, double_click

    if not botao.upper() in ['ESQUERDO', 'DIREITO']:
        raise ValueError('Informe um botão válido: esquerdo, direito.')

    if not tipo_clique.upper() in ['UNICO', 'DUPLO']:
        raise ValueError(
            'Tipo de clique inválido, escolha entre único e duplo.'
        )

    if (not isinstance(eixo_x, int)) or (not isinstance(eixo_y, int)):
        raise ValueError('Coordenadas precisam ser do tipo inteiro .')

    if botao.upper() == 'ESQUERDO':
        botao = 'left'
    else:
        botao = 'right'

    try:
        if tipo_clique.upper() == 'UNICO':
            click(button=botao, coords=(eixo_x, eixo_y))
        else:
            double_click(button=botao, coords=(eixo_x, eixo_y))

        return True
    except Exception:
        return False


def simular_digitacao(
    texto: str,
    com_espaco: bool = True,
    com_tab: bool = False,
    com_linha_nova: bool = False,
) -> bool:
    """Simula digitação do teclado, performando o teclado real.

    Parameters:
        texto: valor str para o valor do texto a ser digitado. \
            Aceita valores 'ESQUERDO' e 'DIREITO'.
        com_espaco: valor booleano, `True` para digitar com espaços, \
            `False` para remover espaços ao digitar.
        com_tab: valor booleano, `True` para digitar tab ao final \
            da digitação, `False` para não digitar tab ao final \
            da digitação.
        com_linha_nova: valor booleano, `True` para digitar linha \
            nova ao final da digitação, `False` para não digitar linha \
            nova ao final da digitação.

    Returns:
        Retorna booleano, `True` caso tenha sucesso ao simular \
            a digitação, `False` caso não tenha sucesso ao simular \
            a digitação.

    Raises:
        ValueError: Informe os parâmetros com_espaco, com_tab e \
            com_linha_nova com valor boleano.
        ValueError: Informe um texto do tipo string.

    Examples:
        >>> simular_digitacao(
        ...     texto = 'FGHIJ',
        ...     com_espaco = True,
        ...     com_tab = False,
        ...     com_linha_nova = False,
        ... )
        True
    """

    # importa recursos do módulo keyboard
    from pywinauto.keyboard import send_keys

    if (
        (not isinstance(com_espaco, bool))
        or (not isinstance(com_tab, bool))
        or (not isinstance(com_linha_nova, bool))
    ):
        raise ValueError(
            """Informe os parâmetros com_espaco,
                com_tab e com_linha_nova com valor boleano"""
        )

    if not isinstance(texto, str):
        raise ValueError('Informe um texto do tipo string.')

    try:
        send_keys(
            keys=texto,
            with_spaces=com_espaco,
            with_tabs=com_tab,
            with_newlines=com_linha_nova,
        )

        return True
    except:
        return False
