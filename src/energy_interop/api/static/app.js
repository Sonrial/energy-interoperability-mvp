const fmt = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 1 });
const api = {
  summary: '/api/sample/kpis',
  measurements: '/api/sample/measurements',
};

function kw(value) { return `${fmt.format(value)} kW`; }
function kwh(value) { return `${fmt.format(value)} kWh`; }
function irradiance(value) { return `${fmt.format(value)} W/m²`; }
function shortTime(value) { return new Date(value).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }); }

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} al consultar ${url}`);
  return response.json();
}

function renderSummary(summary) {
  document.querySelector('#energy-net').textContent = kwh(summary.energy_kwh_net);
  document.querySelector('#energy-expected').textContent = kwh(summary.expected_energy_kwh);
  document.querySelector('#mean-residual').textContent = kw(summary.mean_residual_kw);
  document.querySelector('#record-count').textContent = fmt.format(summary.records);
  document.querySelector('#quality-count').textContent = Object.entries(summary.quality_flag_counts).map(([flag, count]) => `${flag}: ${count}`).join(' · ');
  document.querySelector('#period-range').textContent = `${summary.period_start_utc} → ${summary.period_end_utc}`;
}

function renderTable(items) {
  const tbody = document.querySelector('#measurements-body');
  tbody.innerHTML = items.map((row) => `
    <tr>
      <td>${row.timestamp_local}</td>
      <td>${row.timestamp_utc}</td>
      <td>${irradiance(row.ghi_w_m2)}</td>
      <td>${kw(row.actual_power_kw)}</td>
      <td>${kw(row.expected_power_kw)}</td>
      <td>${kw(row.residual_kw)}</td>
      <td class="${row.quality_flag === 'ok' ? 'flag-ok' : 'flag-warning'}">${row.quality_flag}</td>
    </tr>
  `).join('');
}

function renderChart(items) {
  const chart = document.querySelector('#chart');
  const maxValue = Math.max(...items.flatMap((row) => [row.ghi_w_m2, row.actual_power_kw, row.expected_power_kw]));
  chart.innerHTML = items.map((row) => {
    const ghiHeight = Math.max((row.ghi_w_m2 / maxValue) * 100, 1);
    const actualHeight = Math.max((row.actual_power_kw / maxValue) * 100, 1);
    const expectedHeight = Math.max((row.expected_power_kw / maxValue) * 100, 1);
    return `
      <div>
        <div class="bar-group" title="${row.timestamp_local}">
          <div class="bar ghi" style="height:${ghiHeight}%"></div>
          <div class="bar actual" style="height:${actualHeight}%"></div>
          <div class="bar expected" style="height:${expectedHeight}%"></div>
        </div>
        <div class="bar-label">${shortTime(row.timestamp_local)}</div>
      </div>
    `;
  }).join('');
}

async function loadDashboard() {
  const status = document.querySelector('#load-status');
  status.textContent = 'Cargando…';
  const [summary, measurements] = await Promise.all([fetchJson(api.summary), fetchJson(api.measurements)]);
  renderSummary(summary);
  renderTable(measurements.items);
  renderChart(measurements.items);
  status.textContent = `${measurements.items.length} registros cargados`;
}

document.querySelector('#refresh-button').addEventListener('click', loadDashboard);
loadDashboard().catch((error) => {
  document.querySelector('#load-status').textContent = error.message;
});
