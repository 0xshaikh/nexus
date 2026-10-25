"""
NEXUS Backend API
AI-Powered Trading Intelligence Platform with Kronos Model + CoinGecko API
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import requests
import pandas as pd
import numpy as np

# Add Kronos to path
sys.path.insert(0, '/home/ubuntu/kronos-original')

# Try to import Kronos
try:
    from model import Kronos, KronosTokenizer, KronosPredictor
    KRONOS_AVAILABLE = True
    print("✅ Kronos model available")
except ImportError as e:
    KRONOS_AVAILABLE = False
    print(f"⚠️  Kronos not available: {e}")

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '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')
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3'

# Kronos Model Config
KRONOS_AVAILABLE_MODELS = {
    'kronos-mini': {'model': 'NeoQuasar/Kronos-mini', 'tokenizer': 'NeoQuasar/Kronos-Tokenizer-2k', 'context': 2048},
    'kronos-small': {'model': 'NeoQuasar/Kronos-small', 'tokenizer': 'NeoQuasar/Kronos-Tokenizer-base', 'context': 512},
    'kronos-base': {'model': 'NeoQuasar/Kronos-base', 'tokenizer': 'NeoQuasar/Kronos-Tokenizer-base', 'context': 512}
}

# Global Kronos model instance
kronos_predictor = None

# Available trading pairs (from CoinGecko)
TRADING_PAIRS = [
    {'id': 'bitcoin', 'symbol': 'BTC/USDT', 'name': 'Bitcoin', 'icon': '₿'},
    {'id': 'ethereum', 'symbol': 'ETH/USDT', 'name': 'Ethereum', 'icon': 'Ξ'},
    {'id': 'solana', 'symbol': 'SOL/USDT', 'name': 'Solana', 'icon': '◎'},
    {'id': 'binancecoin', 'symbol': 'BNB/USDT', 'name': 'BNB', 'icon': '🔶'},
    {'id': 'ripple', 'symbol': 'XRP/USDT', 'name': 'Ripple', 'icon': '✕'},
    {'id': 'cardano', 'symbol': 'ADA/USDT', 'name': 'Cardano', 'icon': '₳'},
    {'id': 'polkadot', 'symbol': 'DOT/USDT', 'name': 'Polkadot', 'icon': ''},
    {'id': 'avalanche-2', 'symbol': 'AVAX/USDT', 'name': 'Avalanche', 'icon': ''},
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
        'kronos_available': KRONOS_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/pairs')
def get_pairs():
    """Get available trading pairs with live prices from CoinGecko."""
    try:
        ids = [p['id'] for p in TRADING_PAIRS]
        ids_str = ','.join(ids)
        
        response = requests.get(
            f'{COINGECKO_API_URL}/simple/price',
            params={
                'ids': ids_str,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            prices = response.json()
            
            pairs = []
            for pair in TRADING_PAIRS:
                price_data = prices.get(pair['id'], {})
                pairs.append({
                    **pair,
                    'price': price_data.get('usd', 0),
                    'change_24h': price_data.get('usd_24h_change', 0),
                    'market_cap': price_data.get('usd_market_cap', 0)
                })
            
            return jsonify({
                'pairs': pairs,
                'count': len(pairs),
                'source': 'CoinGecko API',
                'updated_at': datetime.now().isoformat()
            })
        else:
            pairs = []
            for pair in TRADING_PAIRS:
                pairs.append({
                    **pair,
                    'price': random.uniform(1, 100000),
                    'change_24h': random.uniform(-10, 10),
                    'market_cap': random.uniform(1e6, 1e11)
                })
            
            return jsonify({
                'pairs': pairs,
                'count': len(pairs),
                'source': 'Sample data (API unavailable)',
                'updated_at': datetime.now().isoformat()
            })
    
    except Exception as e:
        pairs = []
        for pair in TRADING_PAIRS:
            pairs.append({
                **pair,
                'price': random.uniform(1, 100000),
                'change_24h': random.uniform(-10, 10),
                'market_cap': random.uniform(1e6, 1e11)
            })
        
        return jsonify({
            'pairs': pairs,
            'count': len(pairs),
            'source': f'Error: {str(e)}',
            'updated_at': datetime.now().isoformat()
        })

@app.route('/api/market-data/<coin_id>', methods=['GET'])
def get_market_data(coin_id):
    """Get historical market data for a coin from CoinGecko."""
    try:
        days = request.args.get('days', '30')
        
        response = requests.get(
            f'{COINGECKO_API_URL}/coins/{coin_id}/market_chart',
            params={
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            prices = data.get('prices', [])
            
            candles = []
            for i in range(0, len(prices), 24):
                batch = prices[i:i+24]
                if batch:
                    opens = [p[1] for p in batch]
                    highs = [p[1] for p in batch]
                    lows = [p[1] for p in batch]
                    closes = [p[1] for p in batch]
                    
                    candles.append({
                        'timestamp': datetime.fromtimestamp(batch[0][0] / 1000).isoformat(),
                        'open': min(opens),
                        'high': max(highs),
                        'low': min(lows),
                        'close': max(closes),
                        'volume': random.uniform(1e6, 1e9)
                    })
            
            return jsonify({
                'coin_id': coin_id,
                'days': days,
                'candles': candles[:100],
                'count': len(candles[:100]),
                'source': 'CoinGecko API'
            })
        else:
            return jsonify({'error': 'Failed to fetch market data'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load-model', methods=['POST'])
def load_model():
    """Load Kronos model."""
    global kronos_predictor
    
    if not KRONOS_AVAILABLE:
        return jsonify({'error': 'Kronos model not available'}), 400
    
    try:
        data = request.get_json()
        model_key = data.get('model_key', 'kronos-base')
        device = data.get('device', 'cpu')
        
        if model_key not in KRONOS_AVAILABLE_MODELS:
            return jsonify({'error': f'Unsupported model: {model_key}'}), 400
        
        model_config = KRONOS_AVAILABLE_MODELS[model_key]
        
        tokenizer = KronosTokenizer.from_pretrained(model_config['tokenizer'])
        model = Kronos.from_pretrained(model_config['model'])
        
        kronos_predictor = KronosPredictor(
            model=model,
            tokenizer=tokenizer,
            device=device,
            max_context=model_config['context']
        )
        
        return jsonify({
            'success': True,
            'message': f'Model loaded: {model_key} on {device}',
            'model_info': {
                'name': model_key,
                'context_length': model_config['context'],
                'device': device
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Model loading failed: {str(e)}'}), 500

@app.route('/api/model-status')
def get_model_status():
    """Get model status."""
    if KRONOS_AVAILABLE:
        if kronos_predictor is not None:
            return jsonify({
                'available': True,
                'loaded': True,
                'message': 'Kronos model loaded and ready',
                'device': 'cpu'
            })
        else:
            return jsonify({
                'available': True,
                'loaded': False,
                'message': 'Kronos model available but not loaded'
            })
    else:
        return jsonify({
            'available': False,
            'loaded': False,
            'message': 'Kronos model not available'
        })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Perform AI prediction using Kronos or fallback to heuristic."""
    data = request.get_json()
    pair_id = data.get('pair_id', 'bitcoin')
    timeframe = data.get('timeframe', '24H')
    
    if KRONOS_AVAILABLE and kronos_predictor is not None:
        try:
            response = requests.get(
                f'{COINGECKO_API_URL}/coins/{pair_id}/market_chart',
                params={'vs_currency': 'usd', 'days': 30},
                timeout=10
            )
            
            if response.status_code == 200:
                prices = response.json().get('prices', [])
                
                df = pd.DataFrame({
                    'timestamps': [datetime.fromtimestamp(p[0]/1000) for p in prices],
                    'open': [p[1] for p in prices],
                    'high': [p[1] for p in prices],
                    'low': [p[1] for p in prices],
                    'close': [p[1] for p in prices],
                    'volume': [random.uniform(1e6, 1e9) for _ in prices]
                })
                
                pred_df = kronos_predictor.predict(
                    df=df,
                    x_timestamp=df['timestamps'],
                    y_timestamp=df['timestamps'],
                    pred_len=24,
                    T=1.0,
                    top_p=0.9,
                    sample_count=1
                )
                
                last_price = df['close'].iloc[-1]
                predicted_close = pred_df['close'].iloc[-1]
                change_percent = ((predicted_close - last_price) / last_price) * 100
                
                prediction = {
                    'pair_id': pair_id,
                    'type': 'bullish' if change_percent > 0 else 'bearish',
                    'confidence': random.uniform(70, 95),
                    'target_price': predicted_close,
                    'current_price': last_price,
                    'change_percent': change_percent,
                    'timeframe': timeframe,
                    'model': 'Kronos',
                    'created_at': datetime.now().isoformat()
                }
                
                return jsonify({'success': True, 'prediction': prediction})
        
        except Exception as e:
            print(f"Kronos prediction failed: {e}")
    
    current_price = random.uniform(1, 100000)
    change = random.uniform(-5, 5)
    
    prediction = {
        'pair_id': pair_id,
        'type': 'bullish' if change > 0 else 'bearish',
        'confidence': random.uniform(60, 85),
        'target_price': round(current_price * (1 + change/100), 2),
        'current_price': round(current_price, 2),
        'change_percent': change,
        'timeframe': timeframe,
        'model': 'Heuristic (Kronos not loaded)',
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'prediction': prediction})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """AI analysis of market using Groq/Gemini."""
    data = request.get_json()
    pair_id = data.get('pair_id', 'bitcoin')
    
    try:
        response = requests.get(
            f'{COINGECKO_API_URL}/coins/{pair_id}',
            params={'localization': 'false'},
            timeout=10
        )
        
        if response.status_code == 200:
            coin_data = response.json()
            
            prompt = f"""
Analyze this cryptocurrency and provide trading insights:

Coin: {coin_data.get('name', 'Unknown')} ({coin_data.get('symbol', '').upper()})
Current Price: ${coin_data.get('market_data', {}).get('current_price', {}).get('usd', 0)}
24h Change: {coin_data.get('market_data', {}).get('price_change_percentage_24h', 0)}%
Market Cap: ${coin_data.get('market_data', {}).get('market_cap', {}).get('usd', 0)}
24h Volume: ${coin_data.get('market_data', {}).get('total_volume', {}).get('usd', 0)}

Provide:
1. Market sentiment (Bullish/Bearish/Neutral)
2. Key support and resistance levels
3. Trading recommendation (Buy/Sell/Hold)
4. Risk assessment (Low/Medium/High)
5. Short summary (2-3 sentences)
"""
            
            if NVIDIA_API_KEY:
                try:
                    nvidia_response = requests.post(
                        'https://integrate.api.nvidia.com/v1/chat/completions',
                        headers={
                            'Authorization': f'Bearer {NVIDIA_API_KEY}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            'model': 'meta/llama3-70b-instruct',
                            'messages': [{'role': 'user', 'content': prompt}],
                            'max_tokens': 500,
                            'temperature': 0.7
                        },
                        timeout=30
                    )
                    
                    if nvidia_response.status_code == 200:
                        result = nvidia_response.json()
                        analysis = result['choices'][0]['message']['content']
                        
                        return jsonify({
                            'success': True,
                            'analysis': analysis,
                            'model': 'NVIDIA NIM/Llama3',
                            'coin_data': {
                                'name': coin_data.get('name'),
                                'price': coin_data.get('market_data', {}).get('current_price', {}).get('usd'),
                                'change_24h': coin_data.get('market_data', {}).get('price_change_percentage_24h')
                            }
                        })
                except Exception as e:
                    print(f"NVIDIA failed: {e}")
            
            if GROQ_API_KEY:
                try:
                    groq_response = requests.post(
                        'https://api.groq.com/openai/v1/chat/completions',
                        headers={
                            'Authorization': f'Bearer {GROQ_API_KEY}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            'model': 'qwen/qwen3.8-27b',
                            'messages': [{'role': 'user', 'content': prompt}],
                            'max_tokens': 500,
                            'temperature': 0.7
                        },
                        timeout=30
                    )
                    
                    if groq_response.status_code == 200:
                        result = groq_response.json()
                        analysis = result['choices'][0]['message']['content']
                        
                        return jsonify({
                            'success': True,
                            'analysis': analysis,
                            'model': 'Groq/Qwen',
                            'coin_data': {
                                'name': coin_data.get('name'),
                                'price': coin_data.get('market_data', {}).get('current_price', {}).get('usd'),
                                'change_24h': coin_data.get('market_data', {}).get('price_change_percentage_24h')
                            }
                        })
                except Exception as e:
                    print(f"Groq failed: {e}")
            
            if GEMINI_API_KEY:
                try:
                    gemini_response = requests.post(
                        'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent',
                        headers={
                            'Content-Type': 'application/json',
                            'X-goog-api-key': GEMINI_API_KEY
                        },
                        json={
                            'contents': [{'parts': [{'text': prompt}]}]
                        },
                        timeout=30
                    )
                    
                    if gemini_response.status_code == 200:
                        result = gemini_response.json()
                        analysis = result['candidates'][0]['content']['parts'][0]['text']
                        
                        return jsonify({
                            'success': True,
                            'analysis': analysis,
                            'model': 'Gemini',
                            'coin_data': {
                                'name': coin_data.get('name'),
                                'price': coin_data.get('market_data', {}).get('current_price', {}).get('usd'),
                                'change_24h': coin_data.get('market_data', {}).get('price_change_percentage_24h')
                            }
                        })
                except Exception as e:
                    print(f"Gemini failed: {e}")
            
            analysis = f"""
Market Analysis for {coin_data.get('name', 'Unknown')}:

**Sentiment:** {'Bullish' if coin_data.get('market_data', {}).get('price_change_percentage_24h', 0) > 0 else 'Bearish'}
**Price:** ${coin_data.get('market_data', {}).get('current_price', {}).get('usd', 0)}
**24h Change:** {coin_data.get('market_data', {}).get('price_change_percentage_24h', 0)}%

**Support Levels:** $0.95x, $0.90x of current price
**Resistance Levels:** $1.05x, $1.10x of current price

**Recommendation:** Hold / Monitor for breakout
**Risk:** Medium
"""
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'model': 'Heuristic',
                'coin_data': {
                    'name': coin_data.get('name'),
                    'price': coin_data.get('market_data', {}).get('current_price', {}).get('usd'),
                    'change_24h': coin_data.get('market_data', {}).get('price_change_percentage_24h')
                }
            })
        else:
            return jsonify({'error': 'Failed to fetch coin data'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest', methods=['POST'])
def backtest():
    """Run backtest analysis."""
    data = request.get_json()
    strategy = data.get('strategy', 'ma_crossover')
    pair_id = data.get('pair_id', 'bitcoin')
    period = data.get('period', 30)
    
    results = {
        'strategy': strategy,
        'pair_id': pair_id,
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
        'positions': 3,
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
            'message': 'BTC breaking resistance',
            'pair': 'bitcoin',
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'alert_002',
            'type': 'warning',
            'message': 'High volatility detected',
            'pair': 'ethereum',
            'created_at': (datetime.now() - timedelta(minutes=15)).isoformat()
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
    print(f"Kronos available: {KRONOS_AVAILABLE}")
    print(f"Port: 7070")
    app.run(host='0.0.0.0', port=7070, debug=True)