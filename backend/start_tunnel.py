import os
import subprocess
import time

def start_tunnel():
    """Starts Cloudflare Tunnel to expose local server to the internet."""
    print("[CLOUD] Starting Cloudflare Tunnel...")
    try:
        # This will create a temporary public URL for port 8000
        # Command: cloudflared tunnel --url http://localhost:8000
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", "http://localhost:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Monitor the output for the URL
        for line in process.stdout:
            print(line.strip())
            if "trycloudflare.com" in line:
                print(f"\n[GLOBAL ACCESS] Bhai, URL mil gaya! Dost ko ye bhejo: {line.strip()}")
                break
    except FileNotFoundError:
        print("[ERROR] cloudflared not found. Please install it first: 'npm install -g @cloudflare/cloudflared'")

if __name__ == "__main__":
    start_tunnel()
