document.addEventListener('DOMContentLoaded', () => {
    const repoList = document.getElementById("repository-list");
    const paginationContainer = document.getElementById("pagination-container"); // Pagination container
    const errorMessage = document.getElementById("error-message");

    // Fetch repositories on page load
    fetchRepositories();

    // Function to fetch and display repositories
    async function fetchRepositories(page = 1) {
        $('#loadingModal').modal('show');
        try {
            const apiUrl = `{{ url_for('repository.get_repositories') }}`;
            const response = await fetch(`${apiUrl}?page=${page}`);
            if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            const repositories = data.repositories;
            const totalPages = data.total_pages;

            repoList.innerHTML = "";

            repositories.forEach(repo => {
            const card = document.createElement('div');
            card.classList.add('card', 'col-md-4', 'mb-3', 'repo-card'); // Added 'repo-card' class

            // Check if language is valid and not the placeholder
            const languageIsValid = repo.language && repo.language.toLowerCase() !== "unknown language";
            
            // Truncate description if it's too long
            const maxDescriptionLength = 100; // Set your desired maximum length
            let description = repo.description || "No Descripton available."; // Handle case where description might be null
            if (description.length > maxDescriptionLength) {
                description = description.slice(0, maxDescriptionLength) + "...";
            }


            card.innerHTML = `
                <div class="card-body">
                <h5 class="card-title">
                    <a href="${repo.url}" target="_blank" class="repo-name" data-toggle="tooltip" data-placement="top" title="${repo.name}">
                        ${repo.name}
                    </a>
                </h5>
                <p class="card-text text-secondary">${description}</p>
                <div class="repo-details">
                    ${languageIsValid ? `
                        <span class="language-icon" data-toggle="tooltip" data-placement="top" title="Language">
                            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/${repo.language.toLowerCase()}/${repo.language.toLowerCase()}-original.svg" 
                                alt="${repo.language} Icon" height="16">
                        </span>
                        <span class="language" data-toggle="tooltip" data-placement="top" title="${repo.language}">${repo.language}</span> |
                    ` : ''}
                    <span class="star-icon" data-toggle="tooltip" data-placement="top" title="Stars">&#9733;</span>${repo.stargazers_count} |
                    <span class="fork-icon" data-toggle="tooltip" data-placement="top" title="Forks">&#128236;</span>${repo.forks_count} <br/>
                    <span class="last-updated text-secondary" data-toggle="tooltip" data-placement="top" title="Last Updated">Updated on ${new Date(repo.updated_at).toLocaleDateString()}</span>
                </div>
            </div>
            `;

            card.dataset.repoName = repo.name;
            card.dataset.owner = repo.owner;
            card.addEventListener('click', () => fetchAndDisplayRepoData(repo.owner, repo.name));
            repoList.appendChild(card);
            });
            renderPagination(page, totalPages);
        } catch (error) {
            console.log(error)
            errorMessage.textContent = `Error fetching repositories: ${error.message}`;
            errorMessage.style.display = 'block';
        } finally {
            $('#loadingModal').modal('hide');
        }
        }

  
    // Function to fetch and display commits, branches and contributors for a repository
    async function fetchAndDisplayRepoData(owner, repo) {
        $('#commitloadingModal').modal('show');
        try {
            const apiUrl = `{{ url_for('repository.get_commits', owner=owner, repo=repo) }}`;
            const commitsResponse = await fetch(`${apiUrl}`);
            // const branchesResponse = await fetch(`/api/${owner}/${repo}/branches`);
            // const contributorsResponse = await fetch(`/api/${owner}/${repo}/contributors`);

            const commitData = await commitsResponse.json();
            // const branchData = await branchesResponse.json();
            // const contributorData = await contributorsResponse.json();
            //Extract the necessary information from the responses to be used to render the charts

            renderRepositoryOverview(repo, commitData);
            // renderBranchNetwork(branchData);
            // renderContributorActivity(contributorData);

        } catch (error) {
            errorMessage.textContent = `Error fetching or displaying repository data: ${error.message}`;
            errorMessage.style.display = 'block';
        } finally {
            $('#commitloadingModal').modal('hide');
        }
    }

    function renderRepositoryOverview(repo, commitData) {
        const commitsByDay = commitData.commits_by_day;
        const dailyData = {
            x: Object.keys(commitsByDay).map(dateStr => new Date(dateStr)), 
            y: Object.values(commitsByDay), 
            type: 'bar',
            marker: {
                color: '#2ca02c' // GitHub green
            },
            showscale: true,
            hovertemplate: '%{y} commits on %{x}'
        };

        const layout = {
            title: `Commits Over Time for ${repo}`,
            height: 400, // Adjust height as needed
            xaxis: { 
                title: 'Date', 
                type: 'date', 
            }, 
            yaxis: {
                title: 'Number of Commits' 
            },
        };

        Plotly.newPlot('repositoryOverviewChart', [dailyData], layout); 

        // Add click event listener to the chart
        repositoryOverviewChart.on('plotly_click', function(data) {
            let pts = '';
            for(let i=0; i < data.points.length; i++){
                pts = data.points[i];
                let date = pts.x;

                // Filter commits for the clicked date
                const commitsOnThisDay = commitData.commit_details.filter(
                    (commit) => {
                        // Convert Plotly's date (a JavaScript Date object) to a string in the YYYY-MM-DD format
                        const clickedDate = new Date(date).toISOString().slice(0, 10);
                        return commit.date === clickedDate;
                    });
                
                // Update commit details container
                const commitDetailsContainer = document.getElementById('commit-details');
                commitDetailsContainer.innerHTML = `<h3>Commits on ${date} for ${repo}:</h3>`;

                if (commitsOnThisDay.length > 0) {
                    const commitList = document.createElement('ul');
                    commitsOnThisDay.forEach(commit => {
                        const listItem = document.createElement('li');
                        listItem.innerHTML = `<b>${commit.author}</b>: <a href="${commit.url}" target="_blank">${commit.message}</a>`;
                        commitList.appendChild(listItem);
                    });
                    commitDetailsContainer.appendChild(commitList);
                } else {
                    commitDetailsContainer.innerHTML += '<p>No commits found for this date.</p>';
                }
            }
        });

        // Display highest and lowest commit days (for daily commits only)
        const dates = Object.keys(commitsByDay);
        const commitCounts = Object.values(commitsByDay);

        const highestCommitDay = dates[commitCounts.indexOf(Math.max(...commitCounts))];
        const lowestCommitDay = dates[commitCounts.indexOf(Math.min(...commitCounts))];

        const summaryText = `Highest: ${highestCommitDay} (${Math.max(...commitCounts)} commits)`;
        document.getElementById('commit-summary').textContent = summaryText; 
    }

    // Function to render pagination links
    function renderPagination(currentPage, totalPages) {
        paginationContainer.innerHTML = ''; // Clear existing pagination

        const ul = document.createElement('ul');
        ul.classList.add('pagination', 'justify-content-center');

        // Previous button
        if (currentPage > 1) {
            const prevLink = document.createElement('a');
            prevLink.classList.add('page-link');
            prevLink.href = `/api/repositories?page=${currentPage - 1}`;
            prevLink.textContent = 'Previous';
            prevLink.addEventListener('click', (event) => {
                event.preventDefault();
                fetchRepositories(currentPage - 1); // Fetch previous page's data
            });
            const prevLi = document.createElement('li');
            prevLi.classList.add('page-item');
            prevLi.appendChild(prevLink);
            ul.appendChild(prevLi);
        }

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.classList.add('page-item', i === currentPage ? 'active' : 'inactive');

            const pageLink = document.createElement('a'); 
            pageLink.classList.add('page-link');
            pageLink.href = `/api/repositories?page=${i}`;
            pageLink.textContent = i;
            pageLink.addEventListener('click', (event) => {
            event.preventDefault();
            fetchRepositories(i); // Fetch the selected page's data
            });

            li.appendChild(pageLink);
            ul.appendChild(li);
        }

        // Next button
        if (currentPage < totalPages) {
            const nextLink = document.createElement('a');
            nextLink.classList.add('page-link');
            nextLink.href = `/api/repositories?page=${currentPage + 1}`;
            nextLink.textContent = 'Next';
            nextLink.addEventListener('click', (event) => {
            event.preventDefault();
            fetchRepositories(currentPage + 1); // Fetch next page's data
            });
            const nextLi = document.createElement('li');
            nextLi.classList.add('page-item');
            nextLi.appendChild(nextLink);
            ul.appendChild(nextLi);
        }

        paginationContainer.appendChild(ul);
        }


});
