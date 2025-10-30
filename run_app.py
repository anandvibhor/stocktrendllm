# run_app.py
import subprocess
import sys

def main():
    """Run the Streamlit app"""
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()