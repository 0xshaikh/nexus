// NEXUS Setup Wizard JavaScript

// Configuration
const API_BASE = 'http://localhost:7070';

// State
const state = {
    currentStep: 1,
    aiKeys: {},
    tradingConfig: {},
    aiTeam: {
        analyst: true,
        predictor: true,
        risk: true,
        executor: true,
        news: true,
        copy: false
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSavedConfig();
    updateProgress();
    setupEventListeners();
});

// Load saved configuration
function loadSavedConfig() {
    const saved = localStorage.getItem('nexus-config');
    if (saved) {
        const config = JSON.parse(saved);
        state.aiKeys = config.aiKeys || {};
        state.tradingConfig = config.tradingConfig || {};
        state.aiTeam = config.aiTeam || state.aiTeam;
        
        // Populate fields
        if (state.aiKeys.nvidia) document.getElementById('nvidia-key').value = state.aiKeys.nvidia;
        if (state.aiKeys.gemini) document.getElementById('gemini-key').value = state.aiKeys.gemini;
        if (state.aiKeys.groq) document.getElementById('groq-key').value = state.aiKeys.groq;
        if (state.aiKeys.mistral) document.getElementById('mistral-key').value = state.aiKeys.mistral;
        
        if (state.tradingConfig.binance_key) document.getElementById('binance-key').value = state.tradingConfig.binance_key;
        if (state.tradingConfig.binance_secret) document.getElementById('binance-secret').value = state.tradingConfig.binance_secret;
        if (state.tradingConfig.starting_balance) document.getElementById('starting-balance').value = state.tradingConfig.starting_balance;
        
        // Update AI provider statuses
        updateProviderStatuses();
        updateAgentTeam();
    }
}

// Save configuration
function saveConfig() {
    localStorage.setItem('nexus-config', JSON.stringify({
        aiKeys: state.aiKeys,
        tradingConfig: state.tradingConfig,
        aiTeam: state.aiTeam,
        completed: true
    }));
}

// Step Navigation
function goToStep(step) {
    document.querySelectorAll('.setup-step').forEach(s => s.classList.remove('active'));
    document.getElementById(`step-${step}`).classList.add('active');
    state.currentStep = step;
    updateProgress();
}

function updateProgress() {
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        const stepNumber = index + 1;
        step.classList.toggle('active', stepNumber <= state.currentStep);
        step.classList.toggle('complete', stepNumber < state.currentStep);
    });
}

// AI Keys Configuration
function saveAIKeys() {
    const nvidiaKey = document.getElementById('nvidia-key').value.trim();
    const geminiKey = document.getElementById('gemini-key').value.trim();
    const groqKey = document.getElementById('groq-key').value.trim();
    const mistralKey = document.getElementById('mistral-key').value.trim();
    
    state.aiKeys = {
        nvidia: nvidiaKey || null,
        gemini: geminiKey || null,
        groq: groqKey || null,
        mistral: mistralKey || null
    };
    
    // Validate
    if (!nvidiaKey && !geminiKey && !groqKey && !mistralKey) {
        alert('Please add at least one AI API key');
        return;
    }
    
    // Update UI
    updateProviderStatuses();
    saveConfig();
    
    // Continue to next step
    goToStep(2);
}

function updateProviderStatuses() {
    const providers = {
        nvidia: document.getElementById('nvidia-key').value.trim(),
        gemini: document.getElementById('gemini-key').value.trim(),
        groq: document.getElementById('groq-key').value.trim(),
        mistral: document.getElementById('mistral-key').value.trim()
    };
    
    Object.entries(providers).forEach(([provider, key]) => {
        const card = document.querySelector(`[data-provider="${provider}"]`);
        const status = card.querySelector('.provider-status');
        const indicator = status.querySelector('.status-indicator');
        const text = status.querySelector('span:last-child');
        
        if (key) {
            indicator.classList.remove('inactive');
            indicator.classList.add('active');
            text.textContent = 'Configured';
            card.classList.add('configured');
        } else {
            indicator.classList.remove('active');
            indicator.classList.add('inactive');
            text.textContent = 'Not Configured';
            card.classList.remove('configured');
        }
    });
}

// Trading Configuration
function saveTradingConfig() {
    const binanceKey = document.getElementById('binance-key').value.trim();
    const binanceSecret = document.getElementById('binance-secret').value.trim();
    const startingBalance = parseInt(document.getElementById('starting-balance').value);
    const tradingMode = document.querySelector('input[name="trading-mode"]:checked').value;
    const riskLevel = document.querySelector('input[name="risk-level"]:checked').value;
    const selectedExchange = document.querySelector('.exchange-option.selected').dataset.exchange;
    
    state.tradingConfig = {
        exchange: selectedExchange,
        binance_key: binanceKey || null,
        binance_secret: binanceSecret || null,
        trading_mode: tradingMode,
        risk_level: riskLevel,
        starting_balance: startingBalance
    };
    
    // Validate
    if (!binanceKey || !binanceSecret) {
        alert('Please enter both Binance API key and secret key');
        return;
    }
    
    saveConfig();
    goToStep(3);
}

// AI Team Configuration
function saveAITeam() {
    const agents = document.querySelectorAll('.ai-agent-card');
    let activeCount = 0;
    
    agents.forEach(agent => {
        const agentName = agent.dataset.agent;
        const checkbox = agent.querySelector('input[type="checkbox"]');
        state.aiTeam[agentName] = checkbox.checked;
        
        if (checkbox.checked) {
            agent.classList.add('active');
            agent.querySelector('.status-dot').classList.add('active');
            agent.querySelector('.status-dot').classList.remove('inactive');
            agent.querySelector('.agent-status span:last-child').textContent = 'Active';
            activeCount++;
        } else {
            agent.classList.remove('active');
            agent.querySelector('.status-dot').classList.remove('active');
            agent.querySelector('.status-dot').classList.add('inactive');
            agent.querySelector('.agent-status span:last-child').textContent = 'Inactive';
        }
    });
    
    document.getElementById('active-agents-count').textContent = activeCount;
    document.querySelector('.meter-fill').style.width = `${(activeCount / 6) * 100}%`;
    document.querySelector('.team-power-meter span').textContent = `Team Power: ${Math.round((activeCount / 6) * 100)}%`;
    
    saveConfig();
    goToStep(4);
}

function updateAgentTeam() {
    const agents = document.querySelectorAll('.ai-agent-card');
    agents.forEach(agent => {
        const agentName = agent.dataset.agent;
        const checkbox = agent.querySelector('input[type="checkbox"]');
        checkbox.checked = state.aiTeam[agentName];
        
        if (checkbox.checked) {
            agent.classList.add('active');
            agent.querySelector('.status-dot').classList.add('active');
            agent.querySelector('.status-dot').classList.remove('inactive');
            agent.querySelector('.agent-status span:last-child').textContent = 'Active';
        }
    });
}

// Utility Functions
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    input.type = input.type === 'password' ? 'text' : 'password';
}

function skipSetup() {
    if (confirm('Skip setup? You can always configure later in Settings.')) {
        saveConfig();
        window.location.href = '/';
    }
}

function startTrading() {
    // Update summary
    const aiCount = Object.values(state.aiKeys).filter(k => k).length;
    document.getElementById('summary-ai').textContent = `${aiCount} providers configured`;
    document.getElementById('summary-exchange').textContent = `${state.tradingConfig.exchange} connected`;
    document.getElementById('summary-team').textContent = `${Object.values(state.aiTeam).filter(v => v).length} agents active`;
    document.getElementById('summary-risk').textContent = state.tradingConfig.risk_level;
    
    // Redirect to dashboard
    window.location.href = '/';
}

// Setup Event Listeners
function setupEventListeners() {
    // Exchange selection
    document.querySelectorAll('.exchange-option').forEach(option => {
        option.addEventListener('click', () => {
            document.querySelectorAll('.exchange-option').forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
        });
    });
    
    // AI Agent toggles
    document.querySelectorAll('.toggle-switch input').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            saveAITeam();
        });
    });
    
    // API key inputs
    document.querySelectorAll('.ai-provider-card input').forEach(input => {
        input.addEventListener('input', () => {
            updateProviderStatuses();
        });
    });
}