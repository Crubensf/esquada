// ─── Constantes ───────────────────────────────────────────────────────────────

// Chaves do localStorage para persistir o estado e o histórico
const STORAGE_KEY = 'esquada:web:assessment:v1';
const HISTORY_KEY = 'esquada:web:history:v1';
const MAX_HISTORY = 20; // número máximo de entradas salvas no histórico

// Slug CSS por categoria — usado para montar nomes de classe dinamicamente
const CAT_SLUG = {
  'muito ruim': 'muito-ruim',
  'ruim':       'ruim',
  'boa':        'boa',
  'muito boa':  'muito-boa',
  'excelente':  'excelente',
};

// Classe CSS completa de badge por categoria (derivada de CAT_SLUG)
const CAT_BADGE_CLASS = Object.fromEntries(
  Object.entries(CAT_SLUG).map(([k, v]) => [k, `cat-badge-${v}`])
);

// Rótulo exibido para cada categoria
const CAT_LABELS = {
  'muito ruim': 'Muito ruim',
  'ruim':       'Ruim',
  'boa':        'Boa',
  'muito boa':  'Muito boa',
  'excelente':  'Excelente',
};

// Paleta de cores escuras — usada no gráfico de evolução do histórico
const CAT_COLOR = {
  'muito ruim': '#4a5a72',
  'ruim':       '#8c4e28',
  'boa':        '#8a6a10',
  'muito boa':  '#1e5e48',
  'excelente':  '#142e1e',
};

// Paleta de cores vivas — usada no gráfico de rosca do dashboard
const CAT_COLORS = {
  'muito ruim': '#d94f4f',
  'ruim':       '#e8874a',
  'boa':        '#f0c040',
  'muito boa':  '#6abf6a',
  'excelente':  '#2e8b57',
};


// ─── Elementos do DOM ─────────────────────────────────────────────────────────

// Views (seções de página)
const viewHome       = document.getElementById('view-home');
const viewQuiz       = document.getElementById('view-quiz');
const viewResult     = document.getElementById('view-result');
const viewHistory    = document.getElementById('view-history');
const viewResearcher = document.getElementById('view-researcher');
const viewInfo       = document.getElementById('view-info');

// Auth
const btnAuthHeader     = document.getElementById('btn-auth-header');
const authModal         = document.getElementById('auth-modal');
const btnCloseAuth      = document.getElementById('btn-close-auth');
const formLogin         = document.getElementById('form-login');
const formRegister      = document.getElementById('form-register');
const loginError        = document.getElementById('login-error');
const registerError     = document.getElementById('register-error');
const btnLoginSubmit    = document.getElementById('btn-login-submit');
const btnRegisterSubmit = document.getElementById('btn-register-submit');
const researcherUserBar = document.getElementById('researcher-user-bar');
const userBarName       = document.getElementById('user-bar-name');
const userBarEmail      = document.getElementById('user-bar-email');
const userAvatarEl      = document.getElementById('user-avatar-initials');
const btnLogout         = document.getElementById('btn-logout');

// Auth — cadastro em dois passos
const registerStep1      = document.getElementById('register-step-1');
const registerStep2      = document.getElementById('register-step-2');
const registerEmailSent  = document.getElementById('register-email-sent');
const registerCode       = document.getElementById('register-code');
const registerCodeError  = document.getElementById('register-code-error');
const btnVerifySubmit    = document.getElementById('btn-verify-submit');
const btnResendCode      = document.getElementById('btn-resend-code');
const btnRegisterBack    = document.getElementById('btn-register-back');

// Cabeçalho e navegação
const btnStart            = document.getElementById('btn-start');
const btnStartHeader      = document.getElementById('btn-start-header');
const btnResearcherHeader = document.getElementById('btn-researcher-header');
const btnHome             = document.getElementById('btn-home');
const btnHome2            = document.getElementById('btn-home-2');
const btnRestart          = document.getElementById('btn-restart');
const btnBack             = document.getElementById('btn-back');
const btnBackResearcher   = document.getElementById('btn-back-researcher');
const btnMenu             = document.getElementById('btn-menu');
const nav                 = document.querySelector('.nav');

// Quiz
const btnPrev        = document.getElementById('btn-prev');
const btnNext        = document.getElementById('btn-next');
const progress       = document.getElementById('quiz-progress');
const progressBar    = document.getElementById('quiz-progress-bar');
const progressFill   = document.getElementById('quiz-progress-fill');
const progressPercent= document.getElementById('quiz-progress-percent');
const qText          = document.getElementById('q-text');
const qOptions       = document.getElementById('q-options');

// Resultado individual
const gradeEl       = document.getElementById('result-grade');
const textEl        = document.getElementById('result-text');
const valF1         = document.getElementById('val-f1');
const valSE         = document.getElementById('val-se');
const valF1novo     = document.getElementById('val-f1novo');
const liquidFill    = document.getElementById('liquid-fill');
const resultPercent = document.getElementById('result-percent');

// Card de score na home
const btnHomeScore   = document.getElementById('btn-home-score');
const homeScoreLabel = document.getElementById('home-score-label');
const homeScoreValue = document.getElementById('home-score-value');
const homeScoreMeta  = document.getElementById('home-score-meta');

// Área do pesquisador — upload
const researcherCsvForm   = document.getElementById('researcher-csv-form');
const researcherCsvFile   = document.getElementById('researcher-csv-file');
const uploadZone          = document.getElementById('upload-zone');
const uploadLabel         = document.getElementById('upload-label');
const btnResearcherSubmit = document.getElementById('btn-researcher-submit');
const researcherStatus    = document.getElementById('researcher-status');

// Dashboard do pesquisador
const analysisDashboard  = document.getElementById('analysis-dashboard');
const uploadPanel        = document.getElementById('upload-panel');
const btnNewAnalysis     = document.getElementById('btn-new-analysis');
const btnDownloadResults = document.getElementById('btn-download-results');
const dashStats          = document.getElementById('dash-stats');
const dashDonutSvg       = document.getElementById('dash-donut-svg');
const dashDonutLegend    = document.getElementById('dash-donut-legend');
const dashHistSvg        = document.getElementById('dash-hist-svg');
const dashItemsSvg       = document.getElementById('dash-items-svg');
const dashErrorsPanel    = document.getElementById('dash-errors');
const dashErrorsTbody    = document.getElementById('dash-errors-tbody');
const dashErrorsCount    = document.getElementById('dash-errors-count');
const dashResultsTbody   = document.getElementById('dash-results-tbody');
const dashResultsCount   = document.getElementById('dash-results-count');
const dashFilename       = document.getElementById('dash-filename');


// ─── Estado da aplicação ──────────────────────────────────────────────────────

let currentUser     = null; // usuário autenticado ({id, name, email}) ou null
let schema          = null; // schema dos 25 itens recebido de /api/schema
let current         = 0;    // índice da pergunta atual no quiz
let answers         = [];   // respostas selecionadas (índice da opção por pergunta)
let lastResult      = null; // último resultado calculado
let lastView        = 'home';
let pendingRegister = null; // dados do passo 1 do cadastro aguardando verificação de e-mail

let _lastCsvB64 = null; // CSV pontuado em base64 para download no dashboard


// ─── Persistência (localStorage) ─────────────────────────────────────────────

// Chaves são personalizadas por usuário quando logado
function getStorageKey(){ return currentUser ? `${STORAGE_KEY}:${currentUser.id}` : STORAGE_KEY; }
function getHistoryKey(){ return currentUser ? `${HISTORY_KEY}:${currentUser.id}` : HISTORY_KEY; }

function loadSavedAssessment(){
  try {
    const raw = localStorage.getItem(getStorageKey());
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (_err) {
    return null;
  }
}

/** Normaliza o array de respostas para o tamanho esperado, preenchendo com null. */
function normalizeAnswers(rawAnswers, length){
  const list = Array.isArray(rawAnswers) ? rawAnswers : [];
  return Array.from({ length }, (_, idx) => {
    const value = list[idx];
    return Number.isInteger(value) ? value : null;
  });
}

function clamp(value, min, max){
  return Math.max(min, Math.min(max, value));
}

/** Retorna o índice da primeira pergunta sem resposta, ou a última se todas respondidas. */
function getDefaultQuestionIndex(list){
  const firstEmpty = list.findIndex(value => value == null);
  return firstEmpty === -1 ? Math.max(list.length - 1, 0) : firstEmpty;
}

function hasSavedProgress(state = null){
  const source = state || loadSavedAssessment();
  if (!source) return false;
  const savedAnswers = Array.isArray(source.answers) ? source.answers : [];
  return savedAnswers.some(value => Number.isInteger(value)) || !!source.result;
}

function updateStartLabels(){
  const hasProgress = hasSavedProgress();
  if (btnStart)       btnStart.textContent       = hasProgress ? 'Refazer avaliação' : 'Começar avaliação';
  if (btnStartHeader) btnStartHeader.textContent = hasProgress ? 'Refazer avaliação' : 'Começar avaliação';
}

function updateHomeScoreCard(state = null){
  if (!homeScoreLabel || !homeScoreValue || !homeScoreMeta) return;
  const source        = state || { answers, result: lastResult };
  const sourceAnswers = Array.isArray(source.answers) ? source.answers : [];
  const answered      = sourceAnswers.filter(value => Number.isInteger(value)).length;
  let result          = source.result || null;

  // Fallback: usa o resultado mais recente do histórico se não houver resultado no estado
  if (!result) {
    const hist = loadHistory();
    if (hist.length > 0) result = hist[0];
  }

  if (result && typeof result.F1novo === 'number'){
    const category = result["escore.cat.novo"] || 'sem categoria';
    homeScoreLabel.textContent = 'Score atual';
    homeScoreValue.textContent = `${result.F1novo.toFixed(1)} pontos`;
    homeScoreMeta.textContent  = `Categoria atual: ${category}. Clique para abrir o resultado salvo.`;
    if (btnHomeScore){ btnHomeScore.disabled = false; btnHomeScore.classList.add('is-interactive'); }
    return;
  }

  if (answered > 0){
    homeScoreLabel.textContent = 'Avaliação em andamento';
    homeScoreValue.textContent = `${answered}/25 respostas`;
    homeScoreMeta.textContent  = 'Seu progresso está salvo. Clique para continuar de onde você parou.';
    if (btnHomeScore){ btnHomeScore.disabled = false; btnHomeScore.classList.add('is-interactive'); }
    return;
  }

  homeScoreLabel.textContent = 'Score atual';
  homeScoreValue.textContent = 'Sem resultado salvo';
  homeScoreMeta.textContent  = 'Finalize a avaliação para ver sua pontuação na escala 250/50.';
  if (btnHomeScore){ btnHomeScore.disabled = true; btnHomeScore.classList.remove('is-interactive'); }
}

function saveAssessmentState(){
  const state = { answers, current, result: lastResult, lastView };
  try { localStorage.setItem(getStorageKey(), JSON.stringify(state)); } catch (_err) {}
  updateStartLabels();
  updateHomeScoreCard(state);
}


// ─── Histórico ────────────────────────────────────────────────────────────────

function loadHistory(){
  try { return JSON.parse(localStorage.getItem(getHistoryKey()) || '[]'); } catch(_){ return []; }
}

function saveToHistory(result){
  const hist = loadHistory();
  hist.unshift({ ...result, date: new Date().toISOString() });
  if (hist.length > MAX_HISTORY) hist.length = MAX_HISTORY;
  try { localStorage.setItem(getHistoryKey(), JSON.stringify(hist)); } catch(_){}
}

/** Formata uma data ISO em pt-BR com dia, mês, ano e hora. */
function fmtDate(iso){
  const d = new Date(iso);
  return d.toLocaleDateString('pt-BR', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' });
}

function catLabel(cat){ return cat ? cat[0].toUpperCase() + cat.slice(1) : '—'; }

/** Desenha o gráfico SVG de evolução do histórico. */
function buildChart(hist){
  const svg = document.getElementById('history-chart-svg');
  if (!svg) return;

  // Mede a largura real do container para que o viewBox bata 1:1 sem distorção
  const wrap    = svg.parentElement;
  const measured = wrap ? wrap.clientWidth : 0;
  const W = Math.max(360, Math.round(measured || 800));
  const H = 220, pad = { top:24, right:24, bottom:32, left:48 };
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);

  const innerW = W - pad.left - pad.right;
  const innerH = H - pad.top - pad.bottom;
  const yMin = 150, yMax = 420;
  const pts = [...hist].reverse(); // ordem cronológica
  const n   = pts.length;

  const toX = i => pad.left + (n < 2 ? innerW / 2 : (i / (n-1)) * innerW);
  const toY = v => pad.top + innerH - ((Math.min(Math.max(v, yMin), yMax) - yMin) / (yMax - yMin)) * innerH;

  let out = '';

  // Linhas de grade horizontais
  [200, 275, 375].forEach(v => {
    const y = toY(v);
    out += `<line x1="${pad.left}" y1="${y}" x2="${W - pad.right}" y2="${y}" stroke="rgba(104,117,111,.18)" stroke-width="1" stroke-dasharray="4 4"/>`;
    out += `<text x="${pad.left - 6}" y="${y + 4}" text-anchor="end" font-size="10" fill="rgba(104,117,111,.7)">${v}</text>`;
  });

  // Área preenchida abaixo da linha
  if (n > 1){
    const areaPoints = pts.map((p, i) => `${toX(i)},${toY(p.F1novo)}`).join(' ');
    const lastX = toX(n-1), firstX = toX(0), baseY = pad.top + innerH;
    out += `<defs><linearGradient id="area-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#214f3d" stop-opacity=".15"/><stop offset="100%" stop-color="#214f3d" stop-opacity="0"/></linearGradient></defs>`;
    out += `<polygon points="${firstX},${baseY} ${areaPoints} ${lastX},${baseY}" fill="url(#area-grad)"/>`;

    const lineD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${toX(i)},${toY(p.F1novo)}`).join(' ');
    out += `<path d="${lineD}" fill="none" stroke="#2f6d52" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>`;
  }

  // Pontos coloridos por categoria
  pts.forEach((p, i) => {
    const x   = toX(i), y = toY(p.F1novo);
    const col = CAT_COLOR[p['escore.cat.novo']] || '#214f3d';
    out += `<circle cx="${x}" cy="${y}" r="6" fill="${col}" stroke="#fff" stroke-width="2"/>`;
    out += `<text x="${x}" y="${y - 11}" text-anchor="middle" font-size="10" font-weight="700" fill="${col}">${Math.round(p.F1novo)}</text>`;
  });

  // Eixo X: mostra todos os rótulos se forem poucos, senão só o primeiro e o último
  const showIdx = n <= 5 ? pts.map((_, i) => i) : [0, n-1];
  showIdx.forEach(i => {
    const d     = new Date(pts[i].date);
    const label = d.toLocaleDateString('pt-BR', { day:'2-digit', month:'short' });
    out += `<text x="${toX(i)}" y="${H - 6}" text-anchor="middle" font-size="10" fill="rgba(104,117,111,.7)">${label}</text>`;
  });

  svg.innerHTML = out;
}

function renderHistory(){
  const hist      = loadHistory();
  const emptyEl   = document.getElementById('history-empty');
  const contentEl = document.getElementById('history-content');
  const statsEl   = document.getElementById('history-stats');
  const listEl    = document.getElementById('history-list');

  if (hist.length === 0){
    emptyEl.classList.remove('hidden');
    contentEl.classList.add('hidden');
    return;
  }
  emptyEl.classList.add('hidden');
  contentEl.classList.remove('hidden');

  // Resumo estatístico do histórico
  const scores = hist.map(h => h.F1novo);
  const best   = Math.max(...scores);
  const avg    = scores.reduce((a,b) => a+b, 0) / scores.length;
  const last   = hist[0].F1novo;
  const trend  = hist.length > 1 ? last - hist[1].F1novo : null;
  statsEl.innerHTML = `
    <div class="hstat"><span class="hstat-label">Avaliações</span><span class="hstat-value">${hist.length}</span><span class="hstat-sub">no total</span></div>
    <div class="hstat"><span class="hstat-label">Último escore</span><span class="hstat-value">${last.toFixed(1)}</span><span class="hstat-sub">${catLabel(hist[0]['escore.cat.novo'])}</span></div>
    <div class="hstat"><span class="hstat-label">Melhor escore</span><span class="hstat-value">${best.toFixed(1)}</span><span class="hstat-sub">histórico</span></div>
    <div class="hstat"><span class="hstat-label">Variação</span><span class="hstat-value" style="color:${trend === null ? 'inherit' : trend >= 0 ? '#1e5e48' : '#8c4e28'}">${trend === null ? '—' : (trend >= 0 ? '+' : '') + trend.toFixed(1)}</span><span class="hstat-sub">vs. anterior</span></div>
  `;

  buildChart(hist);

  listEl.innerHTML = hist.map((h, i) => {
    const slug = CAT_SLUG[h['escore.cat.novo']] || 'boa';
    return `
      <div class="hcard" data-idx="${i}">
        <span class="hcard-num">${i+1}</span>
        <div class="hcard-body">
          <div class="hcard-date">${fmtDate(h.date)}</div>
          <div class="hcard-score">${h.F1novo.toFixed(1)} pts</div>
          <span class="hcard-cat cat-badge-${slug}">${catLabel(h['escore.cat.novo'])}</span>
        </div>
        <div class="hcard-pills">
          <span class="hcard-pill">F1 <strong>${h.F1.toFixed(3)}</strong></span>
          <span class="hcard-pill">SE <strong>${h.SE_F1.toFixed(3)}</strong></span>
        </div>
      </div>
    `;
  }).join('');

  // Clique em um card abre o resultado correspondente
  listEl.querySelectorAll('.hcard').forEach(card => {
    card.addEventListener('click', () => {
      const h = hist[+card.dataset.idx];
      showResult(h, false);
    });
  });
}

function openHistory(){
  if (!currentUser) { openAuthModal('login'); return; }
  show(viewHistory);
  renderHistory();
}

// Redesenha o gráfico ao redimensionar a janela, evitando distorção do SVG
let _chartResizeTimer = null;
window.addEventListener('resize', () => {
  if (viewHistory.classList.contains('hidden')) return;
  clearTimeout(_chartResizeTimer);
  _chartResizeTimer = setTimeout(() => {
    const hist = loadHistory();
    if (hist.length) buildChart(hist);
  }, 150);
});


// ─── Saiba mais ───────────────────────────────────────────────────────────────

function openInfo(){
  show(viewInfo);
}

document.getElementById('btn-back-info').addEventListener('click', goHome);
document.getElementById('btn-info-nav').addEventListener('click', openInfo);
document.getElementById('btn-info-footer').addEventListener('click', openInfo);

document.querySelectorAll('.faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!expanded));
    btn.nextElementSibling.hidden = expanded;
  });
});

document.getElementById('btn-back-history').addEventListener('click', goHome);
document.getElementById('btn-history-nav').addEventListener('click', openHistory);
document.getElementById('btn-view-history').addEventListener('click', openHistory);
document.getElementById('btn-start-from-history').addEventListener('click', startQuiz);
document.getElementById('btn-clear-history').addEventListener('click', () => {
  if (!confirm('Apagar todo o histórico?')) return;
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
});


// ─── Navegação ────────────────────────────────────────────────────────────────

// Mapeamento de ID de view para fragmento de URL (deep linking)
const VIEW_HASH = {
  'view-home':       '',
  'view-quiz':       'quiz',
  'view-result':     'resultado',
  'view-history':    'historico',
  'view-researcher': 'pesquisadores',
  'view-info':       'saiba-mais',
};

/** Exibe a view indicada e oculta todas as demais. Atualiza URL e foco. */
function show(el){
  [viewHome, viewQuiz, viewResult, viewResearcher, viewHistory, viewInfo].forEach(v => v.classList.add('hidden'));
  el.classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });

  const hash = VIEW_HASH[el.id];
  if (typeof history !== 'undefined' && history.pushState) {
    history.pushState({ view: el.id }, '', hash ? `#${hash}` : location.pathname + location.search);
  }

  if (el !== viewHome) {
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('nav-active'));
  }

  // Move o foco para o título da view (acessibilidade)
  requestAnimationFrame(() => {
    const target = el.querySelector('h1, [tabindex="-1"]');
    if (target) target.focus({ preventScroll: true });
  });
}

// Suporte ao botão "Voltar" do navegador
window.addEventListener('popstate', (e) => {
  const viewId = e.state?.view;
  if (!viewId) { goHome(); return; }
  const el = document.getElementById(viewId);
  if (!el) { goHome(); return; }
  [viewHome, viewQuiz, viewResult, viewResearcher, viewHistory, viewInfo].forEach(v => v.classList.add('hidden'));
  el.classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'instant' });
});

function goHome(){
  lastView = 'home';
  saveAssessmentState();
  show(viewHome);
}

[btnHome, btnHome2].filter(Boolean).forEach(el => el.addEventListener('click', goHome));

// Botões de seção no nav: vai para home e rola até a seção correspondente
document.querySelectorAll('[data-nav-section]').forEach(btn => {
  btn.addEventListener('click', () => {
    const sectionId = btn.dataset.navSection;
    goHome();
    requestAnimationFrame(() => {
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    if (nav) nav.classList.remove('nav-open');
    document.querySelector('.site-header')?.classList.remove('menu-open');
  });
});


// ─── Auth ─────────────────────────────────────────────────────────────────────

/** Retorna as iniciais do nome (até 2 letras). */
function getInitials(name){
  return (name || '?').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase();
}

/** Atualiza a barra de usuário e o botão do header conforme o estado de autenticação. */
function updateUserBar(){
  if (researcherUserBar){
    if (currentUser){
      researcherUserBar.classList.remove('hidden');
      userBarName.textContent  = currentUser.name;
      userBarEmail.textContent = currentUser.email;
      userAvatarEl.textContent = getInitials(currentUser.name);
    } else {
      researcherUserBar.classList.add('hidden');
    }
  }
  if (btnAuthHeader){
    if (currentUser){
      btnAuthHeader.classList.add('is-logged-in');
      btnAuthHeader.innerHTML = `<span class="header-avatar">${getInitials(currentUser.name)}</span>${currentUser.name.split(' ')[0]}`;
    } else {
      btnAuthHeader.classList.remove('is-logged-in');
      btnAuthHeader.textContent = 'Entrar';
    }
  }
}

/** Verifica com o servidor se há uma sessão ativa e atualiza currentUser. */
async function checkAuth(){
  try {
    const res = await fetch('/api/auth/me', { credentials: 'include' });
    const data = await res.json();
    currentUser = data.user || null;
  } catch (_) {
    currentUser = null;
  }
  updateUserBar();
  return currentUser;
}

function openAuthModal(tab = 'login'){
  switchAuthTab(tab);
  loginError.classList.add('hidden');
  registerError.classList.add('hidden');
  authModal.showModal();
}

function closeAuthModal(){
  authModal.close();
}

function switchAuthTab(tab){
  document.querySelectorAll('.auth-tab').forEach(t =>
    t.classList.toggle('active', t.dataset.tab === tab)
  );
  formLogin.classList.toggle('hidden', tab !== 'login');
  formRegister.classList.toggle('hidden', tab !== 'register');
  if (tab === 'register') resetRegisterForm();
}

if (btnCloseAuth) btnCloseAuth.addEventListener('click', closeAuthModal);

authModal.addEventListener('click', (e) => {
  if (e.target === authModal) closeAuthModal();
});

document.querySelectorAll('.auth-tab').forEach(tab =>
  tab.addEventListener('click', () => switchAuthTab(tab.dataset.tab))
);

document.querySelectorAll('.auth-switch-btn').forEach(btn =>
  btn.addEventListener('click', () => switchAuthTab(btn.dataset.tab))
);

formLogin.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.classList.add('hidden');
  btnLoginSubmit.disabled = true;
  btnLoginSubmit.textContent = 'Entrando…';
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email:    document.getElementById('login-email').value,
        password: document.getElementById('login-password').value,
      }),
    });
    const data = await res.json();
    if (!res.ok){ loginError.textContent = data.error; loginError.classList.remove('hidden'); return; }
    currentUser = data.user;
    updateUserBar();
    closeAuthModal();
    showResearcher();
  } catch (_) {
    loginError.textContent = 'Erro de conexão. Tente novamente.';
    loginError.classList.remove('hidden');
  } finally {
    btnLoginSubmit.disabled = false;
    btnLoginSubmit.textContent = 'Entrar';
  }
});

/** Reseta o formulário de cadastro para o passo 1. */
function resetRegisterForm(){
  registerStep1.classList.remove('hidden');
  registerStep2.classList.add('hidden');
  registerError.classList.add('hidden');
  if (registerCodeError) {
    registerCodeError.classList.add('hidden');
    registerCodeError.removeAttribute('style');
  }
  if (registerCode) registerCode.value = '';
  pendingRegister = null;
}

// Passo 1: valida campos e envia código de verificação
formRegister.addEventListener('submit', async (e) => {
  e.preventDefault();
  registerError.classList.add('hidden');

  const name  = document.getElementById('register-name').value.trim();
  const inst  = document.getElementById('register-institution').value.trim();
  const email = document.getElementById('register-email').value.trim();
  const pw    = document.getElementById('register-password').value;
  const pw2   = document.getElementById('register-password2').value;

  if (!name || !inst || !email || !pw || !pw2) {
    registerError.textContent = 'Preencha todos os campos obrigatórios.';
    registerError.classList.remove('hidden'); return;
  }
  if (pw.length < 8 || !/\d/.test(pw) || !/[^a-zA-Z0-9]/.test(pw)) {
    registerError.textContent = 'A senha não atende aos requisitos de segurança.';
    registerError.classList.remove('hidden'); return;
  }
  if (pw !== pw2) {
    registerError.textContent = 'As senhas não coincidem.';
    registerError.classList.remove('hidden'); return;
  }

  btnRegisterSubmit.disabled = true;
  btnRegisterSubmit.textContent = 'Enviando código…';
  try {
    const res  = await fetch('/api/auth/send-verification', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    const data = await res.json();
    if (!res.ok) {
      registerError.textContent = data.error;
      registerError.classList.remove('hidden'); return;
    }
    pendingRegister = { name, institution: inst, email, password: pw };
    registerEmailSent.textContent = email;
    registerStep1.classList.add('hidden');
    registerStep2.classList.remove('hidden');
    registerCode.value = '';
    registerCode.focus();
    // Modo desenvolvimento: exibe o código na tela
    if (data.dev_code) {
      registerCodeError.textContent = `Modo desenvolvimento — código: ${data.dev_code}`;
      registerCodeError.style.background    = 'var(--brand-tint)';
      registerCodeError.style.color         = 'var(--brand-darker)';
      registerCodeError.style.borderColor   = 'var(--brand-soft)';
      registerCodeError.classList.remove('hidden');
    }
  } catch (_) {
    registerError.textContent = 'Erro de conexão. Tente novamente.';
    registerError.classList.remove('hidden');
  } finally {
    btnRegisterSubmit.disabled = false;
    btnRegisterSubmit.textContent = 'Continuar';
  }
});

// Passo 2: valida código e cria a conta
btnVerifySubmit.addEventListener('click', async () => {
  registerCodeError.classList.add('hidden');
  registerCodeError.removeAttribute('style');

  const code = registerCode.value.trim();
  if (!code || code.length !== 6) {
    registerCodeError.textContent = 'Digite o código de 6 dígitos enviado por e-mail.';
    registerCodeError.classList.remove('hidden'); return;
  }
  if (!pendingRegister) return;

  btnVerifySubmit.disabled = true;
  btnVerifySubmit.textContent = 'Verificando…';
  try {
    const res  = await fetch('/api/auth/register', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...pendingRegister, code }),
    });
    const data = await res.json();
    if (!res.ok) {
      registerCodeError.textContent = data.error;
      registerCodeError.classList.remove('hidden'); return;
    }
    currentUser = data.user;
    pendingRegister = null;
    updateUserBar();
    closeAuthModal();
    showResearcher();
  } catch (_) {
    registerCodeError.textContent = 'Erro de conexão. Tente novamente.';
    registerCodeError.classList.remove('hidden');
  } finally {
    btnVerifySubmit.disabled = false;
    btnVerifySubmit.textContent = 'Verificar e criar conta';
  }
});

// Reenviar código
btnResendCode.addEventListener('click', async () => {
  if (!pendingRegister) return;
  registerCodeError.classList.add('hidden');
  registerCodeError.removeAttribute('style');
  btnResendCode.disabled = true;
  btnResendCode.textContent = 'Reenviando…';
  try {
    const res  = await fetch('/api/auth/send-verification', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: pendingRegister.email }),
    });
    const data = await res.json();
    if (!res.ok) {
      registerCodeError.textContent = data.error;
      registerCodeError.classList.remove('hidden');
    } else {
      registerCodeError.style.background  = 'var(--brand-tint)';
      registerCodeError.style.color       = 'var(--brand-darker)';
      registerCodeError.style.borderColor = 'var(--brand-soft)';
      registerCodeError.textContent = data.dev_code
        ? `Código reenviado. (dev: ${data.dev_code})`
        : 'Código reenviado. Verifique seu e-mail.';
      registerCodeError.classList.remove('hidden');
    }
  } catch (_) {
    registerCodeError.textContent = 'Erro de conexão.';
    registerCodeError.classList.remove('hidden');
  } finally {
    // Bloqueia reenvio por 30 s para evitar spam
    setTimeout(() => {
      btnResendCode.disabled = false;
      btnResendCode.textContent = 'Reenviar código';
    }, 30000);
  }
});

// Voltar ao passo 1
btnRegisterBack.addEventListener('click', () => {
  resetRegisterForm();
  pendingRegister = null;
});

if (btnLogout) btnLogout.addEventListener('click', async () => {
  await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
  currentUser = null;
  updateUserBar();
  goHome();
});


// ─── Área do pesquisador ──────────────────────────────────────────────────────

function showResearcher(){
  lastView = 'researcher';
  updateUserBar();
  show(viewResearcher);
}

async function openResearcher(){
  if (!currentUser) await checkAuth();
  if (!currentUser){ openAuthModal('login'); return; }
  showResearcher();
}

if (btnResearcherHeader) btnResearcherHeader.addEventListener('click', openResearcher);
if (btnAuthHeader) btnAuthHeader.addEventListener('click', () => {
  if (currentUser) openResearcher();
  else openAuthModal('login');
});
if (btnBackResearcher) btnBackResearcher.addEventListener('click', goHome);
document.querySelectorAll('[data-action="open-researcher"]').forEach(el =>
  el.addEventListener('click', openResearcher)
);

if (btnMenu && nav) {
  const siteHeader = document.querySelector('.site-header');
  btnMenu.addEventListener('click', () => {
    const opening = !nav.classList.contains('nav-open');
    nav.classList.toggle('nav-open');
    if (siteHeader) siteHeader.classList.toggle('menu-open', opening);
  });
}


// ─── Quiz ─────────────────────────────────────────────────────────────────────

async function startQuiz(){
  await ensureSchema();
  current    = 0;
  answers    = Array(schema.items.length).fill(null);
  lastResult = null;
  lastView   = 'quiz';
  saveAssessmentState();
  renderQuestion();
  show(viewQuiz);
}

[
  btnStart,
  btnStartHeader,
  ...document.querySelectorAll('[data-action="start-quiz"]')
].filter(Boolean).forEach(el => el.addEventListener('click', startQuiz));

btnBack.addEventListener('click', goHome);

btnPrev.addEventListener('click', () => {
  if (current > 0){
    current--;
    lastView = 'quiz';
    saveAssessmentState();
    renderQuestion();
  }
});

btnNext.addEventListener('click', async () => {
  if (current < schema.items.length - 1){
    current++;
    lastView = 'quiz';
    saveAssessmentState();
    renderQuestion();
  } else {
    // Última pergunta: converte índices de opção em categorias de escore e envia para a API
    const scoredAnswers = answers.map((displayIndex, idx) => {
      const item = schema.items[idx];
      if (displayIndex == null) return null;
      if (item.score_map && item.score_map[displayIndex] != null)
        return Number(item.score_map[displayIndex]);
      return Number(displayIndex);
    });
    if (scoredAnswers.every(v => v == null)){
      alert('Responda pelo menos uma pergunta antes de finalizar.');
      return;
    }
    const res = await fetch('/api/score_rows', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rows: [scoredAnswers] }),
    });
    if (!res.ok){ const err = await res.json().catch(() => ({})); alert('Erro: ' + (err.error || res.statusText)); return; }
    const data = await res.json();
    showResult(data.results[0], true);
  }
});

btnRestart.addEventListener('click', async () => {
  await ensureSchema();
  answers    = normalizeAnswers(answers, schema.items.length);
  current    = getDefaultQuestionIndex(answers);
  lastResult = null;
  lastView   = 'quiz';
  saveAssessmentState();
  renderQuestion();
  show(viewQuiz);
});

if (btnHomeScore){
  btnHomeScore.addEventListener('click', async () => {
    if (btnHomeScore.disabled) return;
    const saved = loadSavedAssessment() || { answers, current, result: lastResult, lastView };
    if (saved.result){ lastResult = saved.result; showResult(saved.result); return; }
    await ensureSchema();
    answers    = normalizeAnswers(saved.answers, schema.items.length);
    current    = clamp(Number.isInteger(saved.current) ? saved.current : getDefaultQuestionIndex(answers), 0, schema.items.length - 1);
    lastResult = null;
    lastView   = 'quiz';
    saveAssessmentState();
    renderQuestion();
    show(viewQuiz);
  });
}

/** Busca o schema de itens da API, caso ainda não tenha sido carregado. */
async function ensureSchema(){
  if (schema) return;
  const res = await fetch('/api/schema');
  if (!res.ok) throw new Error('Falha ao obter /api/schema');
  schema = await res.json();
}

function updateQuizProgress(){
  if (!schema || !progress) return;

  const totalQuestions = schema.items.length;
  if (!totalQuestions){
    progress.textContent = 'Pergunta 0 de 0';
    if (progressPercent) progressPercent.textContent = '0%';
    if (progressFill)    progressFill.style.width = '0%';
    if (progressBar){
      progressBar.setAttribute('aria-valuenow', '0');
      progressBar.setAttribute('aria-valuetext', 'Pergunta 0 de 0');
    }
    return;
  }

  const currentQuestion = clamp(current + 1, 1, totalQuestions);
  const percent         = Math.round((currentQuestion / totalQuestions) * 100);

  progress.textContent = `Pergunta ${currentQuestion} de ${totalQuestions}`;
  if (progressPercent) progressPercent.textContent = `${percent}%`;
  if (progressFill)    progressFill.style.width = `${percent}%`;
  if (progressBar){
    progressBar.setAttribute('aria-valuenow', String(percent));
    progressBar.setAttribute('aria-valuetext', `Pergunta ${currentQuestion} de ${totalQuestions}`);
  }
}

function renderQuestion(){
  const it = schema.items[current];
  updateQuizProgress();
  qText.textContent  = it.text || it.name;
  qOptions.innerHTML = '';
  for (let k = 0; k < it.options.length; k++){
    const b = document.createElement('button');
    b.className   = 'option-btn';
    b.type        = 'button';
    b.textContent = (it.options && it.options[k]) || String(k);
    b.addEventListener('click', () => {
      answers[current] = k;
      lastResult       = null;
      lastView         = 'quiz';
      saveAssessmentState();
      [...qOptions.children].forEach(x => x.classList.remove('selected'));
      b.classList.add('selected');
      btnNext.disabled = false;
    });
    if (answers[current] === k) b.classList.add('selected');
    qOptions.appendChild(b);
  }
  btnPrev.disabled = current === 0;
  btnNext.disabled = false;
}


// ─── Resultado individual ─────────────────────────────────────────────────────

/** Anima um número de `from` até `to` em `duration` ms usando easing cúbico. */
function countUp(el, from, to, duration, formatter) {
  const start = performance.now();
  const diff  = to - from;
  function tick(now) {
    const elapsed = Math.min(now - start, duration);
    const t       = elapsed / duration;
    const eased   = 1 - Math.pow(1 - t, 3);
    el.textContent = formatter(from + diff * eased);
    if (elapsed < duration) requestAnimationFrame(tick);
    else el.textContent = formatter(to);
  }
  requestAnimationFrame(tick);
}

const CAT_CLASSES = ['cat-muito-ruim','cat-ruim','cat-boa','cat-muito-boa','cat-excelente'];

function animateLiquidFill(percent, category){
  liquidFill.classList.remove('is-filling', ...CAT_CLASSES);
  liquidFill.style.transition = 'none';
  liquidFill.style.width      = '0%';
  const catClass = 'cat-' + (category || '').replace('.', '-').replace(' ', '-');
  if (CAT_CLASSES.includes(catClass)) liquidFill.classList.add(catClass);
  void liquidFill.offsetWidth; // força reflow para reiniciar a animação CSS
  liquidFill.style.transition = '';
  setTimeout(() => {
    liquidFill.classList.add('is-filling');
    liquidFill.style.width = `${percent}%`;
  }, 60);
}

function showResult(r, isNew = false){
  if (isNew) saveToHistory(r);
  const pillsEl = document.querySelector('.result-pills');
  if (pillsEl) pillsEl.classList.toggle('show-researcher', !!currentUser);
  lastResult = r;
  lastView   = 'result';

  valF1.textContent     = r.F1.toFixed(4);
  valSE.textContent     = r.SE_F1.toFixed(4);
  valF1novo.textContent = r.F1novo.toFixed(4);
  gradeEl.textContent   = r["escore.cat.novo"][0].toUpperCase() + r["escore.cat.novo"].slice(1);

  const cat = r["escore.cat.novo"];
  if      (cat === 'muito ruim') textEl.textContent = 'Sua dieta está distante do recomendado. Tente incluir mais alimentos in natura.';
  else if (cat === 'ruim')       textEl.textContent = 'Há espaço para melhorias. Aumente frutas, legumes e feijões.';
  else if (cat === 'boa')        textEl.textContent = 'Bom caminho! Continue reduzindo ultraprocessados.';
  else if (cat === 'muito boa')  textEl.textContent = 'Excelente adesão. Mantenha variedade e regularidade.';
  else                           textEl.textContent = 'Excelente! Muito alinhada ao guia.';

  show(viewResult);

  // Barra de preenchimento: escala de 150 a 375
  const f       = Math.max(150, Math.min(375, r.F1novo));
  const percent = ((f - 150) / (375 - 150)) * 100;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reducedMotion) {
    resultPercent.textContent = `${r.F1novo.toFixed(1)} pontos`;
  } else {
    const fromVal = Math.max(150, r.F1novo - 40);
    countUp(resultPercent, fromVal, r.F1novo, 900, v => `${v.toFixed(1)} pontos`);
  }
  animateLiquidFill(percent, r["escore.cat.novo"]);
  saveAssessmentState();
}


// ─── Upload de CSV ────────────────────────────────────────────────────────────

function applyFile(file){
  if (!file) return;
  uploadLabel.textContent = file.name;
  uploadZone.classList.add('has-file');
  uploadZone.classList.remove('drag-over');
  btnResearcherSubmit.disabled = false;
}

researcherCsvFile.addEventListener('change', () => {
  const file = researcherCsvFile.files[0];
  if (file){
    applyFile(file);
  } else {
    uploadLabel.textContent = 'Arraste o CSV aqui ou clique para selecionar';
    uploadZone.classList.remove('has-file');
    btnResearcherSubmit.disabled = true;
  }
});

uploadZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', (e) => {
  if (!uploadZone.contains(e.relatedTarget)) uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.name.toLowerCase().endsWith('.csv')){
    const dt = new DataTransfer();
    dt.items.add(file);
    researcherCsvFile.files = dt.files;
    applyFile(file);
  } else if (file) {
    researcherStatus.innerHTML = '<div class="status-msg status-error">Apenas arquivos .csv são aceitos.</div>';
  }
});


// ─── Dashboard do pesquisador ─────────────────────────────────────────────────

/** Formata número com `dec` casas decimais; retorna '—' se nulo. */
function fmtN(v, dec=1){ return v !== null && v !== undefined ? (+v).toFixed(dec) : '—'; }

function renderStats(stats){
  dashStats.innerHTML = [
    {label:'Participantes',   value: stats.valid ?? stats.n ?? '—', sub: `de ${stats.total ?? '—'} linhas`},
    {label:'Média F1novo',    value: fmtN(stats.mean), sub: `DP ${fmtN(stats.std ?? stats.sd)}`},
    {label:'Min / Máx',       value: `${fmtN(stats.min, 0)} / ${fmtN(stats.max, 0)}`, sub: ''},
    {label:'Mediana',         value: fmtN(stats.median), sub: ''},
    {label:'Incompletos',     value: stats.incomplete ?? '—', sub: 'linhas com dados ausentes'},
    {label:'Categoria modal', value: CAT_LABELS[stats.top_cat] ?? stats.top_cat ?? '—', sub: ''},
  ].map(s => `<div class="dstat"><div class="dstat-label">${s.label}</div><div class="dstat-value">${s.value}</div><div class="dstat-sub">${s.sub}</div></div>`).join('');
}

function renderDonut(catDist){
  const cats  = Object.keys(catDist);
  const vals  = cats.map(k => catDist[k]);
  const total = vals.reduce((a,b) => a+b, 0) || 1;
  const cx = 100, cy = 100, r = 72, stroke = 34;
  const circ = 2 * Math.PI * r;
  let offset = 0;

  const slices = cats.map((cat, i) => {
    const pct    = vals[i] / total;
    const dash   = pct * circ;
    const gap    = circ - dash;
    const rotate = offset * 360 - 90;
    offset += pct;
    return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none"
      stroke="${CAT_COLORS[cat] || '#aaa'}" stroke-width="${stroke}"
      stroke-dasharray="${dash.toFixed(2)} ${gap.toFixed(2)}"
      transform="rotate(${rotate.toFixed(2)} ${cx} ${cy})"
      opacity="${vals[i] ? 1 : 0}"/>`;
  });

  dashDonutSvg.innerHTML = slices.join('') +
    `<text x="${cx}" y="${cy-4}" text-anchor="middle" font-size="22" font-weight="700" fill="#19382c">${total}</text>` +
    `<text x="${cx}" y="${cy+16}" text-anchor="middle" font-size="11" fill="#68756f">total</text>`;

  dashDonutLegend.innerHTML = cats.map((cat, i) =>
    `<div class="dleg-item">
       <div class="dleg-dot" style="background:${CAT_COLORS[cat] || '#aaa'}"></div>
       <span class="dleg-label">${CAT_LABELS[cat] || cat}</span>
       <span class="dleg-val">${vals[i]}</span>
     </div>`
  ).join('');
}

function renderHistogram(histData){
  const counts = histData.map(b => b.count);
  const bins   = histData.map(b => b.lo);
  bins.push(histData[histData.length - 1].hi);

  const W = 600, H = 220, padL = 38, padR = 14, padT = 14, padB = 38;
  const maxCount = Math.max(...counts, 1);
  const bW       = (W - padL - padR) / counts.length;
  const scaleY   = v => padT + (H - padT - padB) * (1 - v / maxCount);

  const bars = counts.map((c, i) => {
    const x = padL + i * bW + 1;
    const y = scaleY(c);
    const h = H - padB - y;
    return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${(bW-2).toFixed(1)}" height="${Math.max(h,0).toFixed(1)}" fill="#214f3d" opacity=".78" rx="2"/>
      ${c ? `<text x="${(x + bW/2 - 0.5).toFixed(1)}" y="${(y-4).toFixed(1)}" text-anchor="middle" font-size="9" fill="#19382c">${c}</text>` : ''}`;
  });

  // Rótulos nas bordas dos bins (não no centro das barras)
  const xLabels = bins.map((b, i) =>
    i % 2 === 0 ? `<text x="${(padL + i * bW).toFixed(1)}" y="${H - padB + 14}" text-anchor="middle" font-size="9" fill="#68756f">${b}</text>` : ''
  ).join('');

  const yLines = [0, 0.25, 0.5, 0.75, 1].map(f => {
    const y = scaleY(f * maxCount);
    const v = Math.round(f * maxCount);
    return `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="#e4dfd2" stroke-width="1"/>
      <text x="${padL - 4}" y="${(y + 3).toFixed(1)}" text-anchor="end" font-size="9" fill="#68756f">${v}</text>`;
  }).join('');

  dashHistSvg.innerHTML = `${yLines}${bars.join('')}${xLabels}`;
}

function renderItemBars(itemMeans){
  const n    = itemMeans.length;
  const barH = 18, gap = 6, padL = 52, padR = 60, padT = 10, padB = 10;
  const W    = 780;
  const H    = padT + n * (barH + gap) + padB;
  const maxW = W - padL - padR;

  const rows = itemMeans.map((item, i) => {
    const bw = (item.pct / 100) * maxW;
    const y  = padT + i * (barH + gap);
    return `<text x="${padL - 6}" y="${y + barH/2 + 4}" text-anchor="end" font-size="10" fill="#68756f">${item.label}</text>
      <rect x="${padL}" y="${y}" width="${maxW}" height="${barH}" fill="#e4dfd2" rx="3"/>
      <rect x="${padL}" y="${y}" width="${bw.toFixed(1)}" height="${barH}" fill="#214f3d" rx="3"/>
      <text x="${(padL + bw + 5).toFixed(1)}" y="${y + barH/2 + 4}" font-size="10" fill="#19382c">${item.pct.toFixed(1)}%</text>`;
  }).join('');

  dashItemsSvg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  dashItemsSvg.setAttribute('width', W);
  dashItemsSvg.setAttribute('height', H);
  dashItemsSvg.innerHTML = rows;
}

function renderResultsTable(results){
  dashResultsCount.textContent = `${results.length} participante${results.length !== 1 ? 's' : ''}`;
  dashResultsTbody.innerHTML = results.map((r, i) => {
    const cls = CAT_BADGE_CLASS[r.cat] || '';
    return `<tr>
      <td>${i + 1}</td>
      <td>${r.ID ?? '—'}</td>
      <td><strong>${r.F1novo !== null ? (+r.F1novo).toFixed(1) : '—'}</strong></td>
      <td><span class="cat-badge ${cls}">${CAT_LABELS[r.cat] || r.cat || '—'}</span></td>
      <td>${r.F1 !== null ? (+r.F1).toFixed(3) : '—'}</td>
      <td>${r.SE_F1 !== null ? (+r.SE_F1).toFixed(3) : '—'}</td>
    </tr>`;
  }).join('');
}

function renderErrors(errors){
  if (!errors || errors.length === 0){ dashErrorsPanel.classList.add('hidden'); return; }
  dashErrorsPanel.classList.remove('hidden');
  dashErrorsCount.textContent = errors.length;
  dashErrorsTbody.innerHTML = errors.map(e =>
    `<tr><td>${e.row}</td><td>${e.id ?? '—'}</td><td>${e.type}</td><td>${e.detail}</td></tr>`
  ).join('');
}

/** Preenche todos os painéis do dashboard com os dados retornados pela API. */
function renderDashboard(data, filename){
  renderStats(data.stats);
  renderDonut(data.category_dist);
  renderHistogram(data.histogram);
  renderItemBars(data.item_means);
  renderResultsTable(data.results);
  renderErrors(data.errors);
  _lastCsvB64 = data.csv_b64 || null;
  dashFilename.textContent = filename || '';
  uploadPanel.classList.add('hidden');
  analysisDashboard.classList.remove('hidden');
}

btnNewAnalysis.addEventListener('click', () => {
  analysisDashboard.classList.add('hidden');
  uploadPanel.classList.remove('hidden');
  researcherStatus.innerHTML = '';
  researcherCsvFile.value    = '';
  uploadLabel.textContent    = 'Arraste o CSV aqui ou clique para selecionar';
  uploadZone.classList.remove('has-file');
  btnResearcherSubmit.disabled = true;
});

btnDownloadResults.addEventListener('click', () => {
  if (!_lastCsvB64) return;
  const bytes = atob(_lastCsvB64);
  const arr   = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
  const blob = new Blob([arr], { type: 'text/csv' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = 'resultados-esquada.csv'; a.click();
  URL.revokeObjectURL(url);
});

researcherCsvForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = researcherCsvFile.files[0];
  if (!file) return;

  btnResearcherSubmit.disabled    = true;
  btnResearcherSubmit.textContent = 'Analisando…';
  researcherStatus.innerHTML      = '<div class="status-msg status-loading">Processando o arquivo…</div>';

  const fd = new FormData();
  fd.append('file', file);

  try {
    const res = await fetch('/api/analyze_csv', { method: 'POST', body: fd, credentials: 'include' });
    if (res.status === 401){
      researcherStatus.innerHTML = '<div class="status-msg status-error">Sessão expirada. Faça login novamente.</div>';
      currentUser = null; updateUserBar(); openAuthModal('login');
      return;
    }
    if (!res.ok){
      const err = await res.json().catch(() => ({}));
      researcherStatus.innerHTML = `<div class="status-msg status-error">Erro: ${err.error || res.statusText}</div>`;
      return;
    }
    const data = await res.json();
    researcherStatus.innerHTML = '';
    renderDashboard(data, file.name);
  } catch (_err) {
    researcherStatus.innerHTML = '<div class="status-msg status-error">Erro de conexão. Verifique se o servidor está rodando.</div>';
  } finally {
    btnResearcherSubmit.disabled    = false;
    btnResearcherSubmit.textContent = 'Analisar dados';
  }
});


// ─── Inicialização ────────────────────────────────────────────────────────────

/** Restaura o estado salvo ao carregar a página. */
async function restoreAssessment(){
  await checkAuth();
  updateStartLabels();
  const saved = loadSavedAssessment();
  updateHomeScoreCard(saved);
  if (!saved) return;

  await ensureSchema();
  answers    = normalizeAnswers(saved.answers, schema.items.length);
  current    = clamp(Number.isInteger(saved.current) ? saved.current : getDefaultQuestionIndex(answers), 0, schema.items.length - 1);
  lastResult = saved.result || null;
  lastView   = saved.lastView || 'home';

  if (lastView === 'result' && lastResult){ showResult(lastResult); return; }
  if (lastView === 'quiz' && answers.some(value => value != null)){ renderQuestion(); show(viewQuiz); return; }

  show(viewHome);
  updateStartLabels();
  updateHomeScoreCard(saved);
}

restoreAssessment();


// ─── Estado ativo do nav (IntersectionObserver) ───────────────────────────────

// Destaca o botão de nav correspondente à seção visível na home
const _navBtns = {};
document.querySelectorAll('[data-nav-section]').forEach(btn => {
  _navBtns[btn.dataset.navSection] = btn;
});

const _navObserver = new IntersectionObserver((entries) => {
  if (!viewHome.classList.contains('hidden')) {
    entries.forEach(e => {
      if (e.isIntersecting) {
        Object.values(_navBtns).forEach(b => b.classList.remove('nav-active'));
        const btn = _navBtns[e.target.id];
        if (btn) btn.classList.add('nav-active');
      }
    });
  }
}, { threshold: 0.35, rootMargin: '-80px 0px 0px 0px' });

['home-hero', 'home-actions', 'home-how'].forEach(id => {
  const el = document.getElementById(id);
  if (el) _navObserver.observe(el);
});


// ─── Toggle de visibilidade de senha ─────────────────────────────────────────

document.querySelectorAll('.pw-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const input   = document.getElementById(btn.dataset.target);
    if (!input) return;
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';
    btn.setAttribute('aria-label', isHidden ? 'Ocultar senha' : 'Mostrar senha');
    btn.querySelector('.eye-show').style.display = isHidden ? 'none' : '';
    btn.querySelector('.eye-hide').style.display = isHidden ? '' : 'none';
  });
});


// ─── Requisitos de senha em tempo real ────────────────────────────────────────

(function setupPwReqs() {
  const pwInput = document.getElementById('register-password');
  const pw2Input = document.getElementById('register-password2');
  const reqLen = document.getElementById('req-len');
  const reqNum = document.getElementById('req-num');
  const reqSym = document.getElementById('req-sym');
  if (!pwInput || !reqLen) return;

  function check(pw) {
    const okLen = pw.length >= 8;
    const okNum = /\d/.test(pw);
    const okSym = /[^a-zA-Z0-9]/.test(pw);
    reqLen.className = 'req-item ' + (pw.length === 0 ? '' : okLen ? 'ok' : 'fail');
    reqNum.className = 'req-item ' + (pw.length === 0 ? '' : okNum ? 'ok' : 'fail');
    reqSym.className = 'req-item ' + (pw.length === 0 ? '' : okSym ? 'ok' : 'fail');
  }

  pwInput.addEventListener('input', () => check(pwInput.value));

  // Confirm password — marca vermelho se diferente (apenas quando tem conteúdo)
  if (pw2Input) {
    pw2Input.addEventListener('input', () => {
      if (!pw2Input.value) { pw2Input.removeAttribute('data-match'); return; }
      pw2Input.dataset.match = pw2Input.value === pwInput.value ? 'ok' : 'fail';
    });
  }
})();


// ─── Autocomplete de instituição ──────────────────────────────────────────────

const UNIVERSITIES = [
  // Federais — sigla, nome completo
  ['UFPI',   'Universidade Federal do Piauí'],
  ['UFPB',   'Universidade Federal da Paraíba'],
  ['UFPE',   'Universidade Federal de Pernambuco'],
  ['UFPA',   'Universidade Federal do Pará'],
  ['UFPR',   'Universidade Federal do Paraná'],
  ['UFPEL',  'Universidade Federal de Pelotas'],
  ['UFP',    'Universidade Federal do Piauí'],
  ['UFRJ',   'Universidade Federal do Rio de Janeiro'],
  ['UFMG',   'Universidade Federal de Minas Gerais'],
  ['UFRGS',  'Universidade Federal do Rio Grande do Sul'],
  ['UFSC',   'Universidade Federal de Santa Catarina'],
  ['UFSM',   'Universidade Federal de Santa Maria'],
  ['UFBA',   'Universidade Federal da Bahia'],
  ['UFCE',   'Universidade Federal do Ceará'],
  ['UFC',    'Universidade Federal do Ceará'],
  ['UFRN',   'Universidade Federal do Rio Grande do Norte'],
  ['UFAL',   'Universidade Federal de Alagoas'],
  ['UFSE',   'Universidade Federal de Sergipe'],
  ['UFS',    'Universidade Federal de Sergipe'],
  ['UFMA',   'Universidade Federal do Maranhão'],
  ['UFAM',   'Universidade Federal do Amazonas'],
  ['UFAC',   'Universidade Federal do Acre'],
  ['UFRR',   'Universidade Federal de Roraima'],
  ['UFAP',   'Universidade Federal do Amapá'],
  ['UFMT',   'Universidade Federal de Mato Grosso'],
  ['UFMS',   'Universidade Federal de Mato Grosso do Sul'],
  ['UFG',    'Universidade Federal de Goiás'],
  ['UFTO',   'Universidade Federal do Tocantins'],
  ['UFT',    'Universidade Federal do Tocantins'],
  ['UFRO',   'Universidade Federal de Rondônia'],
  ['UNIR',   'Universidade Federal de Rondônia'],
  ['UFES',   'Universidade Federal do Espírito Santo'],
  ['UFJF',   'Universidade Federal de Juiz de Fora'],
  ['UFLA',   'Universidade Federal de Lavras'],
  ['UFOP',   'Universidade Federal de Ouro Preto'],
  ['UFSJ',   'Universidade Federal de São João del-Rei'],
  ['UFTM',   'Universidade Federal do Triângulo Mineiro'],
  ['UFU',    'Universidade Federal de Uberlândia'],
  ['UFV',    'Universidade Federal de Viçosa'],
  ['UFVJM',  'Universidade Federal dos Vales do Jequitinhonha e Mucuri'],
  ['UFERSA', 'Universidade Federal Rural do Semi-Árido'],
  ['UFRRJ',  'Universidade Federal Rural do Rio de Janeiro'],
  ['UFRPE',  'Universidade Federal Rural de Pernambuco'],
  ['UFRA',   'Universidade Federal Rural da Amazônia'],
  ['UNIFAP', 'Universidade Federal do Amapá'],
  ['UNIFAL', 'Universidade Federal de Alfenas'],
  ['UNIFEI', 'Universidade Federal de Itajubá'],
  ['UNIFESP','Universidade Federal de São Paulo'],
  ['UNIRIO', 'Universidade Federal do Estado do Rio de Janeiro'],
  ['UFOB',   'Universidade Federal do Oeste da Bahia'],
  ['UFOPA',  'Universidade Federal do Oeste do Pará'],
  ['UFSB',   'Universidade Federal do Sul da Bahia'],
  ['UFCA',   'Universidade Federal do Cariri'],
  ['UFCAT',  'Universidade Federal de Catalão'],
  ['UFGD',   'Universidade Federal da Grande Dourados'],
  ['UFCG',   'Universidade Federal de Campina Grande'],
  ['UFERSA', 'Universidade Federal Rural do Semi-Árido'],
  ['UNIVASF','Universidade Federal do Vale do São Francisco'],
  ['UFCSPA', 'Universidade Federal de Ciências da Saúde de Porto Alegre'],
  ['FURG',   'Universidade Federal do Rio Grande'],
  ['UNIPAMPA','Universidade Federal do Pampa'],
  ['UFFS',   'Universidade Federal da Fronteira Sul'],
  ['UTFPR',  'Universidade Tecnológica Federal do Paraná'],
  // IFs — Instituto Federal
  ['IFPI',   'Instituto Federal do Piauí'],
  ['IFMA',   'Instituto Federal do Maranhão'],
  ['IFCE',   'Instituto Federal do Ceará'],
  ['IFRN',   'Instituto Federal do Rio Grande do Norte'],
  ['IFPB',   'Instituto Federal da Paraíba'],
  ['IFPE',   'Instituto Federal de Pernambuco'],
  ['IFAL',   'Instituto Federal de Alagoas'],
  ['IFSE',   'Instituto Federal de Sergipe'],
  ['IFBA',   'Instituto Federal da Bahia'],
  ['IFES',   'Instituto Federal do Espírito Santo'],
  ['IFRJ',   'Instituto Federal do Rio de Janeiro'],
  ['IFF',    'Instituto Federal Fluminense'],
  ['IFMG',   'Instituto Federal de Minas Gerais'],
  ['IFNMG',  'Instituto Federal do Norte de Minas Gerais'],
  ['IFTM',   'Instituto Federal do Triângulo Mineiro'],
  ['IFSUDESTEMG','Instituto Federal do Sudeste de Minas Gerais'],
  ['IFSUL',  'Instituto Federal Sul-rio-grandense'],
  ['IFRS',   'Instituto Federal do Rio Grande do Sul'],
  ['IFSul',  'Instituto Federal Sul-rio-grandense'],
  ['IFSC',   'Instituto Federal de Santa Catarina'],
  ['IFC',    'Instituto Federal Catarinense'],
  ['IFPR',   'Instituto Federal do Paraná'],
  ['IFSP',   'Instituto Federal de São Paulo'],
  ['IFMS',   'Instituto Federal de Mato Grosso do Sul'],
  ['IFMT',   'Instituto Federal de Mato Grosso'],
  ['IFGO',   'Instituto Federal de Goiás'],
  ['IFTO',   'Instituto Federal do Tocantins'],
  ['IFRO',   'Instituto Federal de Rondônia'],
  ['IFAM',   'Instituto Federal do Amazonas'],
  ['IFAC',   'Instituto Federal do Acre'],
  ['IFRR',   'Instituto Federal de Roraima'],
  ['IFAP',   'Instituto Federal do Amapá'],
  ['IFPA',   'Instituto Federal do Pará'],
  // Estaduais & outras
  ['USP',    'Universidade de São Paulo'],
  ['UNICAMP','Universidade Estadual de Campinas'],
  ['UNESP',  'Universidade Estadual Paulista'],
  ['UFRB',   'Universidade Federal do Recôncavo da Bahia'],
  ['UECE',   'Universidade Estadual do Ceará'],
  ['UERN',   'Universidade do Estado do Rio Grande do Norte'],
  ['UESPI',  'Universidade Estadual do Piauí'],
  ['UEMA',   'Universidade Estadual do Maranhão'],
  ['UEPA',   'Universidade do Estado do Pará'],
  ['UEA',    'Universidade do Estado do Amazonas'],
  ['UERJ',   'Universidade do Estado do Rio de Janeiro'],
  ['UDESC',  'Universidade do Estado de Santa Catarina'],
  ['UESC',   'Universidade Estadual de Santa Cruz'],
  ['UEFS',   'Universidade Estadual de Feira de Santana'],
  ['UESB',   'Universidade Estadual do Sudoeste da Bahia'],
  ['UNEB',   'Universidade do Estado da Bahia'],
  ['UPE',    'Universidade de Pernambuco'],
  ['UEPB',   'Universidade Estadual da Paraíba'],
  ['URCA',   'Universidade Regional do Cariri'],
  ['UVA',    'Universidade Estadual Vale do Acaraú'],
  ['UFNT',   'Universidade Federal do Norte do Tocantins'],
  ['UnB',    'Universidade de Brasília'],
  ['UNB',    'Universidade de Brasília'],
  ['UFABC',  'Universidade Federal do ABC'],
  // Privadas relevantes
  ['PUC',    'Pontifícia Universidade Católica'],
  ['PUCSP',  'PUC-SP — Pontifícia Universidade Católica de São Paulo'],
  ['PUCRS',  'PUC-RS — Pontifícia Universidade Católica do Rio Grande do Sul'],
  ['PUCMG',  'PUC-MG — Pontifícia Universidade Católica de Minas Gerais'],
  ['PUCRJ',  'PUC-Rio — Pontifícia Universidade Católica do Rio de Janeiro'],
  ['FGV',    'Fundação Getulio Vargas'],
  ['INSPER', 'Insper — Instituto de Ensino e Pesquisa'],
  ['IBMEC',  'Ibmec'],
  ['MACKENZIE','Universidade Presbiteriana Mackenzie'],
  ['UNINOVE','Universidade Nove de Julho'],
  ['UNIP',   'Universidade Paulista'],
  ['ANHANGUERA','Universidade Anhanguera'],
  ['ESTÁCIO','Estácio de Sá'],
  ['UNICEUB','Centro Universitário de Brasília'],
];

// Normaliza texto: remove acentos e deixa em minúsculas para comparação
function _normalizeInst(str) {
  return str.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

function searchUniversities(query) {
  if (!query || query.length < 2) return [];
  const q = _normalizeInst(query);
  const seen = new Set();
  const starts = [], contains = [];

  UNIVERSITIES.forEach(([abbr, name]) => {
    const abbrN = _normalizeInst(abbr);
    const nameN = _normalizeInst(name);
    const key = abbr + '|' + name;
    if (seen.has(key)) return;

    if (abbrN.startsWith(q) || nameN.startsWith(q)) {
      seen.add(key); starts.push({ abbr, name });
    } else if (abbrN.includes(q) || nameN.includes(q)) {
      seen.add(key); contains.push({ abbr, name });
    }
  });

  return [...starts, ...contains].slice(0, 8);
}

(function setupInstAutocomplete() {
  const input = document.getElementById('register-institution');
  const list  = document.getElementById('inst-suggestions');
  if (!input || !list) return;

  let activeIdx = -1;
  let items = [];

  function renderList(results) {
    list.innerHTML = '';
    items = results;
    activeIdx = -1;

    if (!results.length) { list.classList.add('hidden'); return; }

    results.forEach(({ abbr, name }, i) => {
      const li = document.createElement('li');
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', 'false');
      li.dataset.idx = i;
      li.innerHTML = `<span class="sugg-abbr">${abbr}</span><span class="sugg-name">${name}</span>`;
      li.addEventListener('mousedown', (e) => {
        e.preventDefault(); // evita blur antes do click
        selectItem(i);
      });
      list.appendChild(li);
    });
    list.classList.remove('hidden');
  }

  function selectItem(idx) {
    if (idx < 0 || idx >= items.length) return;
    input.value = items[idx].name;
    list.classList.add('hidden');
    activeIdx = -1;
  }

  function setActive(idx) {
    const lis = list.querySelectorAll('li');
    lis.forEach(li => { li.classList.remove('active'); li.setAttribute('aria-selected', 'false'); });
    activeIdx = idx;
    if (idx >= 0 && idx < lis.length) {
      lis[idx].classList.add('active');
      lis[idx].setAttribute('aria-selected', 'true');
      lis[idx].scrollIntoView({ block: 'nearest' });
    }
  }

  input.addEventListener('input', () => {
    renderList(searchUniversities(input.value));
  });

  input.addEventListener('keydown', (e) => {
    if (list.classList.contains('hidden')) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive(Math.min(activeIdx + 1, items.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive(Math.max(activeIdx - 1, -1));
    } else if (e.key === 'Enter' && activeIdx >= 0) {
      e.preventDefault();
      selectItem(activeIdx);
    } else if (e.key === 'Escape') {
      list.classList.add('hidden');
    }
  });

  input.addEventListener('blur', () => {
    // pequeno delay para o mousedown do item processar antes do blur
    setTimeout(() => list.classList.add('hidden'), 120);
  });

  input.addEventListener('focus', () => {
    if (input.value.length >= 2) renderList(searchUniversities(input.value));
  });
})();


// ─── Citação acadêmica: copiar para a área de transferência ──────────────────

(function setupCopyCitation() {
  const btn = document.getElementById('btn-copy-citation');
  const txt = document.getElementById('citation-text');
  if (!btn || !txt) return;

  btn.addEventListener('click', async () => {
    const label = btn.querySelector('span');
    const original = label ? label.textContent : '';
    try {
      await navigator.clipboard.writeText(txt.textContent.trim());
      if (label) label.textContent = 'Copiado!';
      btn.classList.add('copied');
    } catch (_) {
      // Fallback para navegadores sem Clipboard API
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(txt);
      sel.removeAllRanges();
      sel.addRange(range);
      if (label) label.textContent = 'Selecione e copie';
    }
    setTimeout(() => {
      if (label) label.textContent = original;
      btn.classList.remove('copied');
    }, 1800);
  });
})();
