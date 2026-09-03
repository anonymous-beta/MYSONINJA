import random
import string
import re

class Obfuscator:
    """Code obfuscation for payloads"""
    
    @staticmethod
    def random_string(length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def obfuscate_powershell(script):
        """Obfuscate PowerShell script"""
        # Variable renaming
        vars_found = set(re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', script))
        var_map = {v: f"${Obfuscator.random_string()}" for v in vars_found}
        for old, new in var_map.items():
            script = script.replace(old, new)
        
        # String splitting
        script = re.sub(r'"([^"]*)"', lambda m: '"' + ''.join([f"'{c}'" for c in m.group(1)]) + '"', script)
        
        # Add random comments
        lines = script.split('\n')
        obfuscated = []
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                obfuscated.append(line + f" # {Obfuscator.random_string(12)}")
            else:
                obfuscated.append(line)
        
        return '\n'.join(obfuscated)
    
    @staticmethod
    def obfuscate_python(code):
        """Obfuscate Python code"""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        
        # Variable renaming
        vars_found = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', code))
        var_map = {v: Obfuscator.random_string() for v in vars_found if v not in ['self', 'cls', 'def', 'class', 'return']}
        for old, new in var_map.items():
            code = re.sub(rf'\b{old}\b', new, code)
        
        # String encoding
        code = re.sub(r'"([^"]*)"', lambda m: f"'{''.join([hex(ord(c)) for c in m.group(1)])}'", code)
        
        return code
