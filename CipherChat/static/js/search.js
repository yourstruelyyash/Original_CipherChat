document.addEventListener("DOMContentLoaded", function() {
        const searchForm = document.getElementById("searchForm");
        const searchInput = document.getElementById("searchInput");
        const searchResultsContainer = document.getElementById("search-results");

        searchForm.addEventListener("submit", function(event) {
            event.preventDefault();
            const searchTerm = searchInput.value.trim();

            // Check if search term is empty
            if (!searchTerm) {
                searchResultsContainer.textContent = "Please enter a username to search.";
                return; // Exit function early if search term is empty
            }

            fetch(`/search_users?term=${searchTerm}`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data);
                })
                .catch(error => console.error("Error searching users:", error));
        });

        function displaySearchResults(users) {
            searchResultsContainer.innerHTML = "";

            if (users && users.length > 0) {
                users.forEach(user => {
                    const userLink = document.createElement("a");
                    userLink.href = `/chat/${user}`;
                    userLink.textContent = user;

                    const br = document.createElement("br");
                    searchResultsContainer.appendChild(userLink);
                    searchResultsContainer.appendChild(br);
                });
            } else {
                searchResultsContainer.textContent = "User not found. Please try again.";
            }
        }
    });