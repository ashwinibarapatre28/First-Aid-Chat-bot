/**
 * FirstAid AI - Core Script
 * Manages search filtering, timer widget, user history tracking in localStorage.
 */

document.addEventListener('DOMContentLoaded', () => {
    initSearchFilter();
    initTimerWidget();
    trackPageHistory();
});

/* Search Filter for Emergency Cards */
function initSearchFilter() {
    const searchInput = document.getElementById('emergencySearch');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        const cards = document.querySelectorAll('.emergency-card');

        cards.forEach(card => {
            const title = card.getAttribute('data-title') || '';
            const desc = card.getAttribute('data-desc') || '';
            const keywords = card.getAttribute('data-keywords') || '';

            if (title.includes(query) || desc.includes(query) || keywords.includes(query)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

/* Response Stopwatch / Timer Widget */
let timerInterval = null;
let timerSeconds = 0;

function initTimerWidget() {
    const display = document.getElementById('timerDisplay');
    const startBtn = document.getElementById('timerStartBtn');
    const pauseBtn = document.getElementById('timerPauseBtn');
    const resetBtn = document.getElementById('timerResetBtn');

    if (!display || !startBtn) return;

    startBtn.addEventListener('click', () => {
        if (timerInterval) return;
        timerInterval = setInterval(() => {
            timerSeconds++;
            updateTimerDisplay(display);
        }, 1000);
    });

    pauseBtn.addEventListener('click', () => {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    });

    resetBtn.addEventListener('click', () => {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        timerSeconds = 0;
        updateTimerDisplay(display);
    });
}

function updateTimerDisplay(display) {
    const mins = Math.floor(timerSeconds / 60).toString().padStart(2, '0');
    const secs = (timerSeconds % 60).toString().padStart(2, '0');
    display.textContent = `${mins}:${secs}`;
}

/* Track Viewed Emergency in LocalStorage */
function trackPageHistory() {
    const guideElement = document.getElementById('emergencyGuideMeta');
    if (!guideElement) return;

    const id = guideElement.getAttribute('data-id');
    const title = guideElement.getAttribute('data-title');
    const severity = guideElement.getAttribute('data-severity');

    if (!id || !title) return;

    let history = JSON.parse(localStorage.getItem('firstAidHistory') || '[]');

    // Remove duplicates if already logged recently
    history = history.filter(item => item.id !== id);

    const now = new Date();
    const formattedDate = now.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    history.unshift({
        id: id,
        title: title,
        severity: severity,
        date: formattedDate
    });

    // Keep max 20 entries
    if (history.length > 20) history.pop();

    localStorage.setItem('firstAidHistory', JSON.stringify(history));
}

/* History Page Renderer */
function renderHistoryTable() {
    const tableBody = document.getElementById('historyTableBody');
    const emptyMsg = document.getElementById('historyEmptyMsg');
    if (!tableBody) return;

    const history = JSON.parse(localStorage.getItem('firstAidHistory') || '[]');

    if (history.length === 0) {
        tableBody.innerHTML = '';
        if (emptyMsg) emptyMsg.style.display = 'block';
        return;
    }

    if (emptyMsg) emptyMsg.style.display = 'none';

    tableBody.innerHTML = history.map(item => `
        <tr>
            <td><strong>${item.title}</strong></td>
            <td><span class="severity-badge ${item.severity.toLowerCase()}">${item.severity}</span></td>
            <td>${item.date}</td>
            <td>
                <a href="/guide/${item.id}" class="btn-card-guide" style="display:inline-flex; width:auto; padding:0.4rem 0.8rem;">
                    View Guide →
                </a>
            </td>
        </tr>
    `).join('');
}

function clearUserHistory() {
    localStorage.removeItem('firstAidHistory');
    renderHistoryTable();
}
