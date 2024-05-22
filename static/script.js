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
            const response = await fetch(`/api/repositories?page=${page}`);
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
        $('#loadingModal').modal('show');
        try {
            const commitsResponse = await fetch(`/api/${owner}/${repo}/commits`);
            // const branchesResponse = await fetch(`/api/${owner}/${repo}/branches`);
            // const contributorsResponse = await fetch(`/api/${owner}/${repo}/contributors`);

            const commitData = await commitsResponse.json();
            console.log(commitData)
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
            $('#loadingModal').modal('hide');
        }
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
