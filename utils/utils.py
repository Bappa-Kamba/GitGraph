from datetime import datetime, timedelta


def commits_per_day(commits):
    """Calculates commits per day from a list of commits."""
    commit_counts = {}
    for commit in commits:
        date_str = commit['date'][:10]  # Extract date (YYYY-MM-DD)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        commit_counts[date] = commit_counts.get(date, 0) + 1
    return commit_counts


def commits_per_week(commits):
    """Calculates commits per week from a list of commits."""
    commit_counts = {}
    for commit in commits:
        date_str = commit['date'][:10]
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        week_start = date - timedelta(days=date.weekday())  # Start of the week
        commit_counts[week_start] = commit_counts.get(week_start, 0) + 1
    return commit_counts


def commits_per_month(commits):
    """Calculates commits per month from a list of commits."""
    commit_counts = {}
    for commit in commits:
        date_str = commit['date'][:10]
        year, month, _ = date_str.split('-')
        month_year = f"{year}-{month}"
        commit_counts[month_year] = commit_counts.get(month_year, 0) + 1
    return commit_counts

