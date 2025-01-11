import subprocess

def list_commits():
    try:
        result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, check=True)
        print("Recent Commits:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running git log: {e.stderr}")

if __name__ == "__main__":
    list_commits()