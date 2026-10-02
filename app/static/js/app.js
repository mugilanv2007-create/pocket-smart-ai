document.addEventListener('DOMContentLoaded', () => {
  bindPlannerForms();
  bindHistoryView();
  maybeHandleJewelryImageUpload();
});

function bindPlannerForms() {
  const forms = document.querySelectorAll('.planner-form');

  forms.forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const planner = form.dataset.planner;
      const resultPanel = document.getElementById('planner-result');
      const submitButton = form.querySelector('button[type="submit"]');

      if (!resultPanel) {
        return;
      }

      submitButton.disabled = true;
      resultPanel.innerHTML = '<p class="empty-state">Generating smart plan...</p>';

      try {
        const payload = Object.fromEntries(new FormData(form).entries());

        if (planner === 'jewelry') {
          const fileInput = document.getElementById('jewelry-image-upload');
          if (fileInput && fileInput.files && fileInput.files[0]) {
            const file = fileInput.files[0];
            const dataUrl = await readFileAsDataUrl(file);
            payload.outfit_image_url = dataUrl;
          }
        }

        Object.keys(payload).forEach((key) => {
          if (key === 'total_budget' || key === 'budget' || key === 'guests') {
            payload[key] = Number(payload[key]);
          }
        });

        const response = await fetch(`/api/generate-${planner}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || 'Unable to generate recommendations.');
        }

        resultPanel.innerHTML = renderPlannerResult(data);
      } catch (error) {
        resultPanel.innerHTML = `<div class="result-block"><div class="result-summary"><h3>Unable to generate plan</h3><p>${error.message || 'Something went wrong.'}</p></div></div>`;
      } finally {
        submitButton.disabled = false;
      }
    });
  });
}

function renderPlannerResult(data) {
  const allocations = (data.budget_allocation || [])
    .map((item) => `
      <div class="allocation-item">
        <div>
          <strong>${item.category}</strong>
          <div>${item.percentage}% of total</div>
        </div>
        <strong>₹${Number(item.amount).toLocaleString('en-IN')}</strong>
      </div>
    `)
    .join('');

  const recommendations = (data.recommendations || [])
    .map((item) => `
      <article class="recommendation-card">
        <div class="rec-head">
          <h4>${item.name}</h4>
          <span class="pill">${item.platform}</span>
        </div>
        <p>${item.reason}</p>
        <div class="rec-meta">
          <strong>₹${Number(item.estimated_price).toLocaleString('en-IN')}</strong>
          <span>${item.category}</span>
        </div>
        <a class="link-button" href="${item.link}" target="_blank" rel="noreferrer">Search ${item.platform}</a>
      </article>
    `)
    .join('');

  const tips = (data.tips || [])
    .map((tip) => `<li>${tip}</li>`)
    .join('');

  return `
    <div class="result-block">
      <div class="result-summary">
        <h3>AI summary</h3>
        <p>${data.summary || 'Smart recommendation plan created.'}</p>
      </div>

      <div>
        <h3>Budget allocation</h3>
        <div class="allocation-grid">${allocations || '<p class="empty-state">No allocation data available.</p>'}</div>
      </div>

      <div>
        <h3>Recommended options</h3>
        <div class="recommendation-grid">${recommendations || '<p class="empty-state">No recommendations available.</p>'}</div>
      </div>

      <div>
        <h3>Tips</h3>
        <ul class="tip-list">${tips || '<li>Keep a small reserve for contingencies.</li>'}</ul>
      </div>
    </div>
  `;
}

function bindHistoryView() {
  const container = document.getElementById('history-container');
  if (!container) {
    return;
  }

  fetch('/api/history-data')
    .then(async (response) => {
      if (!response.ok) {
        throw new Error('History is unavailable. Please log in again.');
      }
      const data = await response.json();
      const items = data.items || [];

      if (!items.length) {
        container.innerHTML = '<p class="empty-state">No recommendations yet. Generate a planner result to start your history.</p>';
        return;
      }

      container.innerHTML = items
        .map((item) => {
          const result = item.response_json || {};
          const summary = result.summary || 'Smart recommendation';
          const recommendations = Array.isArray(result.recommendations) ? result.recommendations.length : 0;
          return `
            <article class="history-item">
              <h3>${item.planner.toUpperCase()} plan</h3>
              <p>${summary}</p>
              <div class="history-meta">
                <span>Recommendations: ${recommendations}</span>
                <span>${new Date(item.created_at).toLocaleString()}</span>
              </div>
            </article>
          `;
        })
        .join('');
    })
    .catch((error) => {
      container.innerHTML = `<p class="empty-state">${error.message}</p>`;
    });
}

function maybeHandleJewelryImageUpload() {
  const uploadInput = document.getElementById('jewelry-image-upload');
  if (!uploadInput) {
    return;
  }

  uploadInput.addEventListener('change', async (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) {
      return;
    }
    const dataUrl = await readFileAsDataUrl(file);
    const urlField = document.querySelector('input[name="outfit_image_url"]');
    if (urlField) {
      urlField.value = dataUrl;
    }
  });
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('Image upload failed.'));
    reader.readAsDataURL(file);
  });
}
