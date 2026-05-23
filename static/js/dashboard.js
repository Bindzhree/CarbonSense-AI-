Chart.defaults.color = '#8ba99b';
Chart.defaults.borderColor = 'rgba(100,200,150,0.08)';

const COLORS  = ['rgba(34,197,94,0.8)','rgba(34,211,238,0.8)','rgba(245,158,11,0.8)',
                  'rgba(167,139,250,0.8)','rgba(248,113,113,0.8)','rgba(251,191,36,0.8)'];
const BORDERS = ['rgba(34,197,94,1)','rgba(34,211,238,1)','rgba(245,158,11,1)',
                  'rgba(167,139,250,1)','rgba(248,113,113,1)','rgba(251,191,36,1)'];

function baseOpts(horizontal=false) {
  return {
    responsive: true, maintainAspectRatio: true,
    indexAxis: horizontal ? 'y' : 'x',
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color:'rgba(100,200,150,0.06)' }, ticks: { font:{ family:'DM Sans', size:12 } } },
      y: { grid: { color:'rgba(100,200,150,0.06)' }, ticks: { font:{ family:'DM Sans', size:12 } } }
    }
  };
}

function barDataset(data, labels) {
  return {
    labels,
    datasets: [{
      data,
      backgroundColor: COLORS.slice(0, labels.length),
      borderColor:     BORDERS.slice(0, labels.length),
      borderWidth: 2, borderRadius: 8
    }]
  };
}

async function loadDashboard() {
  const stats = await fetch('/api/dataset-stats').then(r => r.json());

  // Stat cards
  animNum(document.getElementById('sc-total'),  stats.total);
  animNum(document.getElementById('sc-mean'),   stats.mean_co2);
  animNum(document.getElementById('sc-median'), stats.median_co2);

  // Diet chart
  new Chart(document.getElementById('dietChart'), {
    type: 'bar',
    data: barDataset(Object.values(stats.co2_by_diet), Object.keys(stats.co2_by_diet)),
    options: baseOpts()
  });

  // Transport chart
  const tLabels = { private:'🚗 Private', public:'🚌 Public', 'walk/bicycle':'🚲 Walk/Bike' };
  new Chart(document.getElementById('transportChart'), {
    type: 'bar',
    data: barDataset(
      Object.values(stats.co2_by_transport),
      Object.keys(stats.co2_by_transport).map(k => tLabels[k] || k)
    ),
    options: baseOpts()
  });

  // Distribution doughnut
  new Chart(document.getElementById('distChart'), {
    type: 'doughnut',
    data: {
      labels: Object.keys(stats.emission_dist),
      datasets: [{
        data: Object.values(stats.emission_dist),
        backgroundColor: ['rgba(34,197,94,0.7)','rgba(245,158,11,0.7)','rgba(248,113,113,0.7)'],
        borderColor:     ['rgba(34,197,94,1)','rgba(245,158,11,1)','rgba(248,113,113,1)'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true, cutout: '65%',
      plugins: { legend: { display:true, position:'bottom', labels:{ color:'#8ba99b', padding:16 } } }
    }
  });

  // Air travel chart
  const travelOrder = ['never','rarely','frequently','very frequently'];
  const travelVals  = travelOrder.map(k => stats.co2_by_travel[k] ?? 0);
  new Chart(document.getElementById('travelChart'), {
    type: 'bar',
    data: barDataset(travelVals, travelOrder.map(k => k.charAt(0).toUpperCase()+k.slice(1))),
    options: baseOpts()
  });

  // Heating chart
  new Chart(document.getElementById('heatingChart'), {
    type: 'bar',
    data: barDataset(Object.values(stats.co2_by_heating), Object.keys(stats.co2_by_heating)),
    options: baseOpts()
  });

  // Feature importance
  const fi = METRICS.feature_importance;
  const fiSorted = Object.entries(fi).sort((a,b) => b[1]-a[1]);
  new Chart(document.getElementById('featureChart'), {
    type: 'bar',
    data: {
      labels: fiSorted.map(([k]) => k.replace(/_/g,' ').split(' ').map(w => w.charAt(0).toUpperCase()+w.slice(1)).join(' ')),
      datasets: [{
        data: fiSorted.map(([,v]) => (v*100).toFixed(1)),
        backgroundColor: fiSorted.map((_,i) => COLORS[i % COLORS.length]),
        borderColor:     fiSorted.map((_,i) => BORDERS[i % BORDERS.length]),
        borderWidth: 2, borderRadius: 8
      }]
    },
    options: {
      ...baseOpts(true),
      scales: {
        x: { grid:{ color:'rgba(100,200,150,0.06)' }, ticks:{ callback: v => v+'%' } },
        y: { grid:{ color:'rgba(100,200,150,0.06)' } }
      }
    }
  });

  // Confusion matrix
  buildConfusionMatrix();

  // Model comparison
  new Chart(document.getElementById('modelChart'), {
    type: 'bar',
    data: {
      labels: ['RF Classifier\nAccuracy','DT Classifier\nAccuracy','RF Regressor R²×100','Linear Reg R²×100'],
      datasets: [{
        label: 'Score (%)',
        data: [
          METRICS.rf_classification.accuracy,
          METRICS.dt_classification.accuracy,
          (METRICS.rf_regression.r2 * 100).toFixed(1),
          (METRICS.linear_regression.r2 * 100).toFixed(1)
        ],
        backgroundColor: COLORS,
        borderColor:     BORDERS,
        borderWidth: 2, borderRadius: 10
      }]
    },
    options: {
      ...baseOpts(),
      scales: {
        y: { min:40, max:100, grid:{ color:'rgba(100,200,150,0.06)' }, ticks:{ callback: v => v+'%' } },
        x: { grid:{ color:'rgba(100,200,150,0.06)' } }
      }
    }
  });
}

function buildConfusionMatrix() {
  const cm      = METRICS.confusion_matrix;
  const classes = METRICS.class_names;
  const container = document.getElementById('confusionMatrix');

  const header = document.createElement('div');
  header.className = 'cm-header';
  header.innerHTML = '<span style="width:80px;font-size:12px;color:var(--text3)">Predicted→</span>' +
    classes.map(c => `<span class="cm-header-label">${c}</span>`).join('');
  container.appendChild(header);

  cm.forEach((row, i) => {
    const rowEl = document.createElement('div');
    rowEl.className = 'cm-row';
    rowEl.innerHTML = `<span class="cm-label">${classes[i]}</span>`;
    row.forEach((val, j) => {
      const cell = document.createElement('div');
      cell.className = 'cm-cell ' + (i === j ? 'cm-diag' : 'cm-off');
      cell.textContent = val;
      rowEl.appendChild(cell);
    });
    container.appendChild(rowEl);
  });
}

function animNum(el, target) {
  if (!el) return;
  const dur = 1200, start = performance.now();
  function step(now) {
    const t = Math.min((now - start) / dur, 1);
    const val = target * (1 - Math.pow(1-t, 3));
    el.textContent = Math.round(val).toLocaleString('en-IN');
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

loadDashboard();
