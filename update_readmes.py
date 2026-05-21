import os
import csv
import tempfile
import requests
from github import Github

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ORG = "SFI-Visual-Intelligence"
CSV_FILENAME = os.environ.get("CSV_FILENAME", "VI_publications_for_Github.csv")
BRANCH_NAME_PREFIX = "add-paper-info"
PR_TITLE = "Prepend paper info from master publication list"
PR_BODY = "This PR prepends the paper title and link to the README, based on the VI publications list."

def extract_repo_name(code_link):
    # Handles URLs like https://github.com/owner/repo[.git]
    code_link = code_link.strip().rstrip("/")
    basename = code_link.split("/")[-1]
    return basename.replace(".git", "")

def main():
    g = Github(GITHUB_TOKEN)
    org = g.get_organization(ORG)
    # Build mapping: repo_name -> (paper_title, paper_url)
    mapping = {}
    with open(CSV_FILENAME, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_name = extract_repo_name(row["Code Link"])
            mapping[repo_name] = (row["title"], row["url"])

    repos = {repo.name: repo for repo in org.get_repos()}
    for repo_name, (title, url) in mapping.items():
        if repo_name not in repos:
            print(f"Skipping {repo_name}, repo not found in SFI-Visual-Intelligence")
            continue
        repo = repos[repo_name]
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode()
            paper_line = f'Paper: {title} ([Link]({url}))\n\n'
            if readme_content.startswith(paper_line):
                print(f"Repo {repo_name}: README already up to date.")
                continue
            new_content = paper_line + readme_content

            branch_name = f"{BRANCH_NAME_PREFIX}/{repo_name}"
            sb = repo.get_branch(repo.default_branch)
            # Create new branch
            try:
                repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=sb.commit.sha)
            except Exception as ex:
                print(f"Branch {branch_name} likely exists: {ex}")
            # Update README in branch
            repo.update_file(
                path=readme.path,
                message="Prepend paper info to README",
                content=new_content,
                sha=readme.sha,
                branch=branch_name
            )
            # Create PR (if not already open)
            pulls = list(repo.get_pulls(state="open", head=f"{ORG}:{branch_name}"))
            if not pulls:
                pr = repo.create_pull(
                    title=PR_TITLE,
                    body=PR_BODY,
                    head=branch_name,
                    base=repo.default_branch,
                )
                print(f"PR created for {repo_name}: {pr.html_url}")
            else:
                print(f"PR already exists for {repo_name}!")
        except Exception as e:
            print(f"Error processing repo {repo_name}: {e}")

if __name__ == "__main__":
    main()