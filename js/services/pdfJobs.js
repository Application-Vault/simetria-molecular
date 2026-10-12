import { API_CONFIG } from '../config.js';
import { $ } from '../utils/dom.js';
import { t } from '../i18n.js';
import { clearPdfUi, ensureAbrirPdfButton, openPdfInNewTab, setPdfObjectUrl } from './pdfState.js';

const storageKey = 'sm_pdf_job';
const pollInterval = 3000;
let job = null;
let generation = 0;
let timer = null;
let controller = null;
let busy = false;
let pollStartedAt = 0;
let failures = 0;

function saveJob(value) {
    try {
        if (value) localStorage.setItem(storageKey, JSON.stringify(value));
        else localStorage.removeItem(storageKey);
    } catch { }
}

function showPdfStatus(message) {
    const status = $('pdfStatus');
    if (!status) return;
    status.textContent = t(message);
    status.hidden = !message;
}

function updateButton() {
    const button = $('btnGerarPdf');
    if (!button) return;
    button.disabled = busy;
    button.innerHTML = busy
        ? `<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i> ${t('Gerando...')}`
        : `<i class="fa-regular fa-file-pdf" aria-hidden="true"></i> ${t(job ? 'Consultar PDF' : 'Gerar PDF')}`;
}

function reset() {
    generation++;
    clearTimeout(timer);
    controller?.abort();
    job = null;
    busy = false;
    saveJob(null);
    showPdfStatus('');
    updateButton();
}

async function request(url, options = {}) {
    controller = new AbortController();
    const activeController = controller;
    const timeout = setTimeout(() => activeController.abort(), 12000);
    try {
        const response = await fetch(url, { ...options, cache: 'no-store', signal: activeController.signal });
        let data;
        try { data = await response.json(); } catch { throw new Error(t('Resposta inválida ao consultar o PDF.')); }
        if (!response.ok) {
            const error = new Error(t(data.error || data.message || 'Não foi possível processar a tarefa de PDF.'));
            error.status = response.status;
            throw error;
        }
        return data;
    } finally {
        clearTimeout(timeout);
        if (controller === activeController) controller = null;
    }
}

function completed(data) {
    let url;
    if (data.pdf_base64) {
        const bytes = Uint8Array.from(atob(data.pdf_base64), character => character.charCodeAt(0));
        url = URL.createObjectURL(new Blob([bytes], { type: 'application/pdf' }));
        setPdfObjectUrl(url);
        saveJob(null);
    } else {
        if (!job || !data.download_url) throw new Error(t('Resposta inválida ao consultar o PDF.'));
        url = `${API_CONFIG.baseUrlPdf}/${encodeURIComponent(job.job_id)}?download=1`;
        saveJob({ ...job, status: 'completed' });
    }
    const button = ensureAbrirPdfButton();
    button.onclick = () => openPdfInNewTab(url);
    button.style.display = 'inline-block';
    job = null;
    busy = false;
    showPdfStatus('PDF pronto.');
    updateButton();
}

function pause(message) {
    busy = false;
    showPdfStatus(message);
    updateButton();
}

async function poll(token) {
    if (token !== generation || !job) return;
    let data;
    try {
        data = await request(`${API_CONFIG.baseUrlPdf}/${encodeURIComponent(job.job_id)}`);
    } catch (error) {
        if (token !== generation) return;
        if ([400, 404, 410].includes(error.status)) {
            job = null;
            saveJob(null);
            pause(error.message);
            return;
        }
        failures++;
        if (failures >= 3) {
            pause('Não foi possível consultar o PDF. Tente consultar novamente.');
            return;
        }
        showPdfStatus('Reconectando à tarefa de PDF...');
        timer = setTimeout(() => poll(token), pollInterval);
        return;
    }
    if (token !== generation) return;
    failures = 0;
    try {
        if (data.status === 'completed') {
            completed(data);
            return;
        }
        if (data.status === 'failed') {
            job = null;
            saveJob(null);
            pause(data.error || 'Falha ao gerar PDF. Confira o TeX e tente novamente.');
            return;
        }
        if (!['queued', 'processing'].includes(data.status)) throw new Error(t('Resposta inválida ao consultar o PDF.'));
        if (Date.now() - pollStartedAt > 900000) {
            pause('O PDF ainda está em processamento. Consulte novamente.');
            return;
        }
        showPdfStatus(data.status === 'queued' ? 'PDF na fila...' : 'Gerando PDF...');
        timer = setTimeout(() => poll(token), pollInterval);
    } catch (error) {
        pause(error.message);
    }
}

function resume() {
    busy = true;
    failures = 0;
    pollStartedAt = Date.now();
    updateButton();
    showPdfStatus('Consultando tarefa de PDF...');
    poll(generation);
}

async function start() {
    if (busy) return;
    if (job) {
        resume();
        return;
    }
    const tex = $('resultado')?.value || '';
    if (!tex.trim()) {
        alert(t('Ainda não há conteúdo TeX para enviar.'));
        return;
    }
    clearPdfUi();
    const token = generation;
    busy = true;
    updateButton();
    showPdfStatus('Enviando tarefa de PDF...');
    try {
        const data = await request(API_CONFIG.baseUrlPdf, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tex }) });
        if (token !== generation) return;
        if (data.pdf_base64) {
            completed(data);
            return;
        }
        if (!/^[0-9a-f]{32}$/.test(data.job_id || '')) throw new Error(t('Resposta inválida ao consultar o PDF.'));
        job = { job_id: data.job_id, endpoint: API_CONFIG.baseUrlPdf, status: data.status };
        saveJob(job);
        resume();
    } catch (error) {
        if (token === generation) {
            pause(error.name === 'AbortError' ? 'Não foi possível enviar a tarefa de PDF. Tente novamente.' : error.message);
        }
    }
}

export function initPdfJobs() {
    if (!$('btnGerarPdf')) return;
    $('btnGerarPdf').addEventListener('click', start);
    document.addEventListener('pdf-reset', reset);
    document.addEventListener('languagechange', updateButton);
    try {
        const saved = JSON.parse(localStorage.getItem(storageKey));
        if (saved?.endpoint === API_CONFIG.baseUrlPdf && /^[0-9a-f]{32}$/.test(saved.job_id || '')) job = saved;
    } catch { }
    if (job) resume();
}