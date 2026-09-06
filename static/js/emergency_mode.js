/**
 * FirstAid AI - Quick Emergency Mode
 */

let emCurrentStepIndex = 0;
let emSteps = [];

document.addEventListener('DOMContentLoaded', () => {
    initEmergencyMode();
});

function initEmergencyMode() {
    const toggleBtns = document.querySelectorAll('.btn-emergency-mode-toggle');
    const overlay = document.getElementById('emergencyModeOverlay');
    const closeBtn = document.getElementById('emCloseBtn');

    if (!overlay) return;

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => openEmergencyMode());
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => closeEmergencyMode());
    }

    const prevBtn = document.getElementById('emPrevStep');
    const nextBtn = document.getElementById('emNextStep');

    if (prevBtn) prevBtn.addEventListener('click', () => changeEmStep(-1));
    if (nextBtn) nextBtn.addEventListener('click', () => changeEmStep(1));
}

function openEmergencyMode() {
    const overlay = document.getElementById('emergencyModeOverlay');
    if (!overlay) return;

    // Grab current steps from page context or active emergency guide
    const stepTextEl = document.getElementById('activeStepText');
    const allStepsEls = document.querySelectorAll('[data-step-text]');

    emSteps = [];
    if (allStepsEls.length > 0) {
        allStepsEls.forEach(el => emSteps.push(el.getAttribute('data-step-text')));
    } else if (stepTextEl) {
        emSteps.push(stepTextEl.textContent);
    } else {
        emSteps = [
            "Assess area safety before approaching the victim.",
            "Call Emergency Services 112 immediately if life-threatening.",
            "Stay calm and follow step-by-step first-aid guidance.",
            "Monitor victim's breathing and responsiveness continuously."
        ];
    }

    emCurrentStepIndex = 0;
    renderEmStep();
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeEmergencyMode() {
    const overlay = document.getElementById('emergencyModeOverlay');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
}

function changeEmStep(dir) {
    emCurrentStepIndex += dir;
    if (emCurrentStepIndex < 0) emCurrentStepIndex = 0;
    if (emCurrentStepIndex >= emSteps.length) emCurrentStepIndex = emSteps.length - 1;
    renderEmStep();
}

function renderEmStep() {
    const textEl = document.getElementById('emStepText');
    const tagEl = document.getElementById('emStepTag');
    const counterEl = document.getElementById('emStepCounter');

    if (textEl) textEl.textContent = emSteps[emCurrentStepIndex] || '';
    if (tagEl) tagEl.textContent = `STEP ${emCurrentStepIndex + 1}`;
    if (counterEl) counterEl.textContent = `Step ${emCurrentStepIndex + 1} of ${emSteps.length}`;
}
