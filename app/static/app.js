const form = document.querySelector('#form');
const loading = document.querySelector('#loading');
const result = document.querySelector('#result');
const error = document.querySelector('#error');
const submitButton = document.querySelector('#submitButton');

for (const [id, max] of [['resume', 12000], ['job', 8000]]) {
  const el = document.querySelector(`#${id}`);
  const out = document.querySelector(`#${id}Count`);
  el.addEventListener('input', () => { out.textContent = `${el.value.length} / ${max}`; });
}

const esc = value => String(value ?? '').replace(/[&<>'\"]/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
}[character]));
const list = items => `<ul>${items.map(item => `<li>${esc(item)}</li>`).join('')}</ul>`;

function friendlyError(status, detail, fields = []) {
  if (status === 429) return 'O serviço está recebendo muitas solicitações. Aguarde alguns segundos e tente novamente.';
  if (status === 503) return detail || 'A IA está temporariamente indisponível. Tente novamente em instantes.';
  if (status === 400) {
    const names = fields.map(field => field.field).filter(Boolean);
    return names.length
      ? `${detail || 'Dados inválidos.'} Revise: ${names.join(', ')}.`
      : detail || 'Revise os campos: há dados inválidos ou texto insuficiente.';
  }
  return detail || 'Não foi possível realizar a análise. Tente novamente.';
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  error.textContent = '';
  result.classList.add('hidden');
  loading.classList.remove('hidden');
  submitButton.disabled = true;
  submitButton.setAttribute('aria-busy', 'true');

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        candidate_name: document.querySelector('#name').value,
        resume: document.querySelector('#resume').value,
        job_description: document.querySelector('#job').value,
      }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(friendlyError(response.status, data.detail, data.errors));

    result.innerHTML = `<div class="score-row"><div class="score">${data.match_score}%</div><div><span class="badge">modo ${esc(data.mode)}</span><h2>Resultado da análise</h2><p>${esc(data.summary)}</p></div></div><div class="grid"><article class="result-card"><h3>Pontos fortes</h3>${list(data.strengths)}</article><article class="result-card"><h3>Competências encontradas</h3>${list(data.matching_skills.map(item => `${item.skill}: ${item.evidence}`))}</article><article class="result-card"><h3>Competências a desenvolver</h3>${list(data.missing_skills.map(item => `${item.skill} (${item.importance}): ${item.suggestion}`))}</article><article class="result-card"><h3>Melhorias no currículo</h3>${list(data.resume_improvements)}</article><article class="result-card"><h3>Dicas para entrevista</h3>${list(data.interview_tips)}</article><article class="result-card full"><h3>Carta de apresentação sugerida</h3><p>${esc(data.cover_letter)}</p></article></div><p><small>${esc(data.disclaimer)}</small></p>`;
    result.classList.remove('hidden');
    result.scrollIntoView({behavior: 'smooth'});
  } catch (requestError) {
    error.textContent = requestError instanceof TypeError
      ? 'Não foi possível conectar à aplicação. Verifique sua conexão e tente novamente.'
      : requestError.message;
    form.scrollIntoView({behavior: 'smooth'});
  } finally {
    loading.classList.add('hidden');
    submitButton.disabled = false;
    submitButton.removeAttribute('aria-busy');
  }
});
