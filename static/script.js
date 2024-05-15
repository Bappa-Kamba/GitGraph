document.addEventListener('DOMContentLoaded', () => {
    const repoList = document.getElementById("repo-items");
    const visualizationContainer = document.getElementById("visualization-container"); // container for graphs

    // Fetch repositories on page load
    fetchRepositories();

    // Function to fetch and display repositories
    async function fetchRepositories(page = 1) {
        try {
            const response = await fetch(`/api/repositories?page=${page}`);
            const repositories = await response.json();

            repoList.innerHTML = ""; // Clear previous list

            repositories.forEach(repo => {
                const listItem = document.createElement('li');
                listItem.textContent = `${repo.owner}/${repo.name} - ${repo.description}`;
                listItem.dataset.repoName = repo.name;
                listItem.dataset.owner = repo.owner;
                listItem.addEventListener('click', () => fetchCommits(repo.owner, repo.name));
                repoList.appendChild(listItem);
            });
        } catch (error) {
            console.error('Error fetching repositories:', error);
            // Display an error message to the user
        }
    }

    // Function to fetch and display commits for a repository
    async function fetchCommits(owner, repo) {
        try {
            const response = await fetch(`/api/${owner}/${repo}/commits`);
            const commitData = await response.json();

            // Extract commit information (adjust based on your data structure)
            const dates = commitData[0].map(commit => commit.date);
            const commitCounts = commitData[0].map(commit => 1); // Assuming 1 commit per entry

            // Create Plotly chart data (bar chart example)
            const chartData = [{
                x: dates,
                y: commitCounts,
                type: 'bar'
            }];

            const layout = {
                title: `Commit History for ${owner}/${repo}`,
                xaxis: { title: 'Date' },
                yaxis: { title: 'Number of Commits' }
            };

            // Render Plotly chart
            Plotly.newPlot(visualizationContainer, chartData, layout);

        } catch (error) {
            console.error('Error fetching or displaying commits:', error);
            // Display an error message to the user
        }
    }
});

