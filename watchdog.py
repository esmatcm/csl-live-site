import subprocess
import time
import sys
import os
from datetime import datetime

# Configuration
SCRIPT_TO_RUN = "csl-live-site/daemon_v54_1.py"
RESTART_DELAY = 5  # Seconds to wait before restarting

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [WATCHDOG] {msg}")
    sys.stdout.flush()

def run_forever():
    log(f"Starting watchdog for {SCRIPT_TO_RUN}...")
    
    while True:
        try:
            # Start the process
            log("Launching daemon...")
            # Use same python executable as current process
            cmd = [sys.executable, SCRIPT_TO_RUN]
            
            process = subprocess.Popen(cmd)
            log(f"Daemon started with PID: {process.pid}")
            
            # Wait for it to finish (it shouldn't, unless it crashes)
            exit_code = process.wait()
            
            log(f"Daemon crashed/exited with code: {exit_code}")
            log(f"Restarting in {RESTART_DELAY} seconds...")
            time.sleep(RESTART_DELAY)
            
        except KeyboardInterrupt:
            log("Watchdog stopped by user.")
            if process: process.kill()
            break
        except Exception as e:
            log(f"Watchdog error: {e}")
            time.sleep(RESTART_DELAY)

if __name__ == "__main__":
    run_forever()
