"""
DelayRay Development Runner
Starts FastAPI backend and Vite frontend concurrently.
"""

import subprocess
import sys
import os
import signal
import time

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    frontend_cmd = ["npm", "run", "dev"]

    print("==================================================")
    print("   Starting DelayRay Local Development Stack")
    print("   API:      http://localhost:8000")
    print("   Health:   http://localhost:8000/health")
    print("   Docs:     http://localhost:8000/docs")
    print("   Frontend: http://localhost:5173")
    print("==================================================")

    env = os.environ.copy()
    backend_proc = subprocess.Popen(backend_cmd, cwd=root_dir, env=env)
    
    # Run npm run dev in frontend dir
    frontend_dir = os.path.join(root_dir, "frontend")
    shell_val = True if sys.platform == "win32" else False
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=shell_val, env=env)

    def shutdown(sig, frame):
        print("\nShutting down DelayRay development processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend exited unexpectedly.")
                break
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
