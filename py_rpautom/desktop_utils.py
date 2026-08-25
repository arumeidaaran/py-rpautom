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
    """Cria o objeto ``Application`` do pywinauto e o guarda globalmente.

    Função interna que define a fundação de toda a automação desktop:
    escolhe o backend de acesso à interface e registra o objeto nas
    variáveis globais ``APP`` e ``ESTILO_APLICACAO``, consultadas pelas
    demais funções do módulo. É chamada por ``iniciar_app``,
    ``conectar_app`` e ``retornar_janelas_disponiveis``.

    Parâmetros:
        estilo_aplicacao: Backend de automação: 'win32' para aplicações
            clássicas do Windows, 'uia' para aplicações modernas.

    Retorna:
        Application: Objeto do pywinauto pronto para iniciar ou conectar
            um processo.
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
    """Vincula o objeto ``Application`` a um processo já em execução.

    Função interna que faz a conexão de fato: recria o objeto no backend
    informado e anexa-o ao processo do PID indicado, aguardando até o
    tempo limite caso a aplicação ainda esteja subindo. É a base de
    ``conectar_app`` e de ``encerrar_app``.

    Parâmetros:
        pid: PID do processo já em execução.
        tempo_espera: Tempo máximo de espera pela aplicação, em segundos.
        estilo_aplicacao: Backend de automação: 'win32' ou 'uia'.

    Retorna:
        Application: Objeto do pywinauto vinculado ao processo.
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
    """Percorre a árvore de elementos e devolve o controle apontado.

    Função interna que traduz o dicionário de caminho — a estrutura
    ``window`` / ``child_window`` aninhada usada em todo o módulo — na
    sequência de chamadas do pywinauto que desce da janela até o
    elemento desejado. Em cada nível considera os identificadores
    ``title``, ``control_type``, ``auto_id``, ``best_match`` e
    ``session``, e continua descendo enquanto houver ``child_window``.
    É o mecanismo compartilhado por praticamente todas as funções
    públicas do módulo.

    Parâmetros:
        caminho_campo: Caminho do elemento, em dicionário aninhado.

    Retorna:
        Application: Wrapper do elemento localizado, pronto para receber
            ações como clique, digitação e leitura.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é um dicionário.
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
    """Traz uma janela para frente e lhe dá o foco do teclado.

    Cliques e digitações simulados chegam à janela que está em foco, e
    não necessariamente àquela que o código pretende manipular — por
    isso ativar o foco costuma ser o passo anterior a qualquer
    interação, sobretudo depois que outra aplicação roubou a tela.
    Localiza a janela pelo título, sem exigir o dicionário de caminho.

    Parâmetros:
        nome_janela: Título exato da janela a ser focada.

    Retorna:
        bool: ``True`` se a janela foi focada, ``False`` se não foi
            encontrada ou o foco falhou.

    Exemplos:
        >>> ativar_foco(nome_janela='Sem título - Bloco de Notas')
        True
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
    """Verifica se uma caixa de seleção ou botão de opção está marcado.

    Permite ler o estado atual antes de agir, evitando o erro clássico
    de clicar em uma caixa já marcada e acabar desmarcando-a. As três
    opções de verificação existem porque componentes diferentes expõem
    o estado de formas distintas: se uma não responder, vale testar
    outra.

    Parâmetros:
        caminho_campo: Caminho do elemento, em dicionário aninhado.
        opcao_verificacao: Forma de leitura do estado: 'IS_CHECKED',
            'GET_CHECK_STATE' ou 'GET_SHOW_STATE'.

    Retorna:
        bool: ``True`` se o elemento está marcado, ``False`` caso
            contrário.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é dicionário, quando
            ``opcao_verificacao`` não é texto, ou quando a opção
            informada não é uma das três aceitas.

    Exemplos:
        >>> botao_esta_marcado(caminho_campo=caminho_checkbox)
        False
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
    """Captura a imagem de um elemento da tela e a devolve em bytes.

    Fotografa apenas o elemento indicado, não a tela inteira, o que
    gera evidências mais objetivas e arquivos menores. As coordenadas
    permitem recortar uma região específica dentro do elemento — útil
    para isolar um trecho de tabela ou um selo de status. Devolve os
    bytes crus, que podem ser gravados com
    ``python_utils.criar_arquivo_texto`` no modo binário ou enviados
    diretamente a um serviço de OCR.

    Parâmetros:
        caminho_campo: Caminho do elemento, em dicionário aninhado.
        coordenadas: Recorte a capturar, na ordem esquerda, cima,
            direita, baixo. ``None`` captura o elemento inteiro.

    Retorna:
        bytes: Conteúdo da imagem capturada.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é dicionário, quando
            ``coordenadas`` não é tupla, ou quando a tupla não possui
            exatamente 4 posições.

    Exemplos:
        >>> imagem = capturar_imagem(caminho_campo=caminho_tabela)
        >>> type(imagem)
        <class 'bytes'>
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
    """Devolve todas as propriedades conhecidas de um elemento.

    É a principal ferramenta de investigação do módulo: mostra de uma
    vez classe, textos, posição na tela, visibilidade e se o elemento
    está habilitado. Serve tanto para descobrir por qual identificador
    localizar um elemento durante o desenvolvimento quanto para tomar
    decisões em tempo de execução — a chave ``rectangle`` fornece as
    coordenadas usadas por ``simular_clique`` e ``mover_mouse``.

    Parâmetros:
        caminho_campo: Caminho do elemento, em dicionário aninhado.

    Retorna:
        dict: Propriedades do elemento, entre elas ``class_name``,
            ``texts``, ``rectangle``, ``is_visible``, ``is_enabled`` e
            ``automation_id``.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é um dicionário.

    Exemplos:
        >>> propriedades = capturar_propriedade_elemento(caminho_campo)
        >>> propriedades['is_enabled']
        True
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
    """Lê o texto exibido por um elemento da aplicação.

    Devolve uma lista porque um mesmo controle pode conter várias
    linhas — uma caixa de texto com múltiplas linhas ou uma lista
    devolvem um item por linha. Para um rótulo ou botão comum, o texto
    está na primeira posição. É a função de leitura mais usada do
    módulo, tanto para extrair dados quanto para conferir mensagens da
    aplicação.

    Parâmetros:
        caminho_campo: Caminho do elemento, em dicionário aninhado.

    Retorna:
        list[str]: Texto do elemento, um item por linha.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é um dicionário.

    Exemplos:
        >>> capturar_texto(caminho_campo=caminho_rotulo)
        ['Arquivo']
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
    """Clica em um elemento da aplicação.

    Oferece dois modos, e a escolha entre eles resolve boa parte dos
    problemas de automação desktop: o clique padrão envia a mensagem de
    clique diretamente ao controle, funcionando mesmo com a janela
    minimizada ou coberta; o modo ``performar`` move o ponteiro e clica
    de verdade, necessário em componentes que só reagem a eventos reais
    do mouse. O índice permite alcançar um filho específico quando o
    caminho aponta para um grupo de elementos.

    Parâmetros:
        caminho_campo: Caminho do elemento, em dicionário aninhado.
        performar: Quando ``True``, executa clique físico com o
            ponteiro; quando ``False``, envia o clique ao controle.
        indice: Posição do elemento filho a ser clicado, contada a
            partir de 0. ``None`` clica no próprio elemento.

    Retorna:
        bool: ``True`` quando o clique é executado.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é dicionário,
            ``performar`` não é booleano ou ``indice`` não é inteiro.

    Exemplos:
        >>> clicar(caminho_campo=caminho_botao, performar=True)
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
    """Lista a estrutura de elementos existente sob o caminho informado.

    É a função de exploração usada durante o desenvolvimento: revela os
    elementos filhos disponíveis e, principalmente, os identificadores
    que devem ser usados para alcançá-los — exatamente o que se precisa
    para montar o dicionário de caminho das demais funções. Cada linha
    do retorno traz um trecho da árvore de controles da aplicação. Não
    costuma ser usada em produção.

    Parâmetros:
        caminho_elemento: Caminho do elemento a partir do qual listar,
            em dicionário aninhado.

    Retorna:
        list[str]: Linhas da árvore de controles, incluindo classes,
            textos, coordenadas e sugestões de identificação.

    Exceções:
        ValueError: Quando ``caminho_elemento`` não é um dicionário.

    Exemplos:
        >>> for linha in coletar_arvore_elementos(caminho_janela):
        ...     print(linha)
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
    """Lê a opção atualmente escolhida em um campo de seleção.

    Aplica-se a listas suspensas e caixas de combinação: devolve o
    texto que está visível no campo, e não a lista de opções — para
    essa, use ``coletar_dados_selecao``. Serve para conferir se uma
    seleção anterior surtiu efeito e para capturar o valor padrão antes
    de alterá-lo.

    Parâmetros:
        caminho_campo: Caminho do campo de seleção, em dicionário
            aninhado.

    Retorna:
        str: Texto da opção selecionada.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é um dicionário.

    Exemplos:
        >>> coletar_dado_selecionado(caminho_campo=caminho_combo_fonte)
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
    """Lista todas as opções disponíveis em um campo de seleção.

    Permite validar que a opção desejada existe antes de tentar
    selecioná-la e descobrir a grafia exata que a aplicação usa —
    ``selecionar_em_campo_selecao`` exige o texto idêntico ao da lista.
    Também serve para percorrer todas as opções de um filtro.

    Parâmetros:
        caminho_campo: Caminho do campo de seleção, em dicionário
            aninhado.

    Retorna:
        list[str]: Texto de cada opção disponível, na ordem da lista.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é um dicionário.

    Exemplos:
        >>> coletar_dados_selecao(caminho_campo=caminho_combo_uf)
        ['SP', 'RJ', 'MG']
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
    """Informa se a janela está normal, minimizada ou maximizada.

    Traduz o código de estado do Windows para um texto legível. Serve
    para decidir se é preciso restaurar ou maximizar antes de
    interagir: janelas minimizadas não recebem cliques físicos, e o
    layout de uma janela maximizada pode diferir do layout restaurado.

    Parâmetros:
        caminho_janela: Caminho da janela, em dicionário aninhado.

    Retorna:
        str: 'normal', 'minimizado', 'maximizado' ou 'não identificado'
            quando o estado não corresponde a nenhum dos três.

    Exceções:
        ValueError: Quando ``caminho_janela`` não é um dicionário.

    Exemplos:
        >>> coletar_situacao_janela(caminho_janela=caminho_bloco_notas)
        'maximizado'
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
    """Assume o controle de uma aplicação que já está em execução.

    Alternativa a ``iniciar_app`` para os casos em que o programa não
    deve ser aberto pelo robô: um sistema que fica aberto o dia todo,
    uma janela criada por outra aplicação, um pop-up do navegador.
    Obtenha o PID com ``python_utils.coletar_pid``. A partir daqui, as
    demais funções do módulo operam sobre essa aplicação.

    Parâmetros:
        pid: PID do processo já em execução.
        tempo_espera: Tempo máximo de espera pela aplicação, em
            segundos.
        estilo_aplicacao: Backend de automação: 'win32' para aplicações
            clássicas do Windows, 'uia' para aplicações modernas.

    Retorna:
        int: PID da aplicação agora sob controle da automação.

    Exemplos:
        >>> conectar_app(pid=33144, estilo_aplicacao='win32')
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
    """Escreve um texto em um campo de edição da aplicação.

    Substitui todo o conteúdo do campo de uma vez, em vez de acrescentar
    ao que já existe — não é preciso limpá-lo antes. O texto é entregue
    diretamente ao controle, sem simular teclas, o que é rápido e
    confiável; campos com máscara ou validação a cada tecla podem exigir
    ``simular_digitacao``. Ao final devolve o conteúdo do campo, o que
    permite confirmar a escrita.

    Parâmetros:
        caminho_campo: Caminho do campo de edição, em dicionário
            aninhado.
        valor: Texto a ser escrito.

    Retorna:
        str: Conteúdo do campo após a escrita, em representação de lista
            de linhas.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é um dicionário.

    Exemplos:
        >>> digitar(caminho_campo=caminho_campo_busca, valor='ABCDE')
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
    """Fecha a aplicação correspondente ao PID informado.

    O modo suave pede que o programa se encerre, dando-lhe a chance de
    salvar e liberar recursos; o modo forçado derruba o processo
    imediatamente, perdendo o que não foi gravado. Use o forçado apenas
    quando a aplicação travou. Chamar ao final de cada execução evita o
    acúmulo de processos órfãos entre rodadas do robô.

    Parâmetros:
        pid: PID do processo a ser encerrado.
        forcar: Quando ``True``, derruba o processo imediatamente;
            quando ``False``, solicita o encerramento normal.
        tempo_espera: Tempo máximo de espera pela conexão ao processo,
            em segundos.

    Retorna:
        bool: ``True`` quando o encerramento é solicitado.

    Exemplos:
        >>> encerrar_app(pid=39440, forcar=True)
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
    """Informa se a janela indicada está em primeiro plano.

    O foco determina para onde vão as teclas e os cliques físicos.
    Consultar antes de simular digitação evita o erro difícil de
    diagnosticar em que o texto acaba digitado na janela errada. Para
    corrigir a situação, use ``ativar_foco``.

    Parâmetros:
        nome_janela: Título exato da janela a ser verificada.

    Retorna:
        bool: ``True`` se a janela está com foco, ``False`` caso
            contrário.

    Exemplos:
        >>> esta_com_foco(nome_janela='Sem título - Bloco de Notas')
        True
    """

    # importa app para o escopo da função
    global APP

    # inicializa APP para uma variável interna
    app_interno = APP

    # retorna a situacao atual de foco da janela
    return app_interno.window(title=nome_janela).has_focus()


def esta_visivel(nome_janela: dict) -> str:
    """Informa se a janela está visível na tela.

    Simplifica ``coletar_situacao_janela`` para a pergunta que
    normalmente interessa: dá para interagir com esta janela agora?
    Janelas normais e maximizadas contam como visíveis; minimizadas,
    não. Quando o retorno indicar janela não visível, use
    ``restaurar_janela`` antes de prosseguir.

    Parâmetros:
        nome_janela: Caminho da janela, em dicionário aninhado.

    Retorna:
        str: 'visivel', 'não visível' ou 'não identificado'.

    Exemplos:
        >>> esta_visivel(nome_janela=caminho_bloco_notas)
        'visivel'
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
    """Fecha uma janela específica da aplicação.

    Age sobre uma janela apenas, não sobre o processo inteiro — é o
    recurso para dispensar caixas de diálogo, avisos e janelas
    auxiliares sem derrubar o sistema principal. Se a janela pedir
    confirmação ao fechar, o pop-up permanece aberto e precisa ser
    tratado em seguida. Para encerrar a aplicação toda, use
    ``encerrar_app``.

    Parâmetros:
        caminho_janela: Caminho da janela, em dicionário aninhado.

    Retorna:
        bool: ``True`` quando o fechamento é solicitado.

    Exceções:
        ValueError: Quando ``caminho_janela`` não é um dicionário.

    Exemplos:
        >>> fechar_janela(caminho_janela=caminho_dialogo)
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
    """Abre uma aplicação desktop e a coloca sob controle da automação.

    É o ponto de partida da automação desktop: executa o programa e,
    em vez de devolver o controle de imediato, aguarda a janela atingir
    a condição informada — proteção necessária porque uma aplicação
    recém-iniciada leva algum tempo até responder. Devolve o PID, que
    identifica essa instância nas demais funções. Escolher o backend
    correto é decisivo: 'win32' para programas clássicos do Windows,
    'uia' para aplicações modernas; na dúvida, teste os dois.

    Parâmetros:
        executavel: Caminho completo do programa a ser aberto, com os
            argumentos de linha de comando, se houver.
        estilo_aplicacao: Backend de automação: 'win32' ou 'uia'.
        esperar: Tupla com a condição aguardada e o tempo limite em
            segundos. A condição pode ser 'exists', 'visible',
            'enabled', 'ready' ou 'active'. Vazia usa ('ready', 10).
        inverter: Quando ``False``, aguarda a condição ocorrer; quando
            ``True``, aguarda a condição deixar de valer.
        ocioso: Quando ``True``, espera a aplicação sair do estado
            ocioso antes de seguir.

    Retorna:
        int: PID do processo iniciado.

    Exemplos:
        >>> iniciar_app(
        ...     executavel='notepad.exe',
        ...     estilo_aplicacao='uia',
        ...     esperar=('ready', 10),
        ... )
        40944
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


def janela_existente(pid, nome_janela) -> bool:
    """Informa se a aplicação possui uma janela com o título indicado.

    Serve para descobrir em que ponto do fluxo a aplicação está: se o
    pop-up de erro apareceu, se a tela de resultado já abriu, se o
    diálogo de salvar surgiu. A comparação é exata — títulos que mudam
    a cada execução, com data ou número de registro, não são
    encontrados. Para conhecer os títulos disponíveis, use
    ``retornar_janelas_disponiveis``.

    Parâmetros:
        pid: PID do processo da aplicação.
        nome_janela: Título exato da janela procurada.

    Retorna:
        bool: ``True`` se existe uma janela com esse título, ``False``
            caso contrário.

    Exemplos:
        >>> janela_existente(pid=39440, nome_janela='Erro')
        False
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
    r"""Navega até uma pasta em uma caixa de diálogo com árvore de diretórios.

    Trata o caso específico das janelas antigas de "Procurar pasta", em
    que a escolha é feita em uma árvore, e não em um campo de caminho.
    Percorre a árvore até o diretório informado, clica nele e confirma
    em OK, resolvendo em uma chamada uma navegação que exigiria vários
    cliques. Nunca lança exceção: devolve ``False`` quando a navegação
    falha.

    Parâmetros:
        caminho_janela: Caminho da janela de diálogo, em dicionário
            aninhado.
        caminho_diretorio: Caminho da pasta a ser selecionada dentro da
            árvore.

    Retorna:
        bool: ``True`` se a pasta foi selecionada e confirmada,
            ``False`` em caso de falha.

    Exemplos:
        >>> localizar_diretorio_em_treeview(caminho_dialogo,
        ...                                 'Este Computador\Documentos')
        True
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
    estilo_aplicacao='win32',
) -> bool:
    """Verifica se um elemento existe na aplicação sob controle.

    Funciona como teste de presença antes de agir, evitando exceções ao
    tentar clicar ou ler algo que ainda não apareceu. É também a forma
    de conferir se o dicionário de caminho montado durante o
    desenvolvimento realmente alcança o elemento pretendido.

    Parâmetros:
        caminho_campo: Caminho do elemento, em dicionário aninhado.
        estilo_aplicacao: Backend de automação: 'win32' ou 'uia'.

    Retorna:
        bool: ``True`` se o elemento existe, ``False`` caso contrário.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é um dicionário.

    Exemplos:
        >>> localizar_elemento(caminho_campo=caminho_botao_ok)
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
    """Maximiza a janela da aplicação.

    Amplia a área útil, o que reduz a rolagem e evita que elementos
    fiquem fora da tela — situação em que cliques físicos falham.
    Também estabiliza as coordenadas entre execuções, importante para
    ``simular_clique``, já que a posição dos elementos varia conforme o
    tamanho da janela.

    Parâmetros:
        caminho_janela: Caminho da janela, em dicionário aninhado.

    Retorna:
        bool: ``True`` se a janela foi maximizada, ``False`` em caso de
            falha.

    Exceções:
        ValueError: Quando ``caminho_janela`` não é um dicionário.

    Exemplos:
        >>> maximizar_janela(caminho_janela=caminho_bloco_notas)
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
    """Minimiza a janela da aplicação.

    Tira a janela da frente sem fechá-la, liberando a tela para outra
    aplicação ou para o usuário. Atenção: janelas minimizadas não
    recebem cliques físicos nem digitação simulada — antes de voltar a
    interagir, use ``restaurar_janela``.

    Parâmetros:
        caminho_janela: Caminho da janela, em dicionário aninhado.

    Retorna:
        bool: ``True`` se a janela foi minimizada, ``False`` em caso de
            falha.

    Exceções:
        ValueError: Quando ``caminho_janela`` não é um dicionário.

    Exemplos:
        >>> minimizar_janela(caminho_janela=caminho_bloco_notas)
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
    """Move o ponteiro do mouse para as coordenadas indicadas.

    Posiciona o cursor sem clicar, o que basta para acionar menus e
    dicas que se abrem ao passar o mouse. As coordenadas são absolutas
    na tela, contadas do canto superior esquerdo — obtenha as de um
    elemento pela chave ``rectangle`` de
    ``capturar_propriedade_elemento``, já que valores fixos quebram
    quando a resolução ou a posição da janela muda.

    Parâmetros:
        eixo_x: Coordenada horizontal, em pixels.
        eixo_y: Coordenada vertical, em pixels.

    Retorna:
        bool: ``True`` se o ponteiro foi movido, ``False`` em caso de
            falha.

    Exceções:
        ValueError: Quando alguma coordenada não é um número inteiro.

    Exemplos:
        >>> mover_mouse(eixo_x=961, eixo_y=562)
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
    """Restaura a janela ao tamanho normal, saindo de minimizada ou maximizada.

    É o passo necessário para voltar a interagir com uma janela
    minimizada, que não recebe cliques nem digitação. Também devolve a
    janela ao tamanho intermediário quando ela está maximizada.

    Parâmetros:
        caminho_janela: Caminho da janela, em dicionário aninhado.

    Retorna:
        bool: ``True`` quando a restauração é solicitada.

    Exceções:
        ValueError: Quando ``caminho_janela`` não é um dicionário.

    Exemplos:
        >>> restaurar_janela(caminho_janela=caminho_bloco_notas)
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
    estilo_aplicacao='win32',
) -> list[str]:
    """Lista os títulos de todas as janelas abertas por uma aplicação.

    Mostra o que a aplicação tem na tela naquele instante, o que
    resolve dois problemas frequentes: descobrir o título exato exigido
    por ``ativar_foco`` e ``janela_existente``, e identificar pop-ups
    inesperados que travaram o fluxo. Como reconecta a aplicação, pode
    ser chamada mesmo antes de ``conectar_app``.

    Parâmetros:
        pid: PID do processo da aplicação.
        estilo_aplicacao: Backend de automação: 'win32' ou 'uia'.

    Retorna:
        list[str]: Título de cada janela aberta pelo processo.

    Exemplos:
        >>> retornar_janelas_disponiveis(pid=24728, estilo_aplicacao='uia')
        ['Sem título - Bloco de Notas', 'Salvar como']
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
    """Troca a aba ativa em um controle de abas.

    Aplicações desktop distribuem os campos em abas, e os controles de
    uma aba inativa existem na árvore mas não podem ser manipulados —
    tentar preenchê-los falha silenciosamente ou gera erro. Esta função
    faz a troca antes do preenchimento. A aba pode ser indicada pelo
    título ou pela posição. Nunca lança exceção na troca em si: devolve
    ``False``.

    Parâmetros:
        caminho_campo: Caminho do controle de abas, em dicionário
            aninhado.
        item: Título da aba ou seu índice, contado a partir de 0.

    Retorna:
        bool: ``True`` se a aba foi selecionada, ``False`` em caso de
            falha.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é dicionário ou
            ``item`` não é texto nem inteiro.

    Exemplos:
        >>> selecionar_aba(caminho_campo=caminho_abas, item='Endereço')
        True
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
    """Marca ou desmarca um item em um campo de lista, pela posição.

    Diferentemente das listas suspensas, campos de lista mostram várias
    linhas ao mesmo tempo e frequentemente aceitam seleção múltipla —
    daí o parâmetro ``selecionar``, que permite tanto marcar quanto
    desmarcar. O item é indicado pela posição, e não pelo texto: use
    ``coletar_dados_selecao`` para descobrir o índice correto.

    Parâmetros:
        caminho_campo: Caminho do campo de lista, em dicionário
            aninhado.
        item: Posição do item, contada a partir de 0.
        selecionar: ``True`` marca o item, ``False`` desmarca.
        performar: Quando ``True``, acrescenta um clique físico sobre o
            item, para componentes que exigem interação real.

    Retorna:
        bool: ``True`` se a operação foi executada, ``False`` em caso de
            falha.

    Exceções:
        ValueError: Quando algum parâmetro é informado com tipo
            diferente do esperado.

    Exemplos:
        >>> selecionar_em_campo_lista(caminho_campo=caminho_lista, item=2)
        True
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
    """Escolhe uma opção em uma lista suspensa, pelo texto.

    Abre a lista, clica na opção cujo texto corresponde ao informado e
    devolve o valor que ficou selecionado — o retorno permite confirmar
    que a escolha foi aceita, sem precisar de uma leitura à parte. O
    texto precisa ser idêntico ao da lista; consulte
    ``coletar_dados_selecao`` em caso de dúvida.

    Parâmetros:
        caminho_campo: Caminho do campo de seleção, em dicionário
            aninhado.
        item: Texto da opção, exatamente como aparece na lista.

    Retorna:
        str: Opção efetivamente selecionada após a operação.

    Exceções:
        ValueError: Quando ``caminho_campo`` não é um dicionário.

    Exemplos:
        >>> selecionar_em_campo_selecao(caminho_campo=caminho_combo,
        ...                             item='Arial')
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
    """Aciona um item de menu percorrendo o caminho informado.

    Executa em uma única chamada a sequência de cliques que abriria o
    menu nível a nível — Arquivo, depois Salvar como, e assim por
    diante —, o que é mais rápido e menos frágil do que localizar cada
    item separadamente. Os níveis são separados por ``->`` e devem usar
    os nomes exatos exibidos na aplicação. Nunca lança exceção na
    navegação: devolve ``False``.

    Parâmetros:
        caminho_janela: Caminho da janela que possui o menu, em
            dicionário aninhado.
        caminho_menu: Caminho do item no formato
            'Menu1->Menu2->Menu3'.

    Retorna:
        bool: ``True`` se o item foi acionado, ``False`` em caso de
            falha.

    Exceções:
        ValueError: Quando ``caminho_janela`` não é um dicionário.

    Exemplos:
        >>> selecionar_menu(caminho_janela=caminho_janela,
        ...                 caminho_menu='Arquivo->Salvar como')
        True
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
    """Executa um clique físico do mouse em coordenadas da tela.

    Clica em uma posição, e não em um elemento: é o último recurso para
    componentes que a automação não consegue identificar — telas
    desenhadas graficamente, controles de terceiros, aplicações
    remotas. Por depender de coordenadas absolutas, quebra quando a
    resolução ou a posição da janela muda; sempre que possível,
    prefira ``clicar``. Obtenha as coordenadas pela chave ``rectangle``
    de ``capturar_propriedade_elemento``.

    Parâmetros:
        botao: Botão do mouse: 'ESQUERDO' ou 'DIREITO'.
        eixo_x: Coordenada horizontal, em pixels.
        eixo_y: Coordenada vertical, em pixels.
        tipo_clique: 'UNICO' para um clique, 'DUPLO' para duplo clique.

    Retorna:
        bool: ``True`` se o clique foi executado, ``False`` em caso de
            falha.

    Exceções:
        ValueError: Quando o botão ou o tipo de clique não é um dos
            valores aceitos, ou quando as coordenadas não são inteiras.

    Exemplos:
        >>> simular_clique(botao='ESQUERDO', eixo_x=961, eixo_y=562)
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
    """Digita um texto acionando o teclado de verdade.

    O texto vai para a janela que estiver em foco, e não para um
    elemento específico — garanta o foco com ``ativar_foco`` antes de
    chamar. É a alternativa a ``digitar`` para campos que só reagem a
    teclas reais, como os que têm máscara ou autocompletar, e a única
    forma de enviar teclas especiais: a sintaxe do pywinauto reconhece
    ``{ENTER}``, ``{TAB}``, ``{F5}`` e combinações como ``^a`` para
    Ctrl+A.

    Parâmetros:
        texto: Texto a ser digitado. Aceita códigos de teclas especiais
            entre chaves.
        com_espaco: Quando ``True``, digita os espaços do texto; quando
            ``False``, os remove.
        com_tab: Quando ``True``, interpreta as tabulações do texto como
            a tecla Tab.
        com_linha_nova: Quando ``True``, interpreta as quebras de linha
            do texto como a tecla Enter.

    Retorna:
        bool: ``True`` se a digitação foi executada, ``False`` em caso
            de falha.

    Exceções:
        ValueError: Quando ``texto`` não é uma string ou quando algum
            dos demais parâmetros não é booleano.

    Exemplos:
        >>> simular_digitacao(texto='FGHIJ{TAB}')
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
