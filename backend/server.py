"""
NEXUS Backend API
AI-Powered Trading Intelligence Platform
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configuration
API_KEYS = {
    'groq': os.environ.get('GROQ_API_KEY', ''),
    'gemini': os.environ.get('GEMINI_API_KEY', ''),
    'oxion': os.environ.get('OXION_API_KEY', '')
}

# Available trading pairs
TRADING_PAIRS = [
    {'symbol': 'BTC/USDT', 'name': 'Bitcoin', 'icon': '₿', 'price': 67234.50, 'change': 2.34},
    {'symbol': 'ETH/USDT', 'name': 'Ethereum', 'icon': 'Ξ', 'price': 3456.78, 'change': -1.23},
    {'symbol': 'SOL/USDT', 'name': 'Solana', 'icon': '◎', 'price': 156.78, 'change': 5.67},
    {'symbol': 'BNB/USDT', 'name': 'BNB', 'icon': '🔶', 'price': 567.89, 'change': 1.45},
    {'symbol': 'XRP/USDT', 'name': 'Ripple', 'icon': '✕', 'price': 0.5678, 'change': -0.89},
]

# Sample positions
SAMPLE_POSITIONS = [
    {
        'id': 'pos_001',
        'pair': 'BTC/USDT',
        'icon': '₿',
        'type': 'long',
        'size': 0.5,
        'entry_price': 65000.00,
        'current_price': 67234.50,
        'pnl': 1117.25,
        'pnl_percent': 3.44
    },
    {
        'id': 'pos_002',
        'pair': 'ETH/USDT',
        'icon': 'Ξ',
        'type': 'short',
        'size': 10,
        'entry_price': 3600.00,
        'current_price': 3456.78,
        'pnl': 1432.20,
        'pnl_percent': 4.0
    },
    {
        'id': 'pos_003',
        'pair': 'SOL/USDT',
        'icon': '◎',
        'type': 'long',
        'size': 100,
        'entry_price': 148.00,
        'current_price': 156.78,
        'pnl': 878.00,
        'pnl_percent': 5.93
    }
]

# Sample predictions
SAMPLE_PREDICTIONS = [
    {
        'id': 'pred_001',
        'pair': 'BTC/USDT',
        'type': 'bullish',
        'confidence': 94.2,
        'target_price': 72000.00,
        'current_price': 67234.50,
        'timeframe': '24H',
        'created_at': datetime.now().isoformat()
    },
    {
        'id': 'pred_002',
        'pair': 'ETH/USDT',
        'type': 'bearish',
        'confidence': 78.5,
        'target_price': 3200.00,
        'current_price': 3456.78,
        'timeframe': '24H',
        'created_at': datetime.now().isoformat()
    }
]

@app.route('/')
def index():
    """Serve the frontend."""
    return app.send_static_file('index.html')

@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'nexus-api',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/pairs')
def get_pairs():
    """Get available trading pairs."""
    return jsonify({
        'pairs': TRADING_PAIRS,
        'count': len(TRADING_PAIRS)
    })

@app.route('/api/positions')
def get_positions():
    """Get active positions."""
    return jsonify({
        'positions': SAMPLE_POSITIONS,
        'count': len(SAMPLE_POSITIONS),
        'total_pnl': sum(p['pnl'] for p in SAMPLE_POSITIONS)
    })

@app.route('/api/predictions')
def get_predictions():
    """Get AI predictions."""
    return jsonify({
        'predictions': SAMPLE_PREDICTIONS,
        'count': len(SAMPLE_PREDICTIONS)
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Perform AI prediction."""
    data = request.get_json()
    pair = data.get('pair', 'BTC/USDT')
    timeframe = data.get('timeframe', '24H')
    
    # Generate mock prediction
    prediction = {
        'pair': pair,
        'timeframe': timeframe,
        'type': random.choice(['bullish', 'bearish', 'neutral']),
        'confidence': round(random.uniform(60, 95), 1),
        'target_price': round(random.uniform(0.8, 1.2) * next(p['price'] for p in TRADING_PAIRS if p['symbol'] == pair), 2),
        'current_price': next(p['price'] for p in TRADING_PAIRS if p['symbol'] == pair),
        'signals': {
            'rsi': round(random.uniform(20, 80), 2),
            'macd': round(random.uniform(-50, 50), 2),
            'bollinger': random.choice(['upper', 'middle', 'lower']),
            'volume': round(random.uniform(0.5, 2.0), 2)
        },
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'prediction': prediction
    })

@app.route('/api/backtest', methods=['POST'])
def backtest():
    """Run backtest analysis."""
    data = request.get_json()
    strategy = data.get('strategy', 'ma_crossover')
    pair = data.get('pair', 'BTC/USDT')
    period = data.get('period', 30)
    
    # Generate mock backtest results
    results = {
        'strategy': strategy,
        'pair': pair,
        'period_days': period,
        'total_trades': random.randint(10, 50),
        'win_rate': round(random.uniform(50, 90), 1),
        'profit_factor': round(random.uniform(1.5, 3.5), 2),
        'max_drawdown': round(random.uniform(5, 25), 1),
        'sharpe_ratio': round(random.uniform(1.0, 3.0), 2),
        'total_return': round(random.uniform(10, 100), 2),
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'results': results
    })

@app.route('/api/portfolio')
def get_portfolio():
    """Get portfolio summary."""
    return jsonify({
        'total_value': 125432.50,
        'total_pnl': 2340.50,
        'total_pnl_percent': 1.87,
        'positions': len(SAMPLE_POSITIONS),
        'win_rate': 78.5,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/alerts')
def get_alerts():
    """Get live alerts."""
    alerts = [
        {
            'id': 'alert_001',
            'type': 'critical',
            'message': 'BTC breaking resistance at $67,500',
            'pair': 'BTC/USDT',
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'alert_002',
            'type': 'warning',
            'message': 'High volatility detected in ETH',
            'pair': 'ETH/USDT',
            'created_at': (datetime.now() - timedelta(minutes=15)).isoformat()
        },
        {
            'id': 'alert_003',
            'type': 'info',
            'message': 'AI model retrained with latest data',
            'pair': None,
            'created_at': (datetime.now() - timedelta(hours=1)).isoformat()
        }
    ]
    
    return jsonify({
        'alerts': alerts,
        'count': len(alerts)
    })

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    """Execute a trade (mock)."""
    data = request.get_json()
    
    trade = {
        'id': f'trade_{random.randint(1000, 9999)}',
        'pair': data.get('pair', 'BTC/USDT'),
        'type': data.get('type', 'long'),
        'size': data.get('size', 0.1),
        'price': data.get('price', 67234.50),
        'status': 'executed',
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'trade': trade,
        'message': f"Trade executed: {trade['type']} {trade['size']} {trade['pair']} @ ${trade['price']}"
    })

if __name__ == '__main__':
    print("Starting NEXUS API Server...")
    print(f"Port: 7070")
    app.run(host='0.0.0.0', port=7070, debug=True)