from datetime import datetime, timedelta
import altair as alt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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


def calculate_pull_request_metrics(pull_requests):
    """Calculates pull request metrics and generates a histogram of time to merge.

    Args:
        pull_requests: A list of dictionaries representing pull requests.

    Returns:
        A dictionary containing the calculated metrics and histogram data.
    """

    total_created = 0
    total_merged = 0
    total_open = 0
    total_closed = 0
    time_to_merge = []

    for pr in pull_requests:
        total_created += 1
        if pr['state'] == 'closed':
            total_closed += 1
            if pr['merged_at']:
                total_merged += 1
                created_at = datetime.strptime(
                    pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                merged_at = datetime.strptime(
                    pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
                time_to_merge.append((merged_at - created_at).days)
        elif pr['state'] == 'open':
            total_open += 1

    average_time_to_merge = np.mean(time_to_merge) if time_to_merge else None

    # Create a DataFrame for the histogram data
    df = pd.DataFrame({'Time to Merge (Days)': time_to_merge})

    # Create the histogram chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Time to Merge (Days):Q', bin=True,
                title='Time to Merge (Days)'),
        y=alt.Y('count()', title='Number of Pull Requests'),
        tooltip=[alt.Tooltip('Time to Merge (Days):Q', bin=True), 'count()']
    ).properties(
        title='Distribution of Time to Merge Pull Requests'
    ).interactive()

    chart.save('time_to_merge_histogram.json')

    # # Display the histogram using matplotlib
    # plt.hist(time_to_merge, bins=10, edgecolor='black')
    # plt.xlabel('Time to Merge (Days)')
    # plt.ylabel('Number of Pull Requests')
    # plt.title('Distribution of Time to Merge Pull Requests')
    # plt.show()

    return {
        'total_created': total_created,
        'total_merged': total_merged,
        'total_open': total_open,
        'total_closed': total_closed,
        'average_time_to_merge': average_time_to_merge,
        'time_to_merge_histogram': chart.to_dict()  # Include the histogram data
    }
