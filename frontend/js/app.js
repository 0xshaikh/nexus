// NEXUS - Trading Intelligence Platform

// API Configuration
const API_BASE = 'http://localhost:7070';

// Application State
const state = {
    currentPage: 'dashboard',
    selectedTimeframe: '1H',
    models: [],
    predictions: [],
    positions: []
};

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
    hideLoadingScreen();
    initializeNavigation();
    initializeCharts();
    loadDashboardData();
    loadModelStatus();
});

// Hide Loading Screen
function hideLoadingScreen() {
    const screen = document.getElementById('loading-screen');
    if (screen) {
        setTimeout(() => {
            screen.classList.add('hidden');
        }, 1500);
    }
}

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            navigateToPage(page);
        });
    });
    
    // Timeframe controls
    const timeframeBtns = document.querySelectorAll('.control-btn');
    timeframeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            timeframeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.selectedTimeframe = btn.dataset.timeframe;
            loadChart(state.selectedTimeframe);
        });
    });
}

function navigateToPage(page) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === page) {
            item.classList.add('active');
        }
    });
    
    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    
    const pageEl = document.getElementById(`page-${page}`);
    if (pageEl) {
        pageEl.classList.add('active');
    }
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'trading': 'Trading Terminal',
        'predictions': 'AI Predictions',
        'backtesting': 'Backtesting Engine',
        'portfolio': 'Portfolio Management',
        'settings': 'Settings'
    };
    
    document.getElementById('page-title').textContent = titles[page] || page;
    
    state.currentPage = page;
}

// Charts
function initializeCharts() {
    // Placeholder for chart initialization
    console.log('Charts initialized');
}

function loadChart(timeframe) {
    // Placeholder for chart loading
    console.log(`Loading chart for timeframe: ${timeframe}`);
}

// Dashboard Data
async function loadDashboardData() {
    try {
        // Load positions
        await loadPositions();
        
        // Load predictions
        await loadPredictions();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function loadPositions() {
    // Placeholder - will be connected to backend
    state.positions = [
        {
            pair: 'BTC/USDT',
            icon: '₿',
            type: 'long',
            size: '0.5 BTC',
            pnl: 1234
        },
        {
            pair: 'ETH/USDT',
            icon: 'Ξ',
            type: 'short',
            size: '10 ETH',
            pnl: -456
        },
        {
            pair: 'SOL/USDT',
            icon: '◎',
            type: 'long',
            size: '100 SOL',
            pnl: 890
        }
    ];
    
    // Update UI
    updatePositionsUI();
}

function updatePositionsUI() {
    const positionsList = document.querySelector('.positions-list');
    if (!positionsList) return;
    
    positionsList.innerHTML = state.positions.map(pos => `
        <div class="position-item">
            <div class="position-pair">
                <span class="pair-icon">${pos.icon}</span>
                <span class="pair-name">${pos.pair}</span>
            </div>
            <div class="position-info">
                <span class="position-type ${pos.type}">${pos.type}</span>
                <span class="position-size">${pos.size}</span>
            </div>
            <div class="position-pnl ${pos.pnl >= 0 ? 'positive' : 'negative'}">
                ${pos.pnl >= 0 ? '+' : ''}$${Math.abs(pos.pnl).toLocaleString()}
            </div>
        </div>
    `).join('');
}

async function loadPredictions() {
    // Placeholder - will be connected to backend
    console.log('Loading predictions...');
}

// Model Status
async function loadModelStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/model-status`);
        if (response.ok) {
            const data = await response.json();
            console.log('Model status:', data);
        }
    } catch (error) {
        console.log('Backend not available, using demo mode');
    }
}

// Utility Functions
function formatNumber(num) {
    return num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatCurrency(num) {
    return '$' + formatNumber(num);
}

function formatPercent(num) {
    return (num >= 0 ? '+' : '') + num.toFixed(2) + '%';
}

// Real-time updates (placeholder)
function startRealTimeUpdates() {
    // Update prices every 5 seconds
    setInterval(() => {
        updatePrices();
    }, 5000);
    
    // Update positions every 10 seconds
    setInterval(() => {
        updatePositions();
    }, 10000);
}

function updatePrices() {
    // Simulate price updates
    console.log('Updating prices...');
}

function updatePositions() {
    // Simulate position updates
    console.log('Updating positions...');
}

// Start real-time updates
startRealTimeUpdates();

// Export for debugging
window.NEXUS = {
    state,
    navigateToPage,
    loadDashboardData,
    loadChart
};