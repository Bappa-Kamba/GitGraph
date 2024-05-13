# repository_routes.py

from flask import Blueprint, jsonify, session, g, request
import requests
from routes.auth_routes import auth_required

repository_bp = Blueprint('repository', __name__,
                          url_prefix='/api/repositories')


@repository_bp.route('/')
@auth_required
def get_repositories():
    """
    Fetches the repositories of the authenticated user.
    """
    # Ensure user is logged in via GitHub OAuth
    if g.user is None:
        return jsonify({"error": "Not logged in"}), 401  # Unauthorized

    access_token = ''

    headers = {
        # Use "Bearer" with OAuth tokens
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {
        "visibility": "all",
        "affiliation": "owner,collaborator,organization_member",
        "per_page": 100
    }

    all_repos = []
    page = 1
    while True:
        params["page"] = page
        try:
            response = requests.get(
                'https://api.github.com/user/repos', headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for bad responses
            repos = response.json()
            all_repos.extend(repos)

            # Check if no repositories were returned (end of pagination)
            if not repos:
                break
            if len(repos) < 100:
                break
        except requests.exceptions.RequestException as e:
            from app import app
            app.logger.error(f"Error fetching repositories from GitHub: {e}")
            return jsonify({"error": "Failed to fetch repositories from GitHub"}), 500

        page += 1

    # Extract necessary data and return as JSON
    repositories = [
        {
            "name": repo['name'],
            "owner": repo['owner']['login'],
            "description": repo['description'],
            "url": repo['html_url'],
            "updated_at": repo["updated_at"]
        }
        for repo in all_repos
    ]

    return jsonify(repositories), 200


@repository_bp.route('/<owner>/<repo>/commits', methods=['GET'])
@auth_required
def get_commits(owner='Bappa-Kamba', repo='Github-Visualizer'):
    """
    Fetches commits for a specific repository.
    """
    if g.user is None:
        return jsonify({"error": "Not logged in"}), 401  # Unauthorized

    access_token = session['github_token']

    # Date Filtering (Optional)
    since = request.args.get('since')
    until = request.args.get('until')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {
        'per_page': 100  # Fetch up to 100 commits per page
    }
    if since:
        params['since'] = since
    if until:
        params['until'] = until

    all_commits = []
    page = 1
    while True:
        params["page"] = page
        try:
            response = requests.get(
                f'https://api.github.com/repos/{owner}/{repo}/commits', headers=headers, params=params)
            response.raise_for_status()

            commits = response.json()
            all_commits.extend(commits)

            if not commits:
                break
            if len(commits) < 100:
                break
        except requests.exceptions.RequestException as e:
            from app import app
            app.logger.error(f"Error fetching commits: {e}")
            return jsonify({"error": "Failed to fetch commits from GitHub"}), response.status_code

        page += 1

    # ... (Error handling for API rate limits or other issues) ...

    # Extract and process the data (author, date, message, additions, deletions, etc.)
    commits_data = []
    for commit in all_commits:
        commit_data = {
            "sha": commit['sha'],
            "author": commit['commit']['author']['name'],
            "date": commit['commit']['author']['date'],
            "message": commit['commit']['message'],
            # ... (extract other relevant data as needed)
        }
        commits_data.append(commit_data)

    return jsonify(commits_data), 200
