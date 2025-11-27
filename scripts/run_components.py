"""
Run component/unit tests and perform basic checks
"""
import subprocess
import sys

def run_tests():
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "-q"]) 
        print("All pytest tests passed")
    except subprocess.CalledProcessError as e:
        print("Tests failed", e)
        raise

if __name__ == '__main__':
    run_tests()
