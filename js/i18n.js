const languages = ['pt', 'en', 'zh'];
const locales = { pt: 'pt-BR', en: 'en', zh: 'zh-CN' };
const storageKey = 'sm_language';
const strings = {
    'Análise de Simetria Molecular': ['Molecular Symmetry Analysis', '分子对称性分析'],
    '🔬 Simetria Molecular': ['🔬 Molecular Symmetry', '🔬 分子对称性'],
    '© 2026 Simetria Molecular': ['© 2026 Molecular Symmetry', '© 2026 分子对称性'],
    '🌐 Projeto': ['🌐 Project', '🌐 项目'],
    'Idioma': ['Language', '语言'],
    'Português': ['Portuguese', '葡萄牙语'],
    'Inglês': ['English', '英语'],
    'Chinês': ['Chinese', '中文'],
    'Molécula': ['Molecule', '分子'],
    'Escolha a molécula': ['Choose a molecule', '选择分子'],
    'Carregando moléculas...': ['Loading molecules...', '正在加载分子…'],
    'Selecione uma molécula ...': ['Select a molecule...', '请选择分子…'],
    'Outra (especifique)': ['Other (specify)', '其他（自行输入）'],
    'Entrada / Coordenadas': ['Input / Coordinates', '输入 / 坐标'],
    'Coordenadas xyz ...': ['XYZ coordinates...', 'XYZ 坐标…'],
    'Visualização': ['Visualization', '可视化'],
    'Viewport': ['Viewport', '视图'],
    'área reservada para 3D / orbitais / MEP': ['3D / orbitals / MEP view', '3D / 轨道 / 分子静电势视图'],
    'Resultado (.tex)': ['Result (.tex)', '结果 (.tex)'],
    'saída do backend / análise selecionada': ['Backend output / selected analysis', '后端输出 / 所选分析'],
    'Copiar': ['Copy', '复制'],
    'Gerar PDF': ['Generate PDF', '生成 PDF'],
    'Análise': ['Analysis', '分析'],
    'Selecione a análise': ['Select an analysis', '选择分析'],
    'Gráfico': ['Graphics', '图形'],
    'Simetria': ['Symmetry', '对称性'],
    'Análises Desejadas': ['Requested analyses', '所需分析'],
    'Identificação do Grupo': ['Group identification', '群识别'],
    'Permutações': ['Permutations', '置换'],
    'Tabela de multiplicação': ['Multiplication table', '乘法表'],
    'Classes de conjugação': ['Conjugacy classes', '共轭类'],
    'Caracteres (Em breve)': ['Characters (Coming soon)', '特征标（即将推出）'],
    'Autovalores (Em breve)': ['Eigenvalues (Coming soon)', '特征值（即将推出）'],
    'Subgrupos (Em breve)': ['Subgroups (Coming soon)', '子群（即将推出）'],
    'Cíclico (Em breve)': ['Cyclic (Coming soon)', '循环群（即将推出）'],
    'Abeliano (Em breve)': ['Abelian (Coming soon)', '阿贝尔群（即将推出）'],
    'Formato de Saída': ['Output format', '输出格式'],
    'Visualização 3D': ['3D visualization', '3D 可视化'],
    'Estilo': ['Style', '样式'],
    'Ball & Stick': ['Ball & Stick', '球棍模型'],
    'Bastões': ['Sticks', '棍状模型'],
    'Esferas': ['Spheres', '球形模型'],
    'Linhas': ['Lines', '线条模型'],
    'Paleta de Cores': ['Color palette', '配色'],
    'Padrão por elemento': ['Default by element', '按元素默认配色'],
    'Pastel': ['Pastel', '柔和色'],
    'Vibrante': ['Vibrant', '鲜艳色'],
    'Monocromática': ['Monochrome', '单色'],
    'Exibição': ['Display', '显示'],
    'Mostrar hidrogênios': ['Show hydrogens', '显示氢原子'],
    'Mostrar labels dos átomos': ['Show atom labels', '显示原子标签'],
    'Rotação automática': ['Automatic rotation', '自动旋转'],
    'Fundo escuro': ['Dark background', '深色背景'],
    'Resetar visualização': ['Reset view', '重置视图'],
    'Analisar Simetria': ['Analyze symmetry', '分析对称性'],
    'Análise de Grupos de Simetria': ['Symmetry group analysis', '对称群分析'],
    'Carregando molécula...': ['Loading molecule...', '正在加载分子…'],
    'Erro ao carregar o XYZ': ['Failed to load XYZ coordinates', '加载 XYZ 坐标失败'],
    'Erro ao carregar lista de moléculas': ['Failed to load the molecule list', '加载分子列表失败'],
    'Erro ao carregar moléculas': ['Failed to load molecules', '加载分子失败'],
    'Processando...': ['Processing...', '正在处理…'],
    'Erro na requisição': ['Request failed', '请求失败'],
    'Erro na análise: {message}': ['Analysis error: {message}', '分析错误：{message}'],
    'Resposta do backend não é JSON. Atualize o backend para retornar { tex, pdf_base64? }.': ['The backend response is not JSON. Update the backend to return { tex, pdf_base64? }.', '后端响应不是 JSON。请更新后端以返回 { tex, pdf_base64? }。'],
    'Ativar tema escuro': ['Switch to dark theme', '切换为深色主题'],
    'Ativar tema claro': ['Switch to light theme', '切换为浅色主题'],
    'Ainda não há conteúdo TeX para copiar.': ['There is no TeX content to copy yet.', '尚无可复制的 TeX 内容。'],
    'Ainda não há conteúdo TeX para enviar.': ['There is no TeX content to send yet.', '尚无可发送的 TeX 内容。'],
    'Não foi possível copiar o conteúdo.': ['Could not copy the content.', '无法复制内容。'],
    'Copiado': ['Copied', '已复制'],
    'Gerando...': ['Generating...', '正在生成…'],
    'Falha ao gerar PDF.': ['Failed to generate PDF.', '生成 PDF 失败。'],
    'Resposta sem pdf_base64.': ['The response does not include pdf_base64.', '响应中没有 pdf_base64。'],
    'Erro ao gerar PDF: {message}': ['PDF generation error: {message}', '生成 PDF 时出错：{message}'],
    '📝 Abrir PDF em outra aba': ['📝 Open PDF in a new tab', '📝 在新标签页中打开 PDF'],
};

Object.assign(strings, {
    'Análise de simetria indisponível para esta molécula. A visualização 3D permanece disponível.': ['Symmetry analysis is unavailable for this molecule. 3D visualization remains available.', '此分子暂不支持对称性分析。3D 可视化仍然可用。'],
    'Abrir PDF': ['Open PDF', '打开 PDF'],
    'Consultar PDF': ['Check PDF', '查询 PDF'],
    'PDF pronto.': ['PDF ready.', 'PDF 已生成。'],
    'PDF na fila...': ['PDF queued...', 'PDF 正在排队…'],
    'Gerando PDF...': ['Generating PDF...', '正在生成 PDF…'],
    'Enviando tarefa de PDF...': ['Submitting PDF job...', '正在提交 PDF 任务…'],
    'Consultando tarefa de PDF...': ['Checking PDF job...', '正在查询 PDF 任务…'],
    'Reconectando à tarefa de PDF...': ['Reconnecting to PDF job...', '正在重新连接 PDF 任务…'],
    'Não foi possível consultar o PDF. Tente consultar novamente.': ['Could not check the PDF. Try checking again.', '无法查询 PDF。请重试。'],
    'O PDF ainda está em processamento. Consulte novamente.': ['The PDF is still processing. Check again.', 'PDF 仍在处理中。请再次查询。'],
    'Não foi possível enviar a tarefa de PDF. Tente novamente.': ['Could not submit the PDF job. Try again.', '无法提交 PDF 任务。请重试。'],
    'Resposta inválida ao consultar o PDF.': ['Invalid PDF job response.', 'PDF 任务响应无效。'],
    'Falha ao gerar PDF. Confira o TeX e tente novamente.': ['Failed to generate PDF. Check the TeX and try again.', '生成 PDF 失败。请检查 TeX 后重试。'],
    'Tarefa de PDF não encontrada ou expirada.': ['PDF job not found or expired.', 'PDF 任务不存在或已过期。'],
    'A tarefa de PDF expirou. Gere o PDF novamente.': ['The PDF job expired. Generate the PDF again.', 'PDF 任务已过期。请重新生成 PDF。'],
    'Geração assíncrona de PDF indisponível.': ['Asynchronous PDF generation is unavailable.', '异步 PDF 生成功能不可用。'],
    'Não foi possível processar a tarefa de PDF.': ['Could not process the PDF job.', '无法处理 PDF 任务。'],
    'Não foi possível agendar a geração do PDF.': ['Could not schedule PDF generation.', '无法安排 PDF 生成任务。'],
    "Campo 'tex' vazio.": ['The TeX field is empty.', 'TeX 内容为空。'],
    'O relatório TeX excede o limite de 2 MB.': ['The TeX report exceeds the 2 MB limit.', 'TeX 报告超过 2 MB 限制。'],
});

let language = 'pt';
const textStates = new WeakMap();
const attributeStates = new WeakMap();
const renderedStrings = new Map();
const attributes = ['title', 'aria-label', 'placeholder', 'alt'];
const excluded = 'script, style, textarea, pre, code, [data-i18n-ignore]';
const originalTitle = document.title;

export function t(source, values = {}) {
    const entry = strings[source];
    const template = language === 'pt' || !entry ? source : entry[language === 'en' ? 0 : 1];
    const rendered = template.replace(/\{(\w+)\}/g, (match, key) => String(values[key] ?? match));
    renderedStrings.set(rendered, { source, values });
    return rendered;
}

export function getLocale() {
    return locales[language];
}

export function getLanguage() {
    return language;
}

function localizeText(node) {
    if (node.parentElement?.closest(excluded)) return;
    const raw = node.nodeValue;
    if (!raw?.trim()) return;
    const previous = textStates.get(node);
    const content = raw.trim();
    const normalized = content.replace(/\s+/g, ' ');
    const state = previous?.output === raw
        ? previous
        : renderedStrings.get(content) || { source: strings[normalized] ? normalized : content, values: {} };
    const output = raw.match(/^\s*/)[0] + t(state.source, state.values) + raw.match(/\s*$/)[0];
    textStates.set(node, { ...state, output });
    if (output !== raw) node.nodeValue = output;
}

function localizeAttribute(element, attribute) {
    if (element.closest('[data-i18n-ignore]')) return;
    const raw = element.getAttribute(attribute);
    if (raw === null) return;
    let states = attributeStates.get(element);
    if (!states) {
        states = new Map();
        attributeStates.set(element, states);
    }
    const previous = states.get(attribute);
    const state = previous?.output === raw ? previous : renderedStrings.get(raw) || { source: raw, values: {} };
    const output = t(state.source, state.values);
    states.set(attribute, { ...state, output });
    if (output !== raw) element.setAttribute(attribute, output);
}

function localize(root) {
    if (root.nodeType === Node.TEXT_NODE) {
        localizeText(root);
        return;
    }
    if (root.nodeType !== Node.ELEMENT_NODE || root.closest('[data-i18n-ignore]')) return;
    for (const attribute of attributes) localizeAttribute(root, attribute);
    if (root.matches(excluded)) return;
    for (const child of root.childNodes) localize(child);
}

export function setLanguage(nextLanguage, persist = true) {
    if (!languages.includes(nextLanguage)) return;
    language = nextLanguage;
    document.documentElement.lang = locales[language];
    if (persist) {
        try { localStorage.setItem(storageKey, language); } catch { }
    }
    localize(document.body);
    document.title = t(originalTitle);
    document.querySelectorAll('[data-language]').forEach(button => {
        button.setAttribute('aria-pressed', String(button.dataset.language === language));
    });
    document.dispatchEvent(new CustomEvent('languagechange', { detail: { language } }));
}

export function initLanguage() {
    let saved = 'pt';
    try { saved = localStorage.getItem(storageKey) || 'pt'; } catch { }
    document.querySelectorAll('[data-language]').forEach(button => {
        button.addEventListener('click', () => setLanguage(button.dataset.language));
    });
    setLanguage(languages.includes(saved) ? saved : 'pt', false);
    const observer = new MutationObserver(records => {
        for (const record of records) {
            if (record.type === 'characterData') localizeText(record.target);
            if (record.type === 'attributes') localizeAttribute(record.target, record.attributeName);
            for (const node of record.addedNodes) localize(node);
        }
    });
    observer.observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: attributes });
}