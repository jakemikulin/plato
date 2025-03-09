import os
import subprocess
import time

def start_ollama():
    """Start Ollama from the local folder and use only the models in the repo."""
    try:
        # Path to local Ollama binary
        ollama_path = os.path.join(os.path.dirname(__file__), "ollama", "ollama")

        # Path to local models inside the repo
        model_path = os.path.join(os.path.dirname(__file__), "ollama", "models")

        # Set environment variable to force Ollama to use local models only
        env = os.environ.copy()
        env["OLLAMA_MODELS"] = model_path

        # Start Ollama locally
        if os.name == "nt":  # Windows
            ollama_path += ".exe"
            subprocess.Popen([ollama_path, "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # Mac/Linux
            subprocess.Popen([ollama_path, "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(2)  # Give Ollama time to start
    except Exception as e:
        print(f"Error starting Ollama: {e}")

if __name__ == "__main__":
    start_ollama()
