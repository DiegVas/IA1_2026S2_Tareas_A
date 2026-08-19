// URL base del backend
const API_BASE_URL = window.location.origin.includes('http') 
  ? window.location.origin 
  : 'http://127.0.0.1:8000';

// Elementos del DOM
const searchForm = document.getElementById('search-form');
const itemInput = document.getElementById('item-input');
const clearBtn = document.getElementById('clear-btn');
const submitBtn = document.getElementById('submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnSpinner = submitBtn.querySelector('.btn-spinner');

const statusBar = document.getElementById('status-bar');
const statusFlag = document.getElementById('status-flag');
const statusText = document.getElementById('status-text');
const querySignatureCode = document.getElementById('query-signature-code');

const resultsView = document.getElementById('results-view');
const valTotalItems = document.getElementById('val-total-items');
const valUniqueItems = document.getElementById('val-unique-items');
const valMemberStatus = document.getElementById('val-member-status');

const countInverted = document.getElementById('count-inverted');
const countOrdered = document.getElementById('count-ordered');
const countUnique = document.getElementById('count-unique');

const streamInverted = document.getElementById('stream-inverted');
const streamOrdered = document.getElementById('stream-ordered');
const streamUnique = document.getElementById('stream-unique');

const inspectorToggle = document.getElementById('inspector-toggle');
const inspectorToggleBtn = document.getElementById('inspector-toggle-btn');
const inspectorContent = document.getElementById('inspector-content');
const jsonOutput = document.getElementById('json-output');

const presetPills = document.querySelectorAll('.preset-pill');

// Envio del formulario
searchForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const query = itemInput.value.trim();
  if (query) await ejecutarConsultaProlog(query);
});

// Botones de consulta rapida
presetPills.forEach(pill => {
  pill.addEventListener('click', () => {
    const item = pill.getAttribute('data-item');
    itemInput.value = item;
    ejecutarConsultaProlog(item);
  });
});

clearBtn.addEventListener('click', () => {
  itemInput.value = '';
  itemInput.focus();
});

// Toggle para mostrar/ocultar JSON
inspectorToggle.addEventListener('click', () => {
  const isHidden = inspectorContent.style.display === 'none';
  inspectorContent.style.display = isHidden ? 'block' : 'none';
  inspectorToggleBtn.textContent = isHidden ? 'Ocultar respuesta cruda' : 'Mostrar respuesta cruda';
});

// Peticion GET al backend
async function ejecutarConsultaProlog(itemName) {
  setLoading(true);
  try {
    const response = await fetch(`${API_BASE_URL}/api/inventario?item=${encodeURIComponent(itemName)}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    renderizarDatos(data);
  } catch (error) {
    mostrarError(error.message || 'Error de conexión.');
  } finally {
    setLoading(false);
  }
}

// Renderizado dinámico de resultados
function renderizarDatos(data) {
  const { item_buscado, encontrado, total_items, inventario_invertido, inventario_unico, inventario_ordenado, mensaje } = data;

  statusBar.style.display = 'flex';
  statusBar.className = `status-bar ${encontrado ? 'matched' : 'unmatched'}`;
  statusFlag.textContent = encontrado ? 'UNIFICADO: TRUE' : 'UNIFICADO: FALSE';
  statusText.textContent = mensaje;
  querySignatureCode.textContent = `?- procesar_inventario('${item_buscado}', ${total_items}, Inv, Unico, Ord).`;

  valTotalItems.textContent = total_items;
  valUniqueItems.textContent = inventario_unico.length;
  valMemberStatus.textContent = encontrado ? 'Verdadero' : 'Falso';
  valMemberStatus.style.color = encontrado ? 'var(--state-success-text)' : 'var(--state-error-text)';

  countInverted.textContent = `${inventario_invertido.length} ítems`;
  countOrdered.textContent = `${inventario_ordenado.length} ítems`;
  countUnique.textContent = `${inventario_unico.length} ítems`;

  renderStream(streamInverted, inventario_invertido, item_buscado);
  renderStream(streamOrdered, inventario_ordenado, item_buscado);
  renderStream(streamUnique, inventario_unico, item_buscado);

  jsonOutput.textContent = JSON.stringify(data, null, 2);
  resultsView.style.display = 'flex';
}

// Renderiza cada fila de la lista numerada
function renderStream(container, items, targetItem) {
  container.innerHTML = '';
  if (!items || items.length === 0) return;

  items.forEach((item, index) => {
    const isTarget = item.toLowerCase() === targetItem.toLowerCase();
    const li = document.createElement('li');
    li.className = `stream-item ${isTarget ? 'is-match' : ''}`;
    const num = String(index + 1).padStart(2, '0');

    li.innerHTML = `
      <div class="stream-item-main">
        <span class="stream-item-index">${num}</span>
        <span class="stream-item-name">${item}</span>
      </div>
      ${isTarget ? '<span class="match-tag">Coincidencia</span>' : ''}
    `;
    container.appendChild(li);
  });
}

function mostrarError(msg) {
  statusBar.style.display = 'flex';
  statusBar.className = 'status-bar unmatched';
  statusFlag.textContent = 'ERROR DE RED';
  statusText.textContent = msg;
  querySignatureCode.textContent = 'Fallo de conexión';
  resultsView.style.display = 'none';
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  btnText.style.display = isLoading ? 'none' : 'inline-block';
  btnSpinner.style.display = isLoading ? 'inline-block' : 'none';
}
