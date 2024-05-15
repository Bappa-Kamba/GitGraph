# repository_routes.py

from flask import Blueprint, jsonify, g, request
from utils.utils import commits_per_day, commits_per_week, commits_per_month, calculate_pull_request_metrics
import requests
from config import GITHUB_ACCESS_TOKEN
from routes.auth_routes import auth_required

repository_bp = Blueprint('repository', __name__,
                          url_prefix='/api')


@repository_bp.route('/repositories')
@auth_required
def get_repositories():
    """
    Fetches the repositories of the authenticated user.
    """
    # Ensure user is logged in via GitHub OAuth
    if g.user is None:
        return jsonify({"error": "Not logged in"}), 401  # Unauthorized

    access_token = GITHUB_ACCESS_TOKEN

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

    # Calculate skip and limit for pagination.
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    skip = (page - 1) * per_page

    all_repos = []
    all_repos_count = 0
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

    all_repos_count = len(all_repos)

    repositories = []
    for repo in all_repos[skip:skip+per_page]:
        repository_data = {
            "name": repo['name'],
            "owner": repo['owner']['login'],
            "description": repo['description'],
            "url": repo['html_url'],
            "updated_at": repo["updated_at"]
        }
        repositories.append(repository_data)
    return jsonify(repositories), 200


@repository_bp.route('/<owner>/<repo>/commits', methods=['GET'])
@auth_required
def get_commits(owner='Bappa-Kamba', repo='Github-Visualizer'):
    """
    Fetches commits for a specific repository.
    """
    if g.user is None:
        return jsonify({"error": "Not logged in"}), 401  # Unauthorized

    access_token = GITHUB_ACCESS_TOKEN

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

    commits_by_day = {date_obj.isoformat(): count for date_obj,
                      count in commits_per_day(commits_data).items()}
    commits_by_week = {date_obj.isoformat(): count for date_obj,
                       count in commits_per_week(commits_data).items()}
    commits_by_month = {month_year: count for month_year,
                        count in commits_per_month(commits_data).items()}

    return jsonify([
        all_commits,
        commits_data,
        {
            "commits_by_day": commits_by_day,
            "commits_by_week": commits_by_week,
            "commits_by_month": commits_by_month,
        }
    ]), 200


@repository_bp.route('/pulls', methods=['GET'])
@auth_required
def get_pull_requests(owner='Gomerce', repo='GomerceBE'):
    # Ensure user is logged in via GitHub OAuth
    if g.user is None:
        return jsonify({"error": "Not logged in"}), 401  # Unauthorized

    access_token = GITHUB_ACCESS_TOKEN

    headers = {
        # Use "Bearer" with OAuth tokens
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    all_pulls = []
    page = 1
    while True:
        try:
            response = requests.get(
                f'https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=100&page={page}',
                headers=headers
            )
            response.raise_for_status()
            pulls = response.json()
            all_pulls.extend(pulls)
            # Check if no repositories were returned (end of pagination)
            if not pulls:
                break
            if len(pulls) < 100:
                break
        except requests.exceptions.RequestException as e:
            from app import app
            app.logger.error(f"Error fetching pull requests: {e}")
            return jsonify({"error": "Failed to fetch pull requests from GitHub"}), 500

        page += 1

    pull_request_data = []

    # Fetch additional details for each pull request
    for pull in all_pulls:
        try:
            response = requests.get(pull['url'], headers=headers)
            response.raise_for_status()
            pull_details = response.json()
            pull_request_data.append({
                "number": pull_details['number'],
                "title": pull_details['title'],
                "state": pull_details['state'],
                "created_at": pull_details['created_at'],
                "merged_at": pull_details['merged_at'],
                "closed_at": pull_details['closed_at'],
                # Handle the case where additions/deletions are not present
                "additions": pull_details.get('additions', 0),
                "deletions": pull_details.get('deletions', 0),
                "user": pull_details['user']['login']
            })
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error fetching pull request details: {e}")
            return jsonify({"error": "Failed to fetch pull request details"}), 500
        
        metrics = calculate_pull_request_metrics(pull_request_data)

    return jsonify({
        "pull_requests": all_pulls,
        "pull_request_data": pull_request_data,
        "metrics": metrics
    }), 200
