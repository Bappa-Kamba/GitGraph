# repository_routes.py

from flask import Blueprint, jsonify, g, request, session
from utils.utils import commits_per_day, commits_per_week, commits_per_month, calculate_pull_request_metrics
import requests
from routes.auth_routes import auth_required

repository_bp = Blueprint('repository', __name__,
                          url_prefix='/api')


@repository_bp.route('/repositories')
@auth_required
def get_repositories():
    """
    Fetches the repositories of the authenticated user.
    """
    access_token = session['github_token']

    headers = {
        # Use "Bearer" with OAuth tokens
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {
        "visibility": "all",
        "affiliation": "owner,collaborator,organization_member",
        "per_page": 100  # Fetch 100 repos per page (max allowed)
    }

    all_repos = []
    page = 1
    while True:
        params["page"] = page
        try:
            response = requests.get(
                'https://api.github.com/user/repos', headers=headers, params=params)
            response.raise_for_status()
            repos = response.json()
            all_repos.extend(repos)

            # Check for end of pagination or rate limit
            if not repos or response.status_code == 403:  # Check for rate limit
                break

        except requests.exceptions.RequestException as e:
            from app import app
            error_msg = f"Error fetching repositories from GitHub: {e}"
            if response:
                error_msg += f" (Status code: {response.status_code}, Message: {response.text})"
            app.logger.error(error_msg)
            return jsonify({"error": error_msg}), 500  # More specific error

        page += 1
        
    total_repos = len(all_repos)
    per_page = int(request.args.get('per_page', 10))
    # Calculate total pages
    total_pages = (total_repos + per_page - 1) // per_page

    # Extract relevant data for the current page
    page = int(request.args.get('page', 1))
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    repositories = [{
        "name": repo['name'],
        "owner": repo['owner']['login'],
        "description": repo['description'],
        "url": repo['html_url'],
        "updated_at": repo["updated_at"],
        # Handle case where language is None
        "language": repo.get("language"),
        "language_color": repo.get("language_color", "Unknown"),
        "stargazers_count": repo.get("stargazers_count", 0),
        "forks_count": repo.get("forks_count", 0)
    } for repo in all_repos[start_index:end_index]]

    return jsonify({
        'repositories': repositories,
        'total_pages': total_pages
    }), 200


@repository_bp.route('/<owner>/<repo>/commits', methods=['GET'])
@auth_required
def get_commits(owner='Bappa-Kamba', repo='Github-Visualizer'):
    """
    Fetches commits for a specific repository.
    """    
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
    access_token = session['github_token']

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
