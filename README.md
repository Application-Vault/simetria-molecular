Acesso em: https://quantum-materials-simulation-research.github.io/simetria-molecular/

## Idiomas

O seletor no cabeçalho oferece português (PT), inglês (EN) e chinês simplificado (ZH).
A preferência é salva no navegador em `sm_language`; português é o idioma inicial.
As traduções da interface e das mensagens ficam no módulo `js/i18n.js`.
Coordenadas XYZ, identificadores, nomes de moléculas e operações matemáticas são preservados.
Ao analisar, o frontend envia `idioma: "pt"`, `"en"` ou `"zh"` no payload.
O backend gera os títulos, cabeçalhos e descrições do relatório nesse idioma;
o PDF usa o mesmo TeX traduzido. Clientes que omitem `idioma` recebem português.
Para mudar o idioma de um relatório já gerado, selecione o idioma e execute uma nova análise.
Relatórios chineses usam `ctex` com fontes Fandol para compilação no Tectonic.