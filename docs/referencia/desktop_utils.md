# desktop_utils

Automação de aplicações desktop do Windows via pywinauto: abre ou se
conecta a um programa, percorre a árvore de elementos, preenche campos,
aciona menus e captura evidências.

Os elementos são endereçados por um dicionário de caminho aninhado
(`window` / `child_window`), e o backend — `win32` para aplicações
clássicas, `uia` para as modernas — precisa corresponder à aplicação
manipulada.

Para exemplos de uso passo a passo, veja o
[guia de automação desktop](../guia_usuario/desktop_utils.md).

::: desktop_utils
