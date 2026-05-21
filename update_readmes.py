import os
import csv
from github import Github

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ORG = "SFI-Visual-Intelligence"
CSV_FILENAME = os.environ.get("CSV_FILENAME", "VI_publications_for_Github.csv")
COMMIT_MESSAGE = "Prepend paper info from master publication list to README"

def extract_repo_name(code_link):
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
            default_branch = repo.default_branch
            readme = repo.get_readme(ref=default_branch)
            readme_content = readme.decoded_content.decode()
            paper_line = f'Paper: {title} ([Link]({url}))\n\n'
            if readme_content.startswith(paper_line):
                print(f"Repo {repo_name}: README already up to date.")
                continue
            new_content = paper_line + readme_content

            # Commit directly to the default branch
            repo.update_file(
                path=readme.path,
                message=COMMIT_MESSAGE,
                content=new_content,
                sha=readme.sha,
                branch=default_branch
            )
            print(f"Repo {repo_name}: README updated and committed to {default_branch}.")
        except Exception as e:
            print(f"Error processing repo {repo_name}: {e}")

if __name__ == "__main__":
    main()
