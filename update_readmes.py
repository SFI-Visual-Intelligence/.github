import os
from github import Github

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ORG = "SFI-Visual-Intelligence"

def extract_paper_title(readme_first_line):
    # Parses 'Paper: <paper name> ([Link](...))'
    if readme_first_line.startswith("Paper: "):
        main = readme_first_line[len("Paper: "):].strip()
        # Paper name could end before the first " ([" if present
        bracket = main.find("([Link]")
        if bracket > 0:
            return main[:bracket].strip()
        # More robust: ends before '([' even if there's content after
        sep = main.find("([")
        if sep > 0:
            return main[:sep].strip()
        # Else, whole remainder is name
        return main
    return None

def main():
    g = Github(GITHUB_TOKEN)
    org = g.get_organization(ORG)

    for repo in org.get_repos():
        try:
            readme = repo.get_readme(ref=repo.default_branch)
            readme_content = readme.decoded_content.decode("utf-8")
            first_line = readme_content.splitlines()[0].strip()
            if first_line.startswith("Paper: "):
                paper_title = extract_paper_title(first_line)
                if paper_title:
                    if repo.description != paper_title:
                        repo.edit(description=paper_title)
                        print(f"Updated description for {repo.name}: '{paper_title}'")
                    else:
                        print(f"{repo.name}: description already correct.")
                else:
                    print(f"{repo.name}: Could not extract title from line: {first_line}")
            else:
                print(f"{repo.name}: README does not start with paper info, skipped.")
        except Exception as e:
            print(f"{repo.name}: error {e}")

if __name__ == "__main__":
    main()
