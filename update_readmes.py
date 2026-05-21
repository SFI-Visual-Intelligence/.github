import os
from github import Github

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ORG = "SFI-Visual-Intelligence"
BRANCH_PREFIX = "add-paper-info"

def main():
    g = Github(GITHUB_TOKEN)
    org = g.get_organization(ORG)

    for repo in org.get_repos():
        repo_name = repo.name
        branch_name = f"{BRANCH_PREFIX}/{repo_name}"
        ref_name = f"heads/{branch_name}"
        try:
            # Try to get the ref; if it exists, delete
            ref = repo.get_git_ref(ref_name)
            ref.delete()
            print(f"Deleted branch {branch_name} in repo {repo_name}")
        except Exception as e:
            # Will error if ref does not exist
            print(f"Branch {branch_name} does not exist in repo {repo_name}, skipping.")

if __name__ == "__main__":
    main()
