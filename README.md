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

## PDF assíncrono

Ao clicar em Gerar PDF, a interface envia o TeX e recebe o identificador da tarefa.
O status fica junto do resultado, com indicador indeterminado e consultas a cada
três segundos. Nenhuma aba vazia é aberta durante a espera. Ao concluir, o botão
Abrir PDF abre o documento em uma nova aba por meio de um link temporário privado.

O identificador fica salvo em `sm_pdf_job`, permitindo retomar a consulta após
recarregar a página, inclusive quando o PDF já terminou. Uma falha transitória
habilita Consultar PDF sem criar outra tarefa. Falhas de compilação ou expiração
liberam uma nova geração. Selecionar outra molécula ou executar outra análise
remove a tarefa acompanhada da interface; não cancela a execução no backend.

O contrato de tarefas precisa ser implantado no backend e no Terraform antes
da migração completa. O frontend mantém compatibilidade com `pdf_base64` do
backend antigo durante a publicação.