# Módulo web_utils (web_utils.py)
___

Para realizar automações em navegadores e interagir com páginas web, utilize este módulo. Abaixo estão detalhadas as funções disponíveis e suas utilizações.

## Abrindo uma nova janela

A função ``abrir_janela`` cria uma nova janela ou aba sem substituir a que está em uso. O navegador decide qual dos dois formatos será aberto de acordo com seu próprio comportamento e suas configurações.

O parâmetro ``url`` é opcional. Quando informado, a nova janela já é aberta com o endereço solicitado; quando omitido, ela é criada vazia. Após a abertura, utilize as funções de coleta e troca de contexto caso seja necessário identificar a nova janela e passar a automação para ela.

### função abrir_janela
:::web_utils.abrir_janela

___

## Abrindo uma página

A função ``abrir_pagina`` carrega uma URL na janela que está atualmente sob controle da automação. Diferentemente de ``abrir_janela``, ela não cria outro contexto: a navegação acontece na janela ou aba ativa.

Informe o endereço completo no parâmetro ``url``. Erros do webdriver, endereços inválidos ou falhas de navegação são repassados ao chamador.

### função abrir_pagina
:::web_utils.abrir_pagina

___

## Atualizando a página

A função ``atualizar_pagina`` solicita ao navegador que recarregue o endereço atual. Ela atua sobre a janela ou aba que estiver selecionada naquele momento e não troca o contexto da automação.

A função não possui parâmetros nem retorno. Caso o navegador não esteja iniciado ou a atualização falhe, a exceção produzida pelo webdriver é repassada.

### função atualizar_pagina
:::web_utils.atualizar_pagina

___

## Aguardando um elemento ou estado do navegador

Páginas web frequentemente carregam ou modificam seus elementos de forma assíncrona. A função ``aguardar_elemento`` suspende a execução até que uma condição seja satisfeita ou que o limite definido em ``tempo`` seja alcançado.

O parâmetro ``comportamento_esperado`` determina o que será aguardado. Dependendo da condição escolhida, ``identificador`` pode representar um seletor, texto, URL, título ou quantidade, e ``valor`` fornece dados complementares como o conteúdo de um atributo ou o estado booleano esperado. ``tipo_elemento`` informa como o seletor deve ser interpretado.

Também é possível aguardar elementos dentro de Shadow DOM por meio de ``elemento_shadowroot`` e ``tipo_elemento_shadowroot``. A função absorve erros e timeouts: retorna ``True`` quando a condição é atendida e ``False`` quando a espera falha, em vez de levantar a exceção ao chamador.

### função aguardar_elemento
:::web_utils.aguardar_elemento

___

## Alterando um atributo de um elemento

A função ``alterar_atributo`` modifica diretamente uma propriedade de um elemento por meio de JavaScript. O elemento é localizado e centralizado antes da alteração, e o valor obtido depois da operação é devolvido para permitir a conferência do resultado.

A implementação trata seletores ``XPATH`` e ``CSS_SELECTOR`` de maneiras distintas ao montar o script. Por isso, ``tipo_elemento`` deve corresponder ao formato de ``seletor``. Como a alteração ocorre no DOM, ela pode não disparar os mesmos eventos que uma interação real de teclado ou mouse.

### função alterar_atributo
:::web_utils.alterar_atributo

___

## Autenticando o navegador

Algumas credenciais são solicitadas em uma janela nativa do navegador, fora do HTML e, portanto, fora do alcance do Selenium. A função ``autenticar_navegador`` trata esse caso conectando-se ao processo do navegador e manipulando o pop-up com os recursos de automação desktop da biblioteca.

É necessário informar o ``pid_aplicacao`` e os caminhos hierárquicos da janela, dos campos de usuário e senha e do botão de confirmação. Esses caminhos seguem a mesma estrutura usada pelo módulo ``desktop_utils``. O parâmetro ``estilo_aplicacao`` seleciona o backend ``uia`` ou ``win32``.

Os tipos dos argumentos são validados antes da interação. A função retorna ``True`` quando encontra a janela e envia as credenciais, ou ``False`` quando o pop-up informado não é localizado.

### função autenticar_navegador
:::web_utils.autenticar_navegador

___

## Baixando um arquivo

A função ``baixar_arquivo`` realiza uma requisição HTTP e grava o conteúdo recebido no caminho indicado. ``caminho_destino`` deve incluir tanto a pasta quanto o nome e a extensão do arquivo; a função não deduz o nome a partir da URL.

Os parâmetros de conexão permitem controlar validação SSL, timeout, proxy, cabeçalhos e autenticação HTTP básica. Com ``stream=True``, o corpo da resposta é transferido para o arquivo sem precisar ser carregado integralmente na memória.

O arquivo é gravado antes da avaliação do status HTTP. O retorno será ``True`` apenas para status 200 e ``False`` para outros status, ainda que algum conteúdo tenha sido salvo. Falhas de rede ou de escrita não são convertidas em ``False``: suas exceções são repassadas.

### função baixar_arquivo
:::web_utils.baixar_arquivo

___

## Baixando o webdriver

Para que o Selenium controle um navegador, é necessário um webdriver compatível com a versão instalada. A função ``baixar_webdriver`` procura esse executável no cache da biblioteca e, quando necessário, consulta os metadados do fabricante, baixa e descompacta a versão adequada.

``nome_navegador`` aceita Chrome, Edge ou Firefox, enquanto ``versao_navegador`` deve conter os componentes da versão em uma lista. Proxy e autenticação HTTP básica podem ser fornecidos para os acessos externos usados na consulta e no download.

O retorno é um objeto ``webdriver_info``. Além do caminho do executável encontrado ou baixado, ele reúne informações como URL, nome, plataforma, cabeçalhos e versão, que podem ser usadas na preparação ou no diagnóstico da inicialização.

### função baixar_webdriver
:::web_utils.baixar_webdriver

___

## Centralizando um elemento

A função ``centralizar_elemento`` rola a página até posicionar o elemento informado no centro da área visível do navegador. Isso é útil antes de cliques, leituras ou capturas quando o elemento está fora da viewport ou encoberto pelas extremidades da página.

O seletor pode ser informado como ``CSS_SELECTOR`` ou ``XPATH``. A função não devolve valor e repassa falhas de localização ou incompatibilidades entre o seletor e o tipo escolhido.

### função centralizar_elemento
:::web_utils.centralizar_elemento

___

## Capturando uma janela em imagem

A função ``capturar_janela_em_imagem`` registra o conteúdo visível da janela automatizada e salva a captura em formato PNG. Ela é útil para evidências de execução, depuração e validação visual do estado da página.

``imagem`` pode ser uma string ou um objeto ``Path``, mas o nome precisa terminar em ``.png``; caso contrário, a função levanta ``ValueError``. O retorno é o mesmo booleano produzido pelo método de screenshot do webdriver, indicando se o arquivo foi salvo.

### função capturar_janela_em_imagem
:::web_utils.capturar_janela_em_imagem

___

## Clicando em um elemento

A função ``clicar_elemento`` localiza, centraliza e aciona o clique nativo do Selenium sobre um elemento. Para componentes encapsulados em Shadow DOM, informe também o seletor do host em ``elemento_shadowroot`` e seu tipo em ``tipo_elemento_shadowroot``.

Por padrão, depois do clique a função aguarda o carregamento da página e retorna ``True``. Quando ``com_alerta=True``, o fluxo muda para tratar alertas: ``lista_id_alertas`` define, em ordem, ações como leitura de texto, confirmação ou cancelamento, e ``tempo_alerta`` limita a espera de cada alerta.

Nesse modo, o retorno é o último texto coletado, ou uma string vazia se nenhum alerta for encontrado. A lista recebida é consumida durante o processamento; portanto, evite reutilizar a mesma instância quando seu conteúdo precisar ser preservado.

### função clicar_elemento
:::web_utils.clicar_elemento

___

## Coletando um atributo

A função ``coletar_atributo`` permite consultar três tipos de informação de um elemento. Com ``get_attribute``, coleta-se o valor exposto pelo Selenium; com ``get_dom_attribute``, lê-se especificamente o atributo presente no DOM; e com ``value_of_css_property``, obtém-se o valor calculado de uma propriedade CSS.

O significado de ``atributo`` depende do método escolhido: pode ser, por exemplo, ``value``, ``href`` ou ``display``. Antes da coleta, o elemento é localizado e centralizado. Um método fora das três opções aceitas resulta em ``ValueError``.

### função coletar_atributo
:::web_utils.coletar_atributo

___

## Coletando o identificador da janela

Cada janela ou aba controlada pelo Selenium possui um identificador único, chamado handle. A função ``coletar_id_janela`` devolve o handle do contexto atual, permitindo guardá-lo antes de abrir ou acessar outras janelas.

Esse valor pode ser usado posteriormente em operações que preservam uma janela específica ou retomam seu contexto. Caso não exista uma janela ativa, a exceção do webdriver é repassada.

### função coletar_id_janela
:::web_utils.coletar_id_janela

___

## Coletando o nome do navegador atual

A função ``coletar_nome_navegador_atual`` consulta as capacidades da instância ativa e devolve o nome do navegador sob automação. Esse dado pode ser usado quando um fluxo precisa adotar comportamentos específicos para Chrome, Edge ou Firefox.

Ela depende de uma instância já iniciada e não recebe parâmetros. Se não houver navegador disponível, a falha é repassada ao chamador.

### função coletar_nome_navegador_atual
:::web_utils.coletar_nome_navegador_atual

___

## Coletando os identificadores das janelas

A função ``coletar_todas_ids_janelas`` devolve uma lista com os handles de todas as janelas e abas conhecidas pela instância atual. A posição de cada handle na lista pode ser usada nas operações que trabalham com índice, enquanto o próprio handle identifica a janela de maneira estável.

A função apenas coleta os identificadores: ela não altera a janela ativa. Se o navegador não estiver iniciado, a exceção correspondente é repassada.

### função coletar_todas_ids_janelas
:::web_utils.coletar_todas_ids_janelas

___

## Contando elementos

A função ``contar_elementos`` localiza todos os elementos que correspondem ao seletor e devolve a quantidade encontrada como inteiro. Ela é adequada para validar tabelas, listas, resultados de pesquisa ou qualquer estrutura repetida no HTML.

Ao contrário de ``procurar_elemento``, a função não devolve apenas um indicador booleano. Antes de contar, ela tenta localizar e centralizar uma ocorrência; por isso, a ausência de elementos pode provocar uma exceção em vez de produzir zero. Quando a busca é bem-sucedida, o inteiro retornado informa quantas ocorrências estavam presentes naquele momento.

### função contar_elementos
:::web_utils.contar_elementos

___

## Encerrando o navegador

Para finalizar uma automação e liberar os recursos do webdriver, utilize ``encerrar_navegador``. A função percorre as janelas abertas, fecha-as e, em seguida, encerra a instância do navegador.

Falhas durante esse processo são absorvidas. Assim, o retorno é ``True`` quando o encerramento é concluído e ``False`` quando alguma etapa produz erro, sem que a exceção seja repassada ao chamador.

### função encerrar_navegador
:::web_utils.encerrar_navegador

___

## Escrevendo em um elemento

A função ``escrever_em_elemento`` localiza um elemento editável e envia o conteúdo informado em ``texto``. Antes da digitação, ela tenta centralizar o elemento; se apenas essa centralização falhar, o fluxo ainda prossegue com a localização e a escrita.

Com ``performar=False``, o texto é enviado diretamente pelo elemento do Selenium. Com ``performar=True``, a função usa ``ActionChains`` para clicar no campo, limpá-lo e então digitar, aproximando a sequência de uma interação de usuário. Ao final, aguarda o carregamento da página.

### função escrever_em_elemento
:::web_utils.escrever_em_elemento

___

## Esperando a página carregar

A função ``esperar_pagina_carregar`` bloqueia a continuidade do fluxo até que o navegador informe que o documento atual terminou de carregar. Ela é usada internamente depois de várias operações de navegação e interação, mas também pode ser chamada diretamente quando o processo depende da conclusão da página.

Essa espera diz respeito ao estado geral do documento. Conteúdos carregados posteriormente por JavaScript podem exigir ``aguardar_elemento`` com uma condição específica.

### função esperar_pagina_carregar
:::web_utils.esperar_pagina_carregar

___

## Executando um script

A função ``executar_script`` executa JavaScript diretamente no contexto da página atual. Ela permite acessar APIs do navegador, consultar valores ou realizar operações que não estejam disponíveis diretamente pelos métodos convencionais do Selenium.

Quando ``args`` é informado, seu valor fica disponível no script como ``arguments[0]``. O parâmetro ``assincrono`` escolhe entre a execução comum e ``execute_async_script``; neste último caso, o script deve seguir o mecanismo assíncrono esperado pelo Selenium. O valor retornado pelo JavaScript é repassado pela função.

### função executar_script
:::web_utils.executar_script

___

## Extraindo o texto de um elemento

A função ``extrair_texto`` localiza e centraliza um elemento antes de devolver seu texto visível. Ela é apropriada para valores apresentados ao usuário, como rótulos, mensagens, células e totais.

O resultado corresponde à propriedade textual fornecida pelo Selenium, não necessariamente ao HTML interno nem ao atributo ``value`` de um campo. Para esses outros casos, utilize ``retornar_codigo_fonte`` ou ``coletar_atributo``.

### função extrair_texto
:::web_utils.extrair_texto

___

## Fechando uma janela

A função ``fechar_janela`` seleciona uma janela ou aba pela posição que ela ocupa na lista de handles e então a fecha. Portanto, o parâmetro ``janela`` é um índice, e não o próprio handle retornado por ``coletar_id_janela``.

Como a lista muda quando janelas são fechadas, os índices também podem mudar. Colete a lista atual antes da operação e garanta que outro contexto válido seja selecionado posteriormente, se a automação precisar continuar.

### função fechar_janela
:::web_utils.fechar_janela

___

## Fechando as demais janelas

A função ``fechar_janelas_menos_essa`` percorre todos os handles conhecidos e fecha cada janela ou aba cujo identificador seja diferente de ``id_janela``. Ela é útil para limpar janelas auxiliares e preservar apenas o contexto principal.

Neste caso, o parâmetro é o próprio handle, normalmente obtido com ``coletar_id_janela``, e não uma posição numérica. A função não fecha a janela preservada, mas falhas de seleção ou fechamento são repassadas.

### função fechar_janelas_menos_essa
:::web_utils.fechar_janelas_menos_essa

___

## Iniciando o navegador

A função ``iniciar_navegador`` concentra a preparação do webdriver, a configuração do navegador e a abertura da URL inicial. ``nome_navegador`` define a implementação — Chrome, Edge ou Firefox — e ``url`` informa a primeira página do fluxo.

Para personalizar a sessão, ``options`` recebe argumentos do navegador, ``extensoes`` recebe caminhos de extensões, ``experimentos`` configura opções experimentais e ``capacidades`` adiciona capacidades ao webdriver. Também é possível informar executáveis específicos, uma porta de conexão e o caminho do navegador.

Por padrão, ``baixar_webdriver_previamente=True`` faz a biblioteca localizar ou baixar um driver compatível antes da inicialização. Desative essa etapa quando ``executavel`` já apontar para um webdriver válido. A função retorna ``True`` depois de iniciar o navegador e abrir a página, e valida especialmente a porta e a existência do executável escolhido.

### função iniciar_navegador
:::web_utils.iniciar_navegador

___

## Limpando um campo

A função ``limpar_campo`` remove o conteúdo atual de um elemento editável. O campo é localizado e centralizado antes da limpeza, de modo que erros de seletor ou elementos indisponíveis sejam percebidos antes da ação.

Com ``performar=False``, usa-se diretamente o método ``clear`` do Selenium. Quando ``performar=True``, a função inclui uma ação de clique por ``ActionChains`` antes de limpar e redefine a cadeia de ações ao final. A função aguarda o carregamento da página, mas não devolve valor.

### função limpar_campo
:::web_utils.limpar_campo

___

## Maximizando a janela

A função ``maximizar_janela`` solicita ao webdriver que expanda a janela automatizada até o tamanho máximo permitido pelo ambiente. Isso pode tornar mais previsíveis a área visível, o posicionamento de elementos e as capturas de tela.

Ela atua somente sobre a janela atual, não recebe parâmetros e não devolve valor. Eventuais limitações do navegador ou do ambiente gráfico são repassadas como exceção.

### função maximizar_janela
:::web_utils.maximizar_janela

___

## Simulando uma ação do mouse

A função ``performar`` executa ações de mouse por meio de ``ActionChains``. Ela é uma alternativa às operações diretas do elemento quando o fluxo exige movimento do cursor ou uma sequência mais próxima de uma interação real.

O parâmetro ``acao`` aceita ``CLICK``, ``DOUBLE_CLICK`` e ``MOVE_TO_ELEMENT``. O elemento é localizado pelo seletor informado e a ação escolhida é executada imediatamente. Ao terminar, a função retorna ``True``; problemas de localização ou execução são repassados. A implementação atual não levanta erro para nomes de ação desconhecidos e ainda pode retornar ``True`` sem executar movimento ou clique, portanto utilize apenas os valores documentados.

### função performar
:::web_utils.performar

___

## Imprimindo a página em PDF

A função ``print_para_pdf`` usa o recurso de impressão do webdriver para converter a página atual em PDF. O parâmetro ``caminho_arquivo`` define onde o resultado será gravado, enquanto ``escala`` e ``paginacao`` controlam o tamanho e as páginas incluídas.

As opções ``fundo`` e ``encolher_para_caber`` determinam, respectivamente, se os fundos CSS serão impressos e se o conteúdo será ajustado ao papel. ``orientacao`` recebe o índice 0 para retrato e 1 para paisagem.

A função captura internamente qualquer erro. Ela retorna ``True`` quando consegue decodificar e gravar o PDF e ``False`` quando alguma etapa falha; por isso, o retorno deve ser verificado pelo fluxo chamador.

### função print_para_pdf
:::web_utils.print_para_pdf

___

## Procurando um elemento

A função ``procurar_elemento`` verifica se um elemento correspondente ao seletor está presente e pode ser manipulado. Quando encontra o elemento, também tenta centralizá-lo na janela e devolve ``True``.

É possível pesquisar dentro de Shadow DOM informando o host em ``elemento_shadowroot`` e o respectivo tipo de seletor. Qualquer falha de localização ou centralização é convertida em ``False``; portanto, essa função é indicada para verificações condicionais nas quais a ausência não deve interromper a execução.

### função procurar_elemento
:::web_utils.procurar_elemento

___

## Procurando vários elementos

A função ``procurar_muitos_elementos`` localiza todas as ocorrências correspondentes ao seletor e transforma o resultado em uma lista de textos. Assim, ela não devolve os objetos ``WebElement``: devolve o conteúdo textual de cada elemento na ordem encontrada.

Use-a quando o objetivo for coletar valores de listas, tabelas ou conjuntos repetidos. Para obter apenas a quantidade, ``contar_elementos`` expressa melhor a intenção. Falhas de busca ou centralização são repassadas ao chamador.

### função procurar_muitos_elementos
:::web_utils.procurar_muitos_elementos

___

## Fazendo uma requisição a uma URL

A função ``requisitar_url`` realiza uma requisição HTTP independente da navegação controlada pelo Selenium. Ela devolve diretamente um objeto ``requests.Response``, permitindo ao chamador consultar status, cabeçalhos, conteúdo e demais dados da resposta.

``metodo`` aceita ``GET`` para obter o recurso ou ``HEAD`` para solicitar apenas seus metadados. Também podem ser configurados streaming, validação SSL, autenticação básica, cabeçalhos, timeout e proxy. Métodos diferentes levantam ``SystemError`` e falhas da biblioteca ``requests`` são repassadas.

### função requisitar_url
:::web_utils.requisitar_url

___

## Retornando o código-fonte da página

A função ``retornar_codigo_fonte`` devolve o HTML que o webdriver expõe para a página no momento da chamada. Ela é útil para inspeção, registro ou processamento do documento completo quando a coleta elemento a elemento não é suficiente.

O resultado representa o estado atual conhecido pelo navegador e pode incluir alterações feitas no DOM depois do carregamento inicial. A função depende de uma instância ativa e repassa a exceção se o código-fonte não puder ser obtido.

### função retornar_codigo_fonte
:::web_utils.retornar_codigo_fonte

___

## Selecionando uma opção de um elemento

A função ``selecionar_elemento`` opera sobre elementos HTML ``select`` e escolhe uma opção pelo texto que ela apresenta ao usuário. O parâmetro ``valor`` deve corresponder ao texto visível da opção, não necessariamente ao conteúdo de seu atributo ``value``.

Antes da seleção, a função aguarda a disponibilidade do elemento e o localiza pelo tipo de seletor indicado. Retorna ``True`` quando conclui a escolha; se o elemento ou o texto visível não existir, a exceção do Selenium é repassada.

### função selecionar_elemento
:::web_utils.selecionar_elemento

___

## Trocando o contexto do navegador

Uma automação pode precisar sair do documento atual para atuar em outra janela, frame, alerta ou elemento ativo. A função ``trocar_para`` reúne essas mudanças de contexto por meio dos parâmetros ``tipo`` e ``id``.

``tipo`` aceita ``FRAME``, ``PARENT_FRAME``, ``NEW_WINDOW``, ``WINDOW``, ``ALERT``, ``ACTIVE_ELEMENT`` e ``DEFAULT_CONTENT``. O significado de ``id`` varia: em ``WINDOW`` ele é o índice na lista de handles; em ``ALERT`` pode solicitar texto, confirmação, cancelamento ou envio de conteúdo; alguns contextos não precisam de um identificador significativo.

Normalmente a função devolve ``True``. Para um alerta com ``id='TEXT'``, devolve o texto coletado; se qualquer etapa falhar, devolve ``False``. Como as exceções são absorvidas, o chamador deve avaliar o retorno antes de continuar.

### função trocar_para
:::web_utils.trocar_para

___

## Validando uma porta

A função ``validar_porta`` tenta estabelecer uma conexão TCP com o host ``ip`` e a ``porta`` informada. Ela pode ser usada antes de iniciar um serviço dependente, conectar-se a um webdriver remoto ou validar se um endpoint de rede está acessível.

``tempo_limite`` define por quantos segundos a tentativa aguardará resposta. O retorno ``True`` indica que a conexão foi aceita; ``False`` indica que a porta não respondeu dentro das condições da tentativa. Erros na criação do socket são repassados.

### função validar_porta
:::web_utils.validar_porta

___

## Voltando para a página anterior

A função ``voltar_pagina`` retrocede uma posição no histórico da janela ou aba atual, reproduzindo a ação do botão Voltar do navegador. Ela não troca de janela e depende de existir uma entrada anterior no histórico do contexto selecionado.

Depois da navegação, a função aguarda o carregamento da página de destino. Não há valor de retorno; falhas do navegador ou da espera são repassadas ao chamador.

### função voltar_pagina
:::web_utils.voltar_pagina
