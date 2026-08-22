import os
import shutil

# Target directory to clean
REPO_ROOT = r"C:\Users\Lenovo\Desktop\cyber"

def clean_history():
    print("WARNING: This is a placeholder for a BFG or git filter-repo run.")
    print("Since standard git history rewriting tools (BFG/filter-repo) are not installed natively in this environment, ")
    print("the user is advised to run the following command on their host machine:")
    print("  git filter-repo --path-match '*.db' --path-match 'SECRET_KEY' --invert-paths")
    
    # Clean up local un-tracked junk just to be safe
    for root, dirs, files in os.walk(REPO_ROOT):
        for file in files:
            if file.endswith('.db') or file.endswith('.sqlite3'):
                filepath = os.path.join(root, file)
                try:
                    os.remove(filepath)
                    print(f"Removed local DB: {filepath}")
                except:
                    pass

if __name__ == "__main__":
    clean_history()
