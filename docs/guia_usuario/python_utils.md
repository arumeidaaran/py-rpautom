# Módulo python_utils (python_utils.py)
___

Este módulo reúne utilitários para arquivos, pastas, planilhas, PDFs, processos, configurações, logs e outros recursos comuns em automações. As funções podem ser usadas isoladamente ou combinadas para preparar entradas, registrar execuções e organizar saídas.

## Abrindo um arquivo em bytes

Arquivos binários, como imagens, PDFs e executáveis, não devem ser lidos como texto. ``abrir_arquivo_em_bytes`` entrega o conteúdo bruto existente no disco, sem interpretar encoding nem modificar quebras de linha.

O arquivo inteiro é carregado em memória. Para conteúdo textual conhecido, ``abrir_arquivo_texto`` oferece um retorno mais conveniente; para dados binários ou encoding desconhecido, a leitura em bytes evita conversões que poderiam corromper o conteúdo.

### função abrir_arquivo_em_bytes
:::python_utils.abrir_arquivo_em_bytes

___

## Abrindo um arquivo Excel

``abrir_arquivo_excel`` transforma uma guia de planilha em uma lista de linhas, mantendo a ordem das células. Arquivos ``.xls`` são tratados pelo leitor do formato legado, enquanto ``.xlsx`` e ``.xlsm`` utilizam o formato mais recente, mas a estrutura devolvida é a mesma.

Uma chamada lê somente uma guia. Quando ``guia`` não é informada, utiliza-se a guia ativa ou, no formato legado, a primeira. ``manter_macro`` e ``manter_links`` controlam a preservação desses recursos nos formatos que os suportam; os valores retornados são os resultados calculados das células, não as fórmulas.

### função abrir_arquivo_excel
:::python_utils.abrir_arquivo_excel

___

## Abrindo um arquivo PDF

``abrir_arquivo_pdf`` extrai o texto pesquisável de um PDF e organiza o resultado por página e por linha. ``paginacao`` permite ler o documento inteiro, uma página ou um conjunto de páginas, e ``orientacao`` corrige documentos armazenados com rotação.

PDFs digitalizados podem conter somente imagens e, nesse caso, não produzem texto útil nesta leitura. Converta as páginas com ``converter_pdf_em_imagem`` e aplique ``extrair_texto_ocr`` quando o documento não possuir uma camada textual.

### função abrir_arquivo_pdf
:::python_utils.abrir_arquivo_pdf

___

## Abrindo um arquivo de texto

``abrir_arquivo_texto`` lê todo o conteúdo de um arquivo e o devolve em uma única string, preservando suas quebras de linha. O parâmetro ``encoding`` precisa corresponder à codificação usada na gravação.

Como a leitura carrega tudo em memória, a função é apropriada para arquivos textuais de tamanho controlado. Conteúdo muito grande pode exigir processamento incremental, enquanto arquivos não textuais devem ser abertos com ``abrir_arquivo_em_bytes``.

### função abrir_arquivo_texto
:::python_utils.abrir_arquivo_texto

___

## Adicionando conteúdo a um ZIP

``adicionar_ao_zip`` abre um pacote ZIP em modo de anexação e preserva o conteúdo que já estava armazenado. ``caminho`` pode indicar um único arquivo ou, com ``recursivo=True``, uma pasta cuja hierarquia será adicionada por completo.

O arquivo indicado em ``arquivo_destino`` é criado caso ainda não exista. Quando a intenção for gerar um pacote novo com todo o conteúdo de uma pasta, ``compactar`` expressa melhor a operação e permite escolher explicitamente o modo de criação.

### função adicionar_ao_zip
:::python_utils.adicionar_ao_zip

___

## Alterando linhas de um arquivo de texto

``alterar_arquivo_texto`` procura linhas que contenham ``linha_atual`` e substitui a linha inteira por ``linha_alterada``. A busca é por conteúdo parcial; não é necessário que o texto pesquisado corresponda à linha completa.

Por padrão, somente a primeira ocorrência é alterada. ``multilinhas=True`` aplica a substituição a todas as linhas correspondentes. O arquivo original é regravado sem backup automático, e encodings diferentes podem ser definidos para leitura e saída quando também for necessária uma conversão.

### função alterar_arquivo_texto
:::python_utils.alterar_arquivo_texto

___

## Verificando a existência de um caminho

``caminho_existente`` informa se há um arquivo ou uma pasta no caminho recebido. A função não diferencia os dois tipos de item; ela responde apenas sobre a existência.

Caminhos relativos são resolvidos conforme o diretório de trabalho da execução. Essa verificação pode anteceder operações de leitura ou exclusão quando a ausência for uma situação esperada e não deva ser tratada como exceção.

### função caminho_existente
:::python_utils.caminho_existente

___

## Limpando o terminal

``cls`` limpa o conteúdo visível do console por meio do PowerShell. A operação afeta somente a exibição: mensagens já gravadas em arquivos de log permanecem intactas.

Como depende do comando ``cls``, este recurso é específico de ambientes Windows com PowerShell disponível. Ele não recebe parâmetros nem devolve conteúdo.

### função cls
:::python_utils.cls

___

## Coletando o diretório de um caminho

``coletar_arvore_caminho`` devolve o diretório que contém o item informado. Para um arquivo, o resultado é sua pasta; para uma pasta, o resultado é a pasta imediatamente superior.

O caminho é convertido para absoluto antes da coleta. Isso permite construir destinos relativos à origem sem depender de separadores ou manipulações manuais de string.

### função coletar_arvore_caminho
:::python_utils.coletar_arvore_caminho

___

## Coletando um caminho absoluto

``coletar_caminho_absoluto`` resolve um caminho relativo a partir do diretório de trabalho atual e devolve sua representação absoluta. O item não precisa existir, pois a função normaliza o caminho sem validar sua presença no disco.

Essa conversão reduz ambiguidades quando uma automação pode ser iniciada por terminais, agendadores ou serviços com diretórios de trabalho diferentes.

### função coletar_caminho_absoluto
:::python_utils.coletar_caminho_absoluto

___

## Coletando extensões de um arquivo

``coletar_extensao_arquivo`` devolve todos os sufixos presentes no nome como uma lista. Um arquivo de extensão simples produz um item; nomes compostos podem produzir dois ou mais.

A análise considera apenas o nome e não inspeciona o conteúdo real do arquivo. Quando houver múltiplos sufixos, o último costuma representar o formato externo, mas a lista completa permite preservar extensões compostas.

### função coletar_extensao_arquivo
:::python_utils.coletar_extensao_arquivo

___

## Coletando o idioma do sistema operacional

``coletar_idioma_so`` consulta o idioma configurado para a interface do Windows e o devolve como uma localidade. Essa informação ajuda automações de interface a escolher textos compatíveis com botões, menus e mensagens do ambiente atual.

A função depende das APIs do Windows. O retorno identifica idioma e região, mas não modifica configurações do sistema nem traduz conteúdo.

### função coletar_idioma_so
:::python_utils.coletar_idioma_so

___

## Coletando a versão do sistema operacional

``coletar_versao_so`` reúne dados do sistema operacional e da arquitetura em um dicionário. O resultado contém o nome do sistema, release, versão detalhada e tipo de máquina.

Esses dados podem ser registrados em logs ou usados quando uma automação precisa escolher comportamentos compatíveis com o ambiente. A função apenas consulta informações; ela não valida requisitos mínimos.

### função coletar_versao_so
:::python_utils.coletar_versao_so

___

## Coletando o nome de um arquivo

``coletar_nome_arquivo`` separa o nome de seu diretório e remove a última extensão. O resultado pode ser reutilizado na criação de relatórios, arquivos convertidos ou outros artefatos relacionados à mesma origem.

Em nomes com extensões compostas, apenas o último sufixo é retirado. Utilize ``coletar_extensao_arquivo`` quando precisar analisar ou preservar todos os sufixos.

### função coletar_nome_arquivo
:::python_utils.coletar_nome_arquivo

___

## Coletando os nomes das guias de um arquivo Excel

``coletar_nome_guias_arquivo_excel`` lista as guias na ordem em que aparecem na pasta de trabalho, inclusive as ocultas. Isso permite validar uma guia antes da leitura ou percorrer dinamicamente todas elas com ``abrir_arquivo_excel``.

A função é destinada aos formatos modernos aceitos pelo leitor utilizado e não oferece suporte ao ``.xls`` legado.

### função coletar_nome_guias_arquivo_excel
:::python_utils.coletar_nome_guias_arquivo_excel

___

## Coletando identificadores de processos

``coletar_pid`` percorre os processos ativos e devolve dados daqueles cujo nome contém o texto pesquisado. A comparação é parcial e não diferencia letras maiúsculas de minúsculas, portanto uma consulta pode corresponder a mais de uma instância.

Cada resultado inclui PID, nome e instante de criação. Processos inacessíveis por falta de permissão são ignorados. Quando apenas a existência interessa, utilize ``processo_existente``; para encerrar uma instância específica, repasse seu PID a ``finalizar_processo``.

### função coletar_pid
:::python_utils.coletar_pid

___

## Coletando o tamanho de um arquivo

``coletar_tamanho`` devolve em bytes o tamanho do item indicado. Em arquivos, o valor pode ser usado para validar downloads, detectar saídas vazias ou registrar consumo de armazenamento.

Quando aplicado a uma pasta, o resultado representa a entrada do diretório no sistema de arquivos, não a soma dos itens contidos nela. A ausência do caminho gera exceção.

### função coletar_tamanho
:::python_utils.coletar_tamanho

___

## Coletando a versão de um arquivo

Executáveis e bibliotecas do Windows podem armazenar informações de versão em suas propriedades. ``coletar_versao_arquivo`` consulta esses metadados e devolve os quatro componentes numéricos da versão.

O caminho precisa ser absoluto e o arquivo deve possuir informação de versão. Esse recurso é especialmente útil para comparar versões de executáveis instalados, mas é específico do Windows e não corresponde à data ou ao nome do arquivo.

### função coletar_versao_arquivo
:::python_utils.coletar_versao_arquivo

___

## Compactando uma pasta

``compactar`` percorre recursivamente uma pasta e grava seus arquivos em um ZIP, preservando a estrutura relativa das subpastas. ``arquivo_destino`` define o pacote que será criado ou atualizado.

O modo ``'w'`` recria o ZIP e substitui um pacote existente; ``'a'`` acrescenta conteúdo. Para incluir seletivamente um arquivo ou uma pasta em um pacote sem reconstruí-lo, utilize ``adicionar_ao_zip``.

### função compactar
:::python_utils.compactar

___

## Convertendo um PDF em imagens

``converter_pdf_em_imagem`` gera um PNG para cada página de um PDF dentro de ``caminho_saida``. O processo é útil para OCR, evidências e comparações visuais de documentos.

``zoom`` controla a resolução e também influencia o tamanho dos arquivos produzidos. ``orientacao`` aplica rotação antes da geração, e ``alpha`` determina se a transparência será preservada. A pasta de saída precisa existir antes da chamada.

### função converter_pdf_em_imagem
:::python_utils.converter_pdf_em_imagem

___

## Copiando um arquivo

``copiar_arquivo`` duplica um arquivo em outro local e preserva seus metadados, como datas e permissões. O item original permanece na origem.

Se já houver no destino um arquivo com o mesmo nome, ele poderá ser substituído. Utilize ``recortar`` quando o objetivo for mover o item em vez de manter duas cópias.

### função copiar_arquivo
:::python_utils.copiar_arquivo

___

## Copiando uma pasta

``copiar_pasta`` recria a pasta de origem dentro do destino e preserva toda a hierarquia de arquivos e subpastas. O nome da pasta de origem também faz parte do caminho final.

A cópia não realiza uma mescla com uma pasta final já existente. Essa restrição evita combinar silenciosamente conteúdos de origens diferentes, mas exige que o chamador prepare um destino livre.

### função copiar_pasta
:::python_utils.copiar_pasta

___

## Criando um arquivo de texto

``criar_arquivo_texto`` cria ou sobrescreve um arquivo com o conteúdo informado. A pasta que receberá o arquivo precisa existir; quando ``dado`` não é fornecido, cria-se um arquivo vazio.

Com ``em_bytes=False``, o conteúdo é gravado como texto usando ``encoding``. Com ``em_bytes=True``, a função espera conteúdo binário. Para acrescentar dados sem apagar o conteúdo existente, utilize ``escrever_em_arquivo`` em modo de anexação.

### função criar_arquivo_texto
:::python_utils.criar_arquivo_texto

___

## Criando uma pasta

``criar_pasta`` cria toda a hierarquia necessária até o diretório informado. Assim, um caminho com vários níveis não exige chamadas separadas para cada pasta intermediária.

A pasta final não pode existir previamente. Quando a criação puder ser repetida em diferentes execuções, consulte ``caminho_existente`` antes de chamar a função ou trate a exceção correspondente.

### função criar_pasta
:::python_utils.criar_pasta

___

## Descompactando um arquivo

``descompactar`` extrai um pacote para o diretório indicado e recria a estrutura interna de pastas. O diretório de destino é criado automaticamente quando necessário.

Arquivos existentes com o mesmo nome podem ser sobrescritos. ``senha_arquivo`` permite abrir pacotes protegidos; uma senha incorreta ou um arquivo incompatível produz a exceção da biblioteca de compactação.

### função descompactar
:::python_utils.descompactar

___

## Escrevendo em um arquivo

``escrever_em_arquivo`` oferece controle explícito sobre o modo de abertura. ``'w'`` substitui o conteúdo e ``'a'`` acrescenta novos dados ao final, permitindo registrar informações progressivamente.

``nova_linha`` pode acrescentar ``'\r'``, ``'\n'`` ou ``'\r\n'`` depois do conteúdo. Outros valores, inclusive ``None``, não adicionam terminador. A função trabalha com texto e utiliza o encoding informado.

### função escrever_em_arquivo
:::python_utils.escrever_em_arquivo

___

## Excluindo um arquivo

``excluir_arquivo`` remove definitivamente o arquivo informado. A operação não envia o item para a Lixeira e não oferece recuperação automática.

A função não exclui diretórios. Quando a ausência do arquivo for aceitável, verifique-a previamente com ``caminho_existente``; arquivos abertos ou protegidos podem produzir erro de permissão.

### função excluir_arquivo
:::python_utils.excluir_arquivo

___

## Excluindo uma pasta

``excluir_pasta`` pode remover apenas uma pasta vazia ou excluir recursivamente todo o seu conteúdo. O parâmetro ``vazia=True`` funciona como proteção e impede a remoção quando houver arquivos ou subpastas.

Ao usar ``vazia=False``, todo o conteúdo é apagado definitivamente, sem confirmação e sem passagem pela Lixeira. Confirme cuidadosamente o caminho e o estado desejado antes de autorizar a remoção recursiva.

### função excluir_pasta
:::python_utils.excluir_pasta

___

## Executando um comando no terminal

``executar_comando_terminal`` recebe o executável e seus argumentos como itens separados de uma lista. A execução não passa por um shell, reduzindo interpretações inesperadas de caracteres especiais e operadores.

O resultado é um ``CompletedProcess`` com código de retorno, saída padrão e saída de erro. ``tempo_limite`` restringe a duração, ``diretorio_execucao`` altera a pasta de trabalho e ``nova_linha`` define se as saídas serão devolvidas como texto ou bytes. Código diferente de zero gera exceção.

### função executar_comando_terminal
:::python_utils.executar_comando_terminal

___

## Extraindo texto de uma imagem com OCR

``extrair_texto_ocr`` utiliza o Tesseract para reconhecer texto em imagens. O código informado em ``linguagem`` precisa corresponder a um pacote de idioma instalado no mecanismo, e a qualidade da imagem influencia diretamente o resultado.

O Tesseract deve estar instalado e disponível no PATH do sistema. A função pode ser combinada com ``converter_pdf_em_imagem`` para processar documentos digitalizados que não possuem texto pesquisável.

### função extrair_texto_ocr
:::python_utils.extrair_texto_ocr

___

## Finalizando um processo

``finalizar_processo`` encerra imediatamente a instância identificada pelo PID. Como não há uma solicitação de fechamento normal, dados não salvos pelo processo podem ser perdidos.

Use ``coletar_pid`` para identificar a instância correta antes da finalização. A função devolve ``False`` quando não encontra um processo ativo com aquele PID e ``True`` quando consegue encerrá-lo.

### função finalizar_processo
:::python_utils.finalizar_processo

___

## Gravando um log delimitado em arquivo

``gravar_log_em_arquivo`` combina os itens de ``conteudo`` usando ``delimitador`` e grava uma linha estruturada. O resultado pode ser consumido como arquivo tabular por planilhas e outras ferramentas.

``modo`` define se o arquivo será recriado ou receberá novas linhas, enquanto ``nova_linha`` controla o terminador. Para registros com níveis de severidade e formatação do módulo ``logging``, utilize ``logar``.

### função gravar_log_em_arquivo
:::python_utils.gravar_log_em_arquivo

___

## Exibindo uma janela de diálogo

``janela_dialogo`` abre uma caixa de mensagem nativa do Windows e bloqueia a execução até que o usuário escolha um botão. ``estilo`` determina o conjunto de botões e o ícone conforme os códigos da API do sistema.

O inteiro retornado identifica a opção selecionada. Como exige interação humana e pode permanecer aberta indefinidamente, a função é apropriada para automações assistidas, não para execuções totalmente desatendidas.

### função janela_dialogo
:::python_utils.janela_dialogo

___

## Lendo configurações e variáveis de ambiente

``ler_variavel_ambiente`` consulta duas fontes de configuração. Com ``variavel_sistema=True``, lê uma variável do sistema operacional; caso contrário, lê uma seção de um arquivo INI.

No arquivo, ``nome_bloco_config`` escolhe a seção e ``nome_variavel`` escolhe uma chave. Quando a chave não é informada, o bloco inteiro é devolvido como dicionário. Parâmetros de arquivo e bloco são ignorados na leitura do ambiente do sistema.

### função ler_variavel_ambiente
:::python_utils.ler_variavel_ambiente

___

## Registrando mensagens de log

``logar`` configura e registra uma mensagem com os níveis ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR`` ou ``CRITICAL``. Sem ``arquivo``, a saída vai para o console; com um caminho, pode ser acrescentada ou recriada conforme ``modo``.

``formatacao`` e ``handlers`` permitem personalizar a infraestrutura padrão de logging. Como ``basicConfig`` efetiva sua configuração na primeira chamada, alterações posteriores de destino ou formato podem ser ignoradas durante o mesmo processo. Um nível inválido é devolvido como mensagem de erro em vez de ser registrado.

### função logar
:::python_utils.logar

___

## Verificando se uma pasta está vazia

``pasta_esta_vazia`` devolve ``True`` apenas quando o caminho existe, representa uma pasta e não contém arquivos nem subpastas. Uma subpasta vazia já faz com que a pasta principal seja considerada não vazia.

O retorno ``False`` também pode indicar que o caminho não existe. Combine a função com ``caminho_existente`` quando precisar distinguir ausência de conteúdo existente.

### função pasta_esta_vazia
:::python_utils.pasta_esta_vazia

___

## Verificando a existência de um processo

``processo_existente`` procura processos cujo nome contenha o texto informado, sem diferenciar maiúsculas de minúsculas. O retorno indica apenas se existe ao menos uma correspondência.

Como a busca é parcial, nomes genéricos podem alcançar mais de um executável. Utilize ``coletar_pid`` quando precisar conhecer e distinguir cada instância encontrada.

### função processo_existente
:::python_utils.processo_existente

___

## Movendo um arquivo ou uma pasta

``recortar`` move um item para outro caminho e o remove da origem. O destino pode ser uma pasta ou um caminho final, conforme as regras da operação de movimentação utilizada pelo sistema.

Movimentos no mesmo volume geralmente são diretos; entre volumes, podem envolver cópia seguida de exclusão. Para manter o original, utilize ``copiar_arquivo`` ou ``copiar_pasta``.

### função recortar
:::python_utils.recortar

___

## Removendo acentos de um texto

``remover_acentos`` normaliza o conteúdo Unicode e devolve uma representação limitada a caracteres ASCII. Letras acentuadas são convertidas para suas formas sem acento quando a normalização permite.

Caracteres sem equivalente ASCII, incluindo símbolos, emojis e alfabetos não latinos, podem ser descartados. A função é útil para compatibilidade e comparação, mas não deve ser usada quando esses caracteres carregarem informação que precise ser preservada.

### função remover_acentos
:::python_utils.remover_acentos

___

## Renomeando um arquivo ou uma pasta

``renomear`` recebe separadamente o diretório, o nome atual e o novo nome. A operação mantém o item no mesmo diretório e devolve o caminho resultante produzido pelo sistema.

Os nomes devem incluir a extensão quando ela precisar ser mantida. Para transferir o item para outro diretório, utilize ``recortar``. O comportamento diante de um destino já existente depende das regras do sistema operacional.

### função renomear
:::python_utils.renomear

___

## Retornando itens de uma pasta

``retornar_arquivos_em_pasta`` aplica uma máscara ``glob`` ao diretório e devolve os caminhos correspondentes como strings. O filtro controla extensão, profundidade e quais itens serão incluídos.

O padrão ``'**/*'`` percorre subpastas recursivamente; ``'*'`` limita a busca ao primeiro nível; uma máscara por extensão restringe os resultados. A lista pode incluir arquivos e diretórios quando ambos corresponderem ao padrão.

### função retornar_arquivos_em_pasta
:::python_utils.retornar_arquivos_em_pasta

___

## Retornando a data e a hora atuais

``retornar_data_hora_atual`` formata o instante local da máquina segundo uma máscara compatível com ``strftime``. A mesma função pode devolver uma data legível, somente um componente ou um identificador apropriado para nomes de arquivos.

O resultado não inclui informação de fuso horário. A máscara recebida determina integralmente a string devolvida e deve usar os códigos de data e hora esperados pelo Python.

### função retornar_data_hora_atual
:::python_utils.retornar_data_hora_atual

___

## Transformando um arquivo em Base64

``transformar_arquivo_em_base64`` lê um arquivo binário, codifica seu conteúdo em Base64 e devolve o resultado como string. Esse formato é utilizado quando APIs, documentos ou campos textuais precisam transportar dados binários.

O arquivo inteiro é carregado em memória e a representação resultante é maior que o conteúdo original. Base64 é uma codificação reversível, não um mecanismo de criptografia ou proteção de dados.

### função transformar_arquivo_em_base64
:::python_utils.transformar_arquivo_em_base64
