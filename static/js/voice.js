/**
 * FirstAid AI - Web Speech API Voice Read-Aloud Assistant
 */

let speechSynth = window.speechSynthesis;
let currentUtterance = null;
let isSpeaking = false;
let isPaused = false;

document.addEventListener('DOMContentLoaded', () => {
    initVoiceControls();
});

function initVoiceControls() {
    const playBtn = document.getElementById('voicePlayBtn');
    const pauseBtn = document.getElementById('voicePauseBtn');
    const stopBtn = document.getElementById('voiceStopBtn');

    if (!playBtn) return;

    playBtn.addEventListener('click', () => playVoiceInstruction());

    if (pauseBtn) {
        pauseBtn.addEventListener('click', () => {
            if (speechSynth && isSpeaking) {
                if (isPaused) {
                    speechSynth.resume();
                    isPaused = false;
                    pauseBtn.textContent = '⏸ Pause';
                } else {
                    speechSynth.pause();
                    isPaused = true;
                    pauseBtn.textContent = '▶ Resume';
                }
            }
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', () => stopVoiceInstruction());
    }
}

function playVoiceInstruction(customText = null) {
    if (!speechSynth) {
        alert("Web Speech API is not supported in this browser.");
        return;
    }

    stopVoiceInstruction();

    const textToRead = customText || getCurrentStepText();
    if (!textToRead) return;

    currentUtterance = new SpeechSynthesisUtterance(textToRead);
    currentUtterance.rate = 0.95; // Slightly slower pace for emergency clarity
    currentUtterance.pitch = 1.0;
    currentUtterance.lang = 'en-US';

    const stepTextEl = document.getElementById('activeStepText');
    if (stepTextEl) stepTextEl.classList.add('active-speaking');

    currentUtterance.onend = () => {
        isSpeaking = false;
        isPaused = false;
        if (stepTextEl) stepTextEl.classList.remove('active-speaking');
        updateVoiceButtonStates(false);
    };

    currentUtterance.onerror = (e) => {
        console.error("SpeechSynthesis error:", e);
        isSpeaking = false;
        if (stepTextEl) stepTextEl.classList.remove('active-speaking');
        updateVoiceButtonStates(false);
    };

    speechSynth.speak(currentUtterance);
    isSpeaking = true;
    isPaused = false;
    updateVoiceButtonStates(true);
}

function stopVoiceInstruction() {
    if (speechSynth) {
        speechSynth.cancel();
    }
    isSpeaking = false;
    isPaused = false;
    const stepTextEl = document.getElementById('activeStepText');
    if (stepTextEl) stepTextEl.classList.remove('active-speaking');
    updateVoiceButtonStates(false);
}

function getCurrentStepText() {
    const stepNumberTag = document.getElementById('activeStepTag');
    const stepTextEl = document.getElementById('activeStepText');
    if (!stepTextEl) return null;

    const tag = stepNumberTag ? stepNumberTag.textContent : '';
    const text = stepTextEl.textContent;
    return `${tag}. ${text}`;
}

function updateVoiceButtonStates(speaking) {
    const playBtn = document.getElementById('voicePlayBtn');
    if (!playBtn) return;

    if (speaking) {
        playBtn.style.opacity = '0.7';
    } else {
        playBtn.style.opacity = '1';
    }
}
