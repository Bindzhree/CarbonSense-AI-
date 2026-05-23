// ===== SELECT CARDS =====
function selectCard(el, fieldName) {
  const parent = el.closest('.select-cards');
  parent.querySelectorAll('.select-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById(fieldName).value = el.dataset.value;
}

// ===== RANGE SYNC =====
function syncRange(numId, rangeId, val, unit) {
  document.getElementById(numId).value = val;
}
function syncNum(numId, rangeId, val) {
  document.getElementById(rangeId).value = val;
}

// ===== FORM SUBMIT =====
document.getElementById('predictorForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  const hiddenFields = [
    'body_type','sex','diet','shower_freq','heating_source',
    'transport','social_activity','air_travel_freq',
    'waste_bag_size','energy_efficiency'
  ];
  for (const id of hiddenFields) {
    if (!document.getElementById(id).value) {
      const label = id.replace(/_/g,' ');
      alert(`Please select a value for: ${label}`);
      document.querySelector(`[onclick*="${id}"]`)?.closest('.form-card')
        ?.scrollIntoView({behavior:'smooth', block:'center'});
      return;
    }
  }

  const btn = document.getElementById('predictBtn');
  btn.disabled = true;
  btn.querySelector('.btn-text').classList.add('hidden');
  btn.querySelector('.btn-loader').classList.remove('hidden');

  const payload = {};
  hiddenFields.forEach(id => payload[id] = document.getElementById(id).value);
  ['grocery_bill','new_clothes','vehicle_km','waste_bag_count',
   'tv_pc_hours','internet_hours'].forEach(id => {
    payload[id] = document.getElementById(id).value;
  });

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) showResults(data);
    else alert('Prediction error: ' + data.error);
  } catch(err) {
    alert('Network error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.querySelector('.btn-text').classList.remove('hidden');
    btn.querySelector('.btn-loader').classList.add('hidden');
  }
});

// ===== SHOW RESULTS =====
function showResults(data) {
  const section = document.getElementById('results');
  section.classList.remove('hidden');
  section.scrollIntoView({ behavior:'smooth', block:'start' });

  // Animate CO2 number
  animateNumber(document.getElementById('co2Value'), 0, data.co2_prediction, 1500,
    v => Math.round(v).toLocaleString('en-IN'));

  // Ring arc
  const arc = document.getElementById('scoreArc');
  const maxCO2 = 8500;
  const pct = Math.min(data.co2_prediction / maxCO2, 1);
  const colors = {Low:'#22c55e', Medium:'#f59e0b', High:'#f87171'};
  setTimeout(() => {
    arc.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.34,1.56,0.64,1)';
    arc.style.strokeDashoffset = 534 * (1 - pct);
    arc.style.stroke = colors[data.emission_category] || '#22c55e';
  }, 100);

  // Badge
  const badge = document.getElementById('categoryBadge');
  const labels = {Low:'🌿 Low Emission', Medium:'⚡ Medium Emission', High:'🔥 High Emission'};
  badge.textContent = labels[data.emission_category] || data.emission_category;
  badge.className = 'category-badge ' + data.emission_category;

  // Percentile
  document.getElementById('percentileText').textContent =
    `Higher than ${data.percentile}% of people in the dataset`;

  // Probability bars
  setTimeout(() => {
    ['Low','Medium','High'].forEach(cat => {
      const val = data.probabilities[cat] ?? 0;
      const el  = document.getElementById('prob-' + cat);
      const bar = document.getElementById('pfill-' + cat);
      if (el)  el.textContent  = val + '%';
      if (bar) bar.style.width = val + '%';
    });
  }, 300);

  // Breakdown bars
  const bdEl  = document.getElementById('breakdownChart');
  bdEl.innerHTML = '';
  const total = Object.values(data.breakdown).reduce((a,b) => a+b, 0);
  const icons = {Transport:'🚗', Diet:'🥗', Heating:'🔥',
                 'Air Travel':'✈️', Clothing:'👕', Groceries:'🛒', Digital:'💻'};
  Object.entries(data.breakdown).forEach(([key, val]) => {
    const pct = Math.max(val / total * 100, 2);
    const item = document.createElement('div');
    item.className = 'bd-item';
    item.innerHTML = `
      <span class="bd-label">${icons[key]||''} ${key}</span>
      <div class="bd-track">
        <div class="bd-fill" style="width:0%" data-target="${pct.toFixed(1)}">${val.toLocaleString()} kg</div>
      </div>`;
    bdEl.appendChild(item);
  });
  setTimeout(() => {
    document.querySelectorAll('.bd-fill').forEach(el => {
      el.style.width = el.dataset.target + '%';
    });
  }, 200);

  // Recommendations
  document.getElementById('recsList').innerHTML =
    data.recommendations.map(r => `
      <div class="rec-item">
        <span class="rec-icon">${r.icon}</span>
        <div class="rec-content">
          <div class="rec-title">${r.title}</div>
          <div class="rec-desc">${r.desc}</div>
          <div class="rec-impact">${r.impact}</div>
        </div>
      </div>`).join('');
}

function animateNumber(el, from, to, duration, formatter) {
  const start = performance.now();
  function update(now) {
    const t = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = formatter(from + (to - from) * eased);
    if (t < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

function resetForm() {
  document.getElementById('results').classList.add('hidden');
  document.querySelectorAll('.select-card.selected').forEach(c => c.classList.remove('selected'));
  document.querySelectorAll('input[type=hidden]').forEach(i => i.value = '');
  window.scrollTo({top: document.getElementById('predictor').offsetTop - 80, behavior:'smooth'});
}
