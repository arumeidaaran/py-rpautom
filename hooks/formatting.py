def on_page_markdown(markdown, **kwargs):
    # DEFINIÇÃO DAS CONFIGURAÇÕES #
    def replace_caminho_campo(markdown, **kwargs):
        caminho_campo_trecho = f"""
            Para a interação com uma janela ou elemento dentro da aplicação, é necessário informar a árvore de elementos até o elemento alvo em formato dict, conforme apresentado abaixo: \n \

            \n \
            \\t {{ \n \
            \\t\\t 'window': {{ \n \
            \\t\\t\\t 'title': 'nome do elemento', \n \
            \\t\\t\\t 'session': 'nome da sessão', \n \
            \\t\\t\\t 'child_window': {{ \n \
            \\t\\t\\t\\t 'title': 'nome do elemento filho', \n \
            \\t\\t\\t\\t 'control_type': 'tipo de elemento', \n \
            \\t\\t\\t\\t 'auto_id': 'identificador do elemento', \n \
            \\t\\t\\t\\t 'child_window': {{ \n \
            \\t\\t\\t\\t\\t 'best_match': 'Outro identificador único', \n \
            \\t\\t\\t\\t }} \n \
            \\t\\t\\t }} \n \
            \\t\\t }} \n \
            \\t }} \n \
            \n \

            \n Onde: \n
            - 'window': É a marcação que define os parâmetros da janela; \n
            - 'child_window': É a marcação que define os parâmetros dos elementos filhos e filhos de filhos; \n
            - 'session': é o nome da sessão; \n
            - 'title': é o título da janela ou do elemento; \n
            - 'control_type': é o tipo de elemento desktop; \n
            - 'auto_id': é o identificador do elemento dentro da aplicação desktop. \n
            - 'best_match': é um identificador único, como a classe  do elemento dentro da aplicação desktop. \n
        """

        str_caminho_campo_trecho = [
            item.strip() for item in caminho_campo_trecho.splitlines()
        ]

        return markdown.replace(
            '#formatting.replace_caminho_campo#',
            '\n'.join(str_caminho_campo_trecho).replace('\\t', '\t'),
        )

    def replace_hierarquia_de_elemento(markdown, **kwargs):
        hierarquia_de_elemento_trecho = """
            Para informar o caminho do elemento, deve-se seguir a \
            estrutura de elementos conforme apresendado na sessão \
            "Estrutura de hierarquia de um elemento".
        """

        str_hierarquia_de_elemento_trecho = [
            item.strip() for item in hierarquia_de_elemento_trecho.splitlines()
        ]

        return markdown.replace(
            '#formatting.replace_hierarquia_de_elemento#',
            '\n'.join(str_hierarquia_de_elemento_trecho).replace('\\t', '\t'),
        )

    def replace_estilo_aplicacao(markdown, **kwargs):
        estilo_aplicacao_trecho = """
            > Escolha o estilo da aplicação, Win32 ou UIA, de acordo com a arquitetura da aplicação que se quer manipular. Aplicações Win32 são aplicações no estilo clássico do Windows, já aplicações UIA são aplicações modernas, em sua maioria disponibilizadas a partir da loja do Windows. Recomendamos que, em caso de dúvidas, teste as possibilidades e escolha o que melhor se adequa ao momento.
        """

        str_estilo_aplicacao_trecho = [
            item.strip() for item in estilo_aplicacao_trecho.splitlines()
        ]

        return markdown.replace(
            '#formatting.replace_estilo_aplicacao#',
            '\n'.join(str_estilo_aplicacao_trecho).replace('\\t', '\t'),
        )

    # EXECUÇÃO DAS CONFIGURAÇÕES #
    markdown = replace_caminho_campo(markdown, **kwargs)
    markdown = replace_hierarquia_de_elemento(markdown, **kwargs)
    markdown = replace_estilo_aplicacao(markdown, **kwargs)

    # RETORNO DA DOCUMENTAÇÃO #
    return markdown
