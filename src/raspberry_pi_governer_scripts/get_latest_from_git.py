from pathlib import Path

import requests
from ..utils import run_bash, setup_logs

SCRIPT_PATH_GET_LATEST_COMMIT = "scripts/get_last_commit.sh"
SCRIPT_PATH_GET_REPO_DETAILS = "scripts/get_repo_details.sh"
SCRIPT_PATH_GIT_PULL_LATEST = "scripts/git_pull_latest.sh"
SCRIPT_PATH_ADD_ALIAS = "scripts/python_entrypoint_get_latest_from_git.sh"


def get_latest_remote_commit_id(owner, name, branch='main'):
    url = f'https://api.github.com/repos/{owner}/{name}/commits/{branch}'
    response = requests.get(url)
    response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
    commit_data = response.json()
    return commit_data['sha']


def check_for_new_commit():
    # Get the latest local commit ID
    success, latest_commit_id = run_bash(SCRIPT_PATH_GET_LATEST_COMMIT)
    if not success:
        print(f"Failed to get the latest local commit ID: {latest_commit_id}")
        return

    # Get repository details
    success, repo_details = run_bash(SCRIPT_PATH_GET_REPO_DETAILS)
    if success and repo_details:
        owner, name = repo_details.split('/')

        try:
            # Make a request to the GitHub API
            latest_remote_commit_id = get_latest_remote_commit_id(owner, name)
            print(f"Latest remote commit ID: {latest_remote_commit_id}")

            # Compare the latest local and remote commit IDs
            if latest_commit_id != latest_remote_commit_id:
                print("New commit detected in the main branch. Pulling latest changes.")
                success, pull_output = run_bash(SCRIPT_PATH_GIT_PULL_LATEST)
                if not success:
                    print(f"Failed to pull latest changes: {pull_output}")
            else:
                print("Local repository is up-to-date with the main branch.")
        except requests.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Failed to retrieve repository details.")


def add_alias_for_script():
    success, output = run_bash(SCRIPT_PATH_ADD_ALIAS)
    if not success:
        print(f"Failed to add alias: {output}")


def main():
    setup_logs(Path(__file__).name)
    check_for_new_commit()
    add_alias_for_script()


if __name__ == "__main__":
    main()

