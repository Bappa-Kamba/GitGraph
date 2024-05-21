document.addEventListener('DOMContentLoaded', () => {
    const repoList = document.getElementById("repo-items");
    
    const errorMessage = document.getElementById("error-message");

    // Fetch repositories on page load
    fetchRepositories();

    // Function to fetch and display repositories
    async function fetchRepositories(page=1) {
        try {
            const response = await fetch(`/api/repositories?page=${page}`);
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            const repositories = await response.json();

            repoList.innerHTML = "";
            
            repositories.forEach(repo => {
                const listItem = document.createElement('li');
                listItem.textContent = `${repo.owner}/${repo.name} - ${repo.description}`;
                listItem.dataset.repoName = repo.name;
                listItem.dataset.owner = repo.owner;
                listItem.addEventListener('click', () => fetchAndDisplayRepoData(repo.owner, repo.name));
                repoList.appendChild(listItem);
            });

        } catch (error) {
            errorMessage.textContent = `Error fetching repositories: ${error.message}`;
            errorMessage.style.display = 'block';
        }
    }
  
    // Function to fetch and display commits, branches and contributors for a repository
    async function fetchAndDisplayRepoData(owner, repo) {
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
        }
    }


});
