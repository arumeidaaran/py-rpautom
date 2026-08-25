"""Extensão do griffe que traduz rótulos de seção do português.

O parser Google do griffe só reconhece rótulos de seção em inglês
(``Args:``, ``Returns:``, ``Raises:``...). Como as docstrings desta
biblioteca são escritas em português — decisão coerente com a proposta
do projeto, descrita no README —, sem esta extensão o mkdocstrings
trataria ``Parâmetros:`` como um bloco de aviso genérico, e não como a
seção que gera a tabela de parâmetros.

A extensão reescreve o texto da docstring antes que ele seja
interpretado, trocando apenas a linha do rótulo. O conteúdo permanece
intacto, e o código-fonte no repositório continua em português: a
tradução acontece somente em memória, durante a geração da
documentação.

O rótulo original é reaproveitado como título da seção
(``Parâmetros:`` vira ``Args: Parâmetros:``), então a página final
também exibe o cabeçalho em português — o griffe usa a palavra em
inglês apenas para classificar a seção.

Uso no ``mkdocs.yml``:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            extensions:
              - docs/extensoes/traduzir_secoes.py:TraduzirSecoes
```

Para acrescentar ou substituir rótulos, informe o mapa ``rotulos``:

```yaml
            extensions:
              - docs/extensoes/traduzir_secoes.py:TraduzirSecoes:
                  rotulos:
                    devolve: Returns
```
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from griffe import Extension, Object

__all__ = ['ROTULOS_PADRAO', 'TraduzirSecoes']


# Rótulo em português (sem acento, em minúsculas) -> rótulo reconhecido
#   pelo parser Google do griffe.
ROTULOS_PADRAO: dict[str, str] = {
    # Parâmetros
    'parametros': 'Args',
    'parametro': 'Args',
    'argumentos': 'Args',
    'argumento': 'Args',
    'outros parametros': 'Other Args',
    'parametros nomeados': 'Keyword Args',
    'parametros de tipo': 'Type Params',
    # Retorno
    'retorna': 'Returns',
    'retorno': 'Returns',
    'retornos': 'Returns',
    'devolve': 'Returns',
    # Geradores
    'gera': 'Yields',
    'produz': 'Yields',
    'recebe': 'Receives',
    # Exceções
    'excecoes': 'Raises',
    'excecao': 'Raises',
    'erros': 'Raises',
    'levanta': 'Raises',
    # Exemplos
    'exemplos': 'Examples',
    'exemplo': 'Examples',
    # Membros
    'atributos': 'Attributes',
    'funcoes': 'Functions',
    'metodos': 'Methods',
    'classes': 'Classes',
    'modulos': 'Modules',
    'apelidos de tipo': 'Type Aliases',
    # Avisos
    'avisos': 'Warns',
    'aviso': 'Warns',
}

# Mesmo formato de cabeçalho que o parser Google do griffe reconhece:
#   um rótulo de palavras seguido de ':' e, opcionalmente, de um título.
_RE_CABECALHO = re.compile(
    r'^(?P<rotulo>[\w][\s\w-]*):(\s+(?P<titulo>[^\s].*))?\s*$',
)


def _normalizar(rotulo: str) -> str:
    """Reduz um rótulo à forma usada como chave do mapa de tradução.

    Remove acentos e converte para minúsculas, de modo que
    ``Parâmetros``, ``PARAMETROS`` e ``parâmetros`` sejam tratados como
    o mesmo rótulo. Assim, um deslize de digitação na acentuação não
    impede o reconhecimento da seção.

    Parâmetros:
        rotulo: Texto do rótulo, como escrito na docstring.

    Retorna:
        str: Rótulo sem acentos, em minúsculas e sem espaços nas
        pontas.
    """
    decomposto = unicodedata.normalize('NFKD', rotulo)
    sem_acento = ''.join(
        caractere
        for caractere in decomposto
        if not unicodedata.combining(caractere)
    )

    return ' '.join(sem_acento.lower().split())


def traduzir_secoes(
    texto: str,
    rotulos: dict[str, str],
    *,
    manter_titulo: bool = True,
) -> str:
    """Traduz os rótulos de seção de uma docstring.

    Percorre o texto linha a linha e substitui apenas as que são
    cabeçalho de seção: sem recuo, no formato ``Rótulo:`` e com o
    rótulo presente no mapa. Linhas dentro de blocos de código
    delimitados por crase tripla são preservadas, mesma regra que o
    parser do griffe aplica — sem isso, um ``Retorna:`` que aparecesse
    dentro de um exemplo de código seria alterado.

    O conteúdo da seção nunca é tocado, apenas a linha do cabeçalho.

    Parâmetros:
        texto: Conteúdo da docstring, já sem o recuo do código.
        rotulos: Mapa de rótulo normalizado para rótulo em inglês.
        manter_titulo: Quando ``True``, o rótulo original é reaproveitado
            como título da seção, na forma ``Args: Parâmetros:``. O
            griffe classifica a seção pela palavra em inglês e usa o
            título para exibi-la, de modo que a página final continua em
            português. Quando ``False``, resta só o rótulo em inglês e o
            texto exibido passa a ser o padrão do tema.

    Retorna:
        str: Docstring com os cabeçalhos de seção traduzidos.

    Exemplos:
        >>> traduzir_secoes('Retorna:\\n    bool: Sucesso.',
        ...                 {'retorna': 'Returns'})
        'Returns: Retorna:\\n    bool: Sucesso.'

        >>> traduzir_secoes('Retorna:\\n    bool: Sucesso.',
        ...                 {'retorna': 'Returns'}, manter_titulo=False)
        'Returns:\\n    bool: Sucesso.'
    """
    linhas = texto.split('\n')
    em_bloco_de_codigo = False
    alterado = False

    for indice, linha in enumerate(linhas):
        if linha.lstrip(' ').startswith('```'):
            em_bloco_de_codigo = not em_bloco_de_codigo
            continue

        if em_bloco_de_codigo:
            continue

        cabecalho = _RE_CABECALHO.match(linha)
        if cabecalho is None:
            continue

        rotulo = cabecalho.group('rotulo').strip()
        traducao = rotulos.get(_normalizar(rotulo))
        if traducao is None:
            continue

        # Um título escrito pelo autor tem precedência sobre o rótulo.
        titulo = cabecalho.group('titulo')
        if titulo is None and manter_titulo:
            titulo = f'{rotulo}:'

        linhas[indice] = f'{traducao}:' + (f' {titulo}' if titulo else '')
        alterado = True

    if not alterado:
        return texto

    return '\n'.join(linhas)


class TraduzirSecoes(Extension):
    """Traduz os rótulos de seção das docstrings em português.

    Atua no momento em que cada objeto é criado pelo griffe, antes de a
    docstring ser interpretada. Como a interpretação só acontece na
    renderização, alterar o texto aqui basta para que módulos, classes,
    funções e atributos escritos em português produzam as mesmas
    tabelas de parâmetros, retorno e exceções que produziriam se
    estivessem em inglês.

    Parâmetros:
        rotulos: Rótulos adicionais ou substituições, no formato
            ``{'rotulo em portugues': 'Rótulo Google'}``. As chaves são
            normalizadas, então acentos e maiúsculas são indiferentes.
            O que for informado tem precedência sobre
            ``ROTULOS_PADRAO``.
        manter_titulo: Quando ``True``, o cabeçalho continua sendo
            exibido em português na página gerada. Informe ``False``
            para deixar o tema exibir o texto padrão, em inglês.
    """

    def __init__(
        self,
        rotulos: dict[str, str] | None = None,
        *,
        manter_titulo: bool = True,
    ) -> None:
        super().__init__()

        self.manter_titulo: bool = manter_titulo
        self.rotulos: dict[str, str] = dict(ROTULOS_PADRAO)
        for rotulo, traducao in (rotulos or {}).items():
            self.rotulos[_normalizar(rotulo)] = traducao

    def on_instance(self, *, obj: Object, **kwargs: Any) -> None:
        """Traduz a docstring do objeto recém-criado pelo griffe.

        Objetos sem docstring são ignorados. O cache de interpretação é
        descartado por precaução, para o caso de a docstring já ter
        sido lida por outra extensão antes desta.

        Parâmetros:
            obj: Objeto criado pelo griffe (módulo, classe, função ou
                atributo).
            kwargs: Demais argumentos passados pelo griffe, não
                utilizados aqui.

        Retorna:
            None
        """
        docstring = obj.docstring
        if docstring is None or not docstring.value:
            return

        traduzida = traduzir_secoes(
            docstring.value,
            self.rotulos,
            manter_titulo=self.manter_titulo,
        )
        if traduzida == docstring.value:
            return

        docstring.value = traduzida
        docstring.__dict__.pop('parsed', None)
