from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime, timedelta
import time
import threading
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Simulation state
active_simulations = {
    'DDoS': False,
    'Port Scan': False,
    'SQL Injection': False,
    'XSS': False,
    'Brute Force': False,
    'Malware': False,
    'Phishing': False
}

simulation_locks = {attack_type: threading.Lock() for attack_type in active_simulations}
simulated_alerts = []
alert_lock = threading.Lock()

# Dummy data generation functions
def generate_attack_data(attack_type=None):
    attack_types = ['DDoS', 'Port Scan', 'SQL Injection', 'XSS', 'Brute Force', 'Malware', 'Phishing']
    sources = ['External', 'Internal', 'Unknown']
    severities = ['low', 'medium', 'high', 'critical']
    
    if attack_type is None:
        attack_type = random.choice(attack_types)
    
    return {
        'id': str(uuid.uuid4()),
        'title': f"{attack_type} Attempt",
        'description': f"Detected {attack_type} activity from {random.choice(sources)} source",
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'severity': random.choice(severities),
        'source': random.choice(sources),
        'isNew': True,
        'attackType': attack_type
    }

def generate_port_data():
    services = ['HTTP', 'HTTPS', 'SSH', 'FTP', 'MySQL', 'RDP', 'DNS']
    statuses = ['active', 'inactive', 'blocked']
    
    return {
        'port': random.randint(1, 65535),
        'service': random.choice(services),
        'traffic': round(random.uniform(0.1, 100), 1),
        'status': random.choice(statuses),
        'connections': random.randint(0, 500)
    }

def generate_traffic_data():
    now = datetime.now()
    data = []
    for i in range(30):
        timestamp = (now - timedelta(minutes=i)).strftime('%H:%M')
        data.append({
            'timestamp': timestamp,
            'inbound': round(random.uniform(1, 100), 2),
            'outbound': round(random.uniform(1, 50), 2)
        })
    return data[::-1]  # Reverse to have oldest first

def generate_system_status():
    services = ['Web Server', 'Database', 'Auth Service', 'Monitoring', 'API Gateway']
    
    # Check if any simulations are active
    any_active = any(active_simulations.values())
    
    if any_active:
        # System is under attack
        statuses = ['operational', 'degraded', 'outage', 'unknown']
        
        # Calculate threat level based on active simulations
        threat_multiplier = sum(1 for sim in active_simulations.values() if sim)
        threat_level = min(random.randint(10, 30) + (threat_multiplier * 15), 100)
        
        return {
            'overallStatus': random.choices(
                statuses, 
                weights=[80 - (threat_multiplier * 10), 15 + (threat_multiplier * 5), 4 + (threat_multiplier * 5), 1]
            )[0],
            'services': [{
                'name': service,
                'status': random.choices(
                    statuses, 
                    weights=[90 - (threat_multiplier * 5), 7 + (threat_multiplier * 2), 2 + (threat_multiplier * 3), 1]
                )[0],
                'uptime': max(95 - (threat_multiplier * random.randint(0, 3)), 80)
            } for service in services],
            'lastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'threatLevel': threat_level,
            'isSafe': False
        }
    else:
        # System is safe
        return {
            'overallStatus': 'operational',
            'services': [{
                'name': service,
                'status': 'operational',
                'uptime': random.randint(98, 100)
            } for service in services],
            'lastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'threatLevel': random.randint(0, 5),  # Very low threat level
            'isSafe': True
        }

def generate_top_ips():
    countries = ['USA', 'China', 'Russia', 'Germany', 'UK', 'Internal']
    return [
        {'ip': '192.168.1.45', 'requests': 1542, 'country': 'Internal'},
        {'ip': '203.0.113.42', 'requests': 856, 'country': 'Russia'},
        {'ip': '8.8.8.8', 'requests': 721, 'country': 'USA'},
        {'ip': '104.28.12.39', 'requests': 684, 'country': 'Germany'}
    ]

# Simulation functions
def simulation_thread(attack_type):
    while True:
        with simulation_locks[attack_type]:
            if not active_simulations[attack_type]:
                break
            
            with alert_lock:
                simulated_alerts.append(generate_attack_data(attack_type))
                # Keep only the latest 50 alerts
                if len(simulated_alerts) > 50:
                    simulated_alerts.pop(0)
        
        # Wait random time between 5-15 seconds before generating new alert
        time.sleep(random.uniform(5, 15))

# API Routes
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    with alert_lock:
        # If no simulations are active, return empty list to show system is safe
        if not any(active_simulations.values()):
            return jsonify([])
        
        # Return simulated alerts
        return jsonify(simulated_alerts)

@app.route('/api/ports', methods=['GET'])
def get_ports():
    ports = [generate_port_data() for _ in range(10)]
    return jsonify(ports)

@app.route('/api/traffic', methods=['GET'])
def get_traffic():
    time_range = request.args.get('range', '1h')
    # Adjust data based on time range
    data = generate_traffic_data()
    return jsonify(data)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Check if any simulations are active
    any_active = any(active_simulations.values())
    active_count = sum(1 for sim in active_simulations.values() if sim)
    
    if any_active:
        return jsonify({
            'activeAlerts': len(simulated_alerts),
            'protectedServers': 15,
            'networkTraffic': f"{round(random.uniform(0.5, 2.0) + (active_count * 0.5), 1)} TB",
            'activeUsers': random.randint(30, 50),
            'systemSafe': False
        })
    else:
        return jsonify({
            'activeAlerts': 0,
            'protectedServers': 15,
            'networkTraffic': f"{round(random.uniform(0.2, 0.5), 1)} TB",
            'activeUsers': random.randint(30, 50),
            'systemSafe': True
        })

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(generate_system_status())

@app.route('/api/top-ips', methods=['GET'])
def get_top_ips():
    return jsonify(generate_top_ips())

@app.route('/api/acknowledge-alert', methods=['POST'])
def acknowledge_alert():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        alert_id = data.get('id')
        if not alert_id:
            return jsonify({'success': False, 'message': 'Alert ID is required'}), 400
        
        with alert_lock:
            for alert in simulated_alerts:
                if alert['id'] == alert_id:
                    alert['isNew'] = False
                    break
            
        return jsonify({'success': True, 'message': f'Alert {alert_id} acknowledged'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/connection-status', methods=['GET'])
def connection_status():
    return jsonify({'status': 'connected', 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        attack_type = data.get('attackType')
        if not attack_type or attack_type not in active_simulations:
            return jsonify({'success': False, 'message': 'Invalid attack type'}), 400
        
        with simulation_locks[attack_type]:
            if active_simulations[attack_type]:
                return jsonify({'success': False, 'message': f'{attack_type} simulation already running'}), 400
            
            active_simulations[attack_type] = True
            thread = threading.Thread(target=simulation_thread, args=(attack_type,))
            thread.daemon = True
            thread.start()
        
        return jsonify({'success': True, 'message': f'{attack_type} simulation started'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        attack_type = data.get('attackType')
        if not attack_type or attack_type not in active_simulations:
            return jsonify({'success': False, 'message': 'Invalid attack type'}), 400
        
        with simulation_locks[attack_type]:
            if not active_simulations[attack_type]:
                return jsonify({'success': False, 'message': f'{attack_type} simulation not running'}), 400
            
            active_simulations[attack_type] = False
        
        return jsonify({'success': True, 'message': f'{attack_type} simulation stopped'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/simulation/status', methods=['GET'])
def get_simulation_status():
    return jsonify(active_simulations)

@app.route('/api/simulation/clear', methods=['POST'])
def clear_alerts():
    try:
        with alert_lock:
            simulated_alerts.clear()
        return jsonify({'success': True, 'message': 'All alerts cleared'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)