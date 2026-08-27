# Py-RPAutom

Essa biblioteca tem como objetivo facilitar a criação de processos automatizados via código. Durante a documentação será explicado como utilizar recursos para automação web, desktop e recursos do sistema como cópia de arquivos ou criação de pastas.

## Instalação

Para instalar a biblioteca `Py-RPAutom`, execute o comando abaixo no terminal de sua preferência:

```Powershell
python -m pip install py-rpautom
```

## Veja o Py-RPAutom em ação

Deixamos aqui um exemplo de como utilizar a biblioteca `Py-RPAutom`.
No exemplo abaixo, interagimos com o módulo web de automação:

```Python
"""Consulta no Bing as últimas notícias do Brasil publicadas pela EFE."""

from py_rpautom.web_utils import (
    aguardar_elemento,
    abrir_pagina,
    clicar_elemento,
    coletar_atributo,
    encerrar_navegador,
    escrever_em_elemento,
    iniciar_navegador,
    maximizar_janela,
    procurar_muitos_elementos,
)


def fechar_aviso_cookies_bing() -> None:
    """Fecha o aviso de cookies do Bing quando ele estiver presente."""
    seletor_aviso_cookies_bing = 'div[id=bnp_btn_accept]'

    validacao_aviso_cookies_bing = aguardar_elemento(
        identificador=seletor_aviso_cookies_bing,
        tipo_elemento="CSS_SELECTOR",
        tempo=20,
    )
    if not validacao_aviso_cookies_bing:
        raise RuntimeError(
            "O aviso de cookies não apareceu em tempo para o clique."
        )

    clicar_elemento(
        seletor=seletor_aviso_cookies_bing,
        tipo_elemento="CSS_SELECTOR",
    )


def fechar_aviso_cookies_efe() -> None:
    """Fecha o aviso de cookies da EFE quando ele estiver presente."""
    seletor_aviso_cookies_efe = 'button[id="accept-btn"]'
    validacao_aviso_cookies_efe = aguardar_elemento(
        identificador=seletor_aviso_cookies_efe,
        tipo_elemento="CSS_SELECTOR",
        tempo=10,
    )

    if validacao_aviso_cookies_efe:
        clicar_elemento(
            seletor=seletor_aviso_cookies_efe,
            tipo_elemento="CSS_SELECTOR",
        )


def pesquisar_noticias() -> None:
    """Preenche e envia o formulário de pesquisa do Bing."""
    pesquisa_bing = "últimas noticias de Brasil pt-br site:efe.com"

    campo_pesquisa = 'textarea[id="sb_form_q"]'
    campo_disponivel = aguardar_elemento(
        identificador=campo_pesquisa,
        tipo_elemento="CSS_SELECTOR",
        tempo=20,
    )
    if not campo_disponivel:
        raise RuntimeError("O campo de pesquisa do Bing não foi localizado.")

    escrever_em_elemento(
        seletor=campo_pesquisa,
        texto=pesquisa_bing,
        tipo_elemento="CSS_SELECTOR",
    )

    seletor_buscar_bing = 'label[for="sb_form_go"]'
    clicar_elemento(
        seletor=seletor_buscar_bing,
        tipo_elemento="CSS_SELECTOR",
    )

    seletor_resultados_bing = 'div[id="b_tween_searchResults"]'
    resultados_bing = aguardar_elemento(
        identificador=seletor_resultados_bing,
        tipo_elemento="CSS_SELECTOR",
        tempo=30,
    )
    if not resultados_bing:
        raise RuntimeError("O resultado do Bing não foi localizado.")


def acessar_resultado_efe() -> None:
    """Abre o primeiro resultado de pesquisa pertencente à Agência EFE."""
    seletor_efe_bing = (
        '//div[@class="b_attribution"]/cite[contains(text(), "pt-br") and '
        'contains(text(), "brasil")]//'
        'parent::*//parent::*//parent::*//parent::a'
    )

    efe_bing = aguardar_elemento(
        identificador=seletor_efe_bing,
        tipo_elemento="XPATH",
        tempo=20,
    )
    if not efe_bing:
        raise RuntimeError(
            'Link da Agência EFE no Bing não encontrado'
        )
    link_efe_bing = coletar_atributo(
        seletor=seletor_efe_bing,
        atributo='href',
        tipo_elemento="XPATH",
    )

    abrir_pagina(url=link_efe_bing)


def coletar_titulos_efe() -> list[str]:
    """Coleta títulos usando alternativas para diferentes páginas da EFE."""
    seletor_titulos = '//h2[@class="entry-title"]'

    titulos = []

    titulos = procurar_muitos_elementos(
        seletor = seletor_titulos,
        tipo_elemento="XPATH",
    )

    return titulos


def exibir_titulos(titulos: list[str]) -> None:
    """Exibe os títulos coletados de forma numerada."""
    if not titulos:
        print("Nenhum título de notícia foi localizado na página da EFE.")
        return

    print("\nÚltimas notícias do Brasil publicadas pela Agência EFE:\n")
    for indice, titulo in enumerate(titulos, start=1):
        print(f"{indice}. {titulo}")


def main() -> None:
    """Executa a automação completa e sempre encerra o navegador."""
    navegador_iniciado = False

    try:
        url_bing = "https://www.bing.com/"
        navegador_iniciado = iniciar_navegador(
            url=url_bing,
            nome_navegador="chrome",
        )
        if not navegador_iniciado:
            raise RuntimeError("Não foi possível iniciar o navegador.")

        maximizar_janela()
        fechar_aviso_cookies_bing()
        pesquisar_noticias()
        acessar_resultado_efe()
        fechar_aviso_cookies_efe()

        titulos = coletar_titulos_efe()
        exibir_titulos(titulos)
    finally:
        if navegador_iniciado:
            encerrar_navegador()


main()

```

## Continue explorando

- [Automação web](guia_usuario/web_utils.md)
- [Automação desktop](guia_usuario/desktop_utils.md)
- [Utilitários em Python](guia_usuario/python_utils.md)
