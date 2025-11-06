// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // Backend API URL
const LOCAL_RECIPES_PATH = 'data/recipes_with_local_images.json'; // Fallback

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const searchResultsDropdown = document.getElementById('searchResults');
const recipesContainer = document.getElementById('recipesContainer');
const filterBtns = document.querySelectorAll('.filter-btn');
let searchTypeRadios = null;

// State
let currentFilter = 'all';
let allRecipes = [];
let filteredRecipes = [];
let currentPage = 1;
const recipesPerPage = 12;
let searchTimeout = null;
let apiService = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    apiService = new ApiService(API_BASE_URL);
    searchTypeRadios = document.querySelectorAll('input[name="searchType"]');
    loadLocalRecipes();
    setupEventListeners();
    loadRecipeOfTheDay();
});

// Setup Event Listeners
function setupEventListeners() {
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length >= 2) {
            searchTimeout = setTimeout(() => {
                handleSearchSuggestions(query);
            }, 300);
        } else {
            hideSearchResults();
        }
    });

    document.addEventListener('click', (e) => {
        if (!searchResultsDropdown.contains(e.target) && 
            !searchInput.contains(e.target) && 
            !searchBtn.contains(e.target)) {
            hideSearchResults();
        }
    });

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.textContent;
            filterRecipesByCategory(currentFilter);
            hideSearchResults();
        });
    });

    if (searchTypeRadios) {
        searchTypeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const placeholder = e.target.value === 'name' 
                    ? 'What do you want to cook today?' 
                    : 'Enter ingredients (comma separated)';
                searchInput.placeholder = placeholder;
                hideSearchResults();
            });
        });
    }
}

// Load Recipes from Backend API
async function loadLocalRecipes() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/recipes`);

        if (!response.ok) {
            throw new Error('Unable to load recipe data from server');
        }

        allRecipes = await response.json();
        filteredRecipes = [...allRecipes];
        console.log(`Loaded ${allRecipes.length} recipes from API`);
        displayRecipesWithPagination();

        // Fill other sections with data
        await fillPopularRecipes();
    } catch (error) {
        console.error('Load recipes error:', error);
        // Fallback to local JSON if API fails
        try {
            const fallbackResponse = await fetch(LOCAL_RECIPES_PATH);
            if (fallbackResponse.ok) {
                allRecipes = await fallbackResponse.json();
                filteredRecipes = [...allRecipes];
                console.log(`Loaded ${allRecipes.length} recipes from fallback`);
                displayRecipesWithPagination();
                await fillPopularRecipes();
            } else {
                throw new Error('Fallback also failed');
            }
        } catch (fallbackError) {
            console.error('Fallback error:', fallbackError);
            displaySampleRecipes();
        }
    } finally {
        hideLoading();
    }
}

// Load Recipe of The Day (Random)
async function loadRecipeOfTheDay() {
    try {
        const response = await fetch(`${API_BASE_URL}/recipes?limit=100`);
        if (!response.ok) {
            throw new Error('Unable to load recipes');
        }

        const recipes = await response.json();
        if (recipes.length > 0) {
            // Get random recipe
            const randomRecipe = recipes[Math.floor(Math.random() * recipes.length)];
            displayRecipeOfTheDay(randomRecipe);
        }
    } catch (error) {
        console.error('Load recipe of the day error:', error);
        // Keep default content if fails
    }
}

// Display Recipe of The Day
function displayRecipeOfTheDay(recipe) {
    const imageElement = document.getElementById('recipeOfDayImage');
    const titleElement = document.getElementById('recipeOfDayTitle');
    const authorElement = document.getElementById('recipeOfDayAuthor');
    const descriptionElement = document.getElementById('recipeOfDayDescription');

    if (imageElement) {
        imageElement.src = recipe.image || 'assets/images/recipe-of-the-day.png';
        imageElement.alt = recipe.title;
        imageElement.onclick = () => viewRecipe(recipe.id);
        imageElement.style.cursor = 'pointer';
    }

    if (titleElement) {
        titleElement.textContent = recipe.title;
        titleElement.onclick = () => viewRecipe(recipe.id);
        titleElement.style.cursor = 'pointer';
    }

    if (authorElement) {
        authorElement.textContent = `By ${recipe.area} Chef`;
    }

    if (descriptionElement) {
        const description = recipe.instructions 
            ? recipe.instructions.substring(0, 200) + '...'
            : 'Delicious recipe. Click to view more details.';
        descriptionElement.textContent = description;
    }
}

// Fill Popular Recipes Section using Backend API
async function fillPopularRecipes() {
    const containers = document.querySelectorAll('.section-title-wrapper .recipes-slider');
    if (containers.length < 1) return;

    try {
        // Try to get popular recipes from backend API
        const response = await fetch(`${API_BASE_URL}/popular?limit=4`);

        if (response.ok) {
            const popular = await response.json();
            const popularContainer = containers[0];
            popularContainer.innerHTML = popular.map(recipe => createSmallRecipeCard(recipe)).join('');
            return;
        }
    } catch (error) {
        console.log('Popular API not available, using fallback:', error);
    }

    // Fallback: Take recipes with longer instructions as "popular"
    const popularContainer = containers[0];
    const popular = [...allRecipes]
        .sort((a, b) => (b.instructions?.length || 0) - (a.instructions?.length || 0))
        .slice(0, 4);
    popularContainer.innerHTML = popular.map(recipe => createSmallRecipeCard(recipe)).join('');
}

// Create Small Recipe Card for sliders and grids
function createSmallRecipeCard(recipe) {
    const estimatedTime = recipe.instructions 
        ? Math.max(15, Math.min(90, Math.floor(recipe.instructions.length / 12)))
        : 30;
    
    let difficulty = 'easy';
    if (recipe.instructions) {
        const len = recipe.instructions.length;
        if (len > 500) difficulty = 'hard';
        else if (len > 250) difficulty = 'medium';
    }
    
    const description = recipe.instructions 
        ? recipe.instructions.substring(0, 100) + '...' 
        : 'Delicious and easy to make.';
    
    const imageUrl = recipe.image || 'assets/images/thai-green-curry.png';
    
    return `
        <div class="recipe-card" onclick="viewRecipe('${recipe.id}')">
            <img src="${imageUrl}" 
                 alt="${recipe.title}"
                 loading="lazy" />
            <span class="difficulty-badge ${difficulty}">${difficulty}</span>
            <div class="recipe-info">
                <span class="recipe-time">${estimatedTime} mins</span>
                <h3>${recipe.title}</h3>
                <p class="recipe-author">By ${recipe.area} Chef</p>
                <p class="recipe-desc">${description}</p>
            </div>
        </div>
    `;
}

// Handle Search Suggestions (Real-time dropdown)
async function handleSearchSuggestions(query) {
    try {
        showSearchLoading();

        const searchType = document.querySelector('input[name="searchType"]:checked')?.value || 'name';

        if (searchType === 'ingredient') {
            const ingredients = query.split(',').map(ing => ing.trim()).filter(ing => ing);
            if (ingredients.length === 0) {
                hideSearchResults();
                return;
            }

            const result = await apiService.searchByIngredients(ingredients);
            if (result.success) {
                displaySearchResults(result.data);
            } else {
                hideSearchResults();
            }
        } else {
            const searchResponse = await fetch(`${API_BASE_URL}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    top_k: 10
                })
            });

            if (!searchResponse.ok) {
                throw new Error('Search request failed');
            }

            const searchResults = await searchResponse.json();
            displaySearchResults(searchResults);
        }
    } catch (error) {
        console.error('Search suggestions error:', error);
        hideSearchResults();
    }
}

// Display Search Results in Dropdown
function displaySearchResults(results) {
    if (results.length === 0) {
        searchResultsDropdown.innerHTML = '<div class="search-no-results">No results found</div>';
        searchResultsDropdown.classList.add('show');
        return;
    }

    const query = searchInput.value.trim();
    const resultsHTML = results.map(result => `
        <div class="search-result-item" onclick="viewRecipeWithQuery('${result.id}', '${encodeURIComponent(query)}')">
            <img src="${result.image || 'assets/images/thai-green-curry.png'}" 
                 alt="${result.title}" 
                 class="search-result-image" />
            <div class="search-result-info">
                <h4 class="search-result-title">${result.title}</h4>
                <p class="search-result-meta">${result.category} • ${result.area}</p>
                <p class="search-result-score">Match: ${(result.score * 100).toFixed(0)}%</p>
            </div>
        </div>
    `).join('');

    searchResultsDropdown.innerHTML = resultsHTML;
    searchResultsDropdown.classList.add('show');
}

// Show Search Loading
function showSearchLoading() {
    searchResultsDropdown.innerHTML = '<div class="search-loading">Searching...</div>';
    searchResultsDropdown.classList.add('show');
}

// Hide Search Results
function hideSearchResults() {
    searchResultsDropdown.classList.remove('show');
    searchResultsDropdown.innerHTML = '';
}

// Handle Search using Backend API
async function handleSearch() {
    const query = searchInput.value.trim();

    if (query === '') {
        hideSearchResults();
        return;
    }

    try {
        showSearchLoading();

        const searchType = document.querySelector('input[name="searchType"]:checked')?.value || 'name';

        if (searchType === 'ingredient') {
            const ingredients = query.split(',').map(ing => ing.trim()).filter(ing => ing);
            if (ingredients.length === 0) {
                searchResultsDropdown.innerHTML = '<div class="search-no-results">Please enter at least one ingredient</div>';
                searchResultsDropdown.classList.add('show');
                return;
            }

            const result = await apiService.searchByIngredients(ingredients);
            if (result.success) {
                displaySearchResults(result.data);
                if (result.data.length === 0) {
                    searchResultsDropdown.innerHTML = '<div class="search-no-results">No recipes found with these ingredients</div>';
                    searchResultsDropdown.classList.add('show');
                }
            } else {
                searchResultsDropdown.innerHTML = '<div class="search-no-results">Search error. Please try again.</div>';
                searchResultsDropdown.classList.add('show');
            }
        } else {
            const searchResponse = await fetch(`${API_BASE_URL}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    top_k: 50
                })
            });

            if (!searchResponse.ok) {
                throw new Error('Search request failed');
            }

            const searchResults = await searchResponse.json();
            displaySearchResults(searchResults);

            if (searchResults.length === 0) {
                searchResultsDropdown.innerHTML = '<div class="search-no-results">No recipes found for "' + query + '"</div>';
                searchResultsDropdown.classList.add('show');
            }
        }
    } catch (error) {
        console.error('Search error:', error);
        searchResultsDropdown.innerHTML = '<div class="search-no-results">Search error. Please try again.</div>';
        searchResultsDropdown.classList.add('show');
    }
}

// Filter Recipes by Category
function filterRecipesByCategory(categoryName) {
    currentPage = 1;
    
    if (categoryName === 'Quick Meal' || categoryName === 'all' || categoryName === 'All') {
        filteredRecipes = [...allRecipes];
        displayRecipesWithPagination();
        return;
    }
    
    // Map filter button names to actual categories
    const categoryMap = {
        'Stir-fry Veggies': 'Vegetarian',
        'Grilled Chicken': 'Chicken',
        'Pasta': 'Pasta',
        'Side Dishes': 'Side',
        'Salads': 'Side',
        'Red Meat Dishes': 'Beef',
        'Dessert': 'Dessert',
        'Chicken': 'Chicken',
        'Beef': 'Beef',
        'Seafood': 'Seafood',
        'Vegetarian': 'Vegetarian'
    };
    
    const actualCategory = categoryMap[categoryName] || categoryName;
    filteredRecipes = allRecipes.filter(recipe => 
        recipe.category.toLowerCase().includes(actualCategory.toLowerCase())
    );
    
    displayRecipesWithPagination();
    
    if (filteredRecipes.length === 0) {
        showError(`No recipes found for category "${categoryName}"`);
    }
}

// Display Recipes with Pagination
function displayRecipesWithPagination() {
    const startIndex = (currentPage - 1) * recipesPerPage;
    const endIndex = startIndex + recipesPerPage;
    const recipesToShow = filteredRecipes.slice(startIndex, endIndex);
    
    displayRecipes(recipesToShow);
    displayPagination();
}

// Display Recipes
function displayRecipes(recipes) {
    if (!recipesContainer) return;

    if (recipes.length === 0) {
        recipesContainer.innerHTML = '<p class="no-results">No recipes found.</p>';
        return;
    }

    recipesContainer.innerHTML = recipes.map(recipe => createRecipeCard(recipe)).join('');
}

// Display Pagination
function displayPagination() {
    const totalPages = Math.ceil(filteredRecipes.length / recipesPerPage);
    
    // Remove existing pagination if any
    const existingPagination = document.querySelector('.pagination-container');
    if (existingPagination) {
        existingPagination.remove();
    }
    
    if (totalPages <= 1) return; // No need for pagination
    
    const paginationHTML = `
        <div class="pagination-container">
            <div class="pagination-info">
                Showing ${(currentPage - 1) * recipesPerPage + 1}-${Math.min(currentPage * recipesPerPage, filteredRecipes.length)} 
                of ${filteredRecipes.length} recipes
            </div>
            <div class="pagination-buttons">
                <button class="pagination-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
                    ← Previous
                </button>
                ${generatePageNumbers(currentPage, totalPages)}
                <button class="pagination-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
                    Next →
                </button>
            </div>
        </div>
    `;
    
    const recipesSection = document.querySelector('.recipes-section');
    if (recipesSection) {
        recipesSection.insertAdjacentHTML('beforeend', paginationHTML);
    }
}

// Generate Page Numbers
function generatePageNumbers(current, total) {
    let pages = '';
    const maxVisible = 5;
    
    let startPage = Math.max(1, current - Math.floor(maxVisible / 2));
    let endPage = Math.min(total, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        pages += `
            <button class="pagination-btn page-number ${i === current ? 'active' : ''}" 
                    onclick="changePage(${i})">
                ${i}
            </button>
        `;
    }
    
    return pages;
}

// Change Page
function changePage(page) {
    const totalPages = Math.ceil(filteredRecipes.length / recipesPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    displayRecipesWithPagination();
    
    // Scroll to top of recipes section
    const recipesSection = document.querySelector('.recipes-section');
    if (recipesSection) {
        recipesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Make changePage available globally
window.changePage = changePage;

// View Recipe Details
function viewRecipe(recipeId) {
    window.location.href = `/recipe.html?id=${recipeId}`;
}

// View Recipe with Search Query
function viewRecipeWithQuery(recipeId, query) {
    window.location.href = `/recipe.html?id=${recipeId}&q=${query}`;
}

// Make functions available globally
window.viewRecipe = viewRecipe;
window.viewRecipeWithQuery = viewRecipeWithQuery;

// Create Recipe Card HTML from TheMealDB data
function createRecipeCard(recipe) {
    // Determine difficulty based on instructions length
    let difficulty = 'easy';
    if (recipe.instructions) {
        const instructionsLength = recipe.instructions.length;
        if (instructionsLength > 500) difficulty = 'hard';
        else if (instructionsLength > 250) difficulty = 'medium';
    }
    
    // Truncate instructions for preview
    const description = recipe.instructions 
        ? recipe.instructions.substring(0, 120) + '...' 
        : 'Delicious recipe.';
    
    // Calculate estimated time based on instructions
    const estimatedTime = recipe.instructions 
        ? Math.max(15, Math.min(120, Math.floor(recipe.instructions.length / 10)))
        : 30;
    
    // Ensure image URL is valid (now using local paths)
    const imageUrl = recipe.image || 'assets/images/thai-green-curry.png';
    
    return `
        <div class="recipe-card" onclick="viewRecipe('${recipe.id}')">
            <img src="${imageUrl}" 
                 alt="${recipe.title}"
                 loading="lazy" />
            <span class="difficulty-badge ${difficulty}">${difficulty}</span>
            <div class="recipe-info">
                <span class="recipe-time">${estimatedTime} mins</span>
                <h3>${recipe.title}</h3>
                <p class="recipe-author">By NomNom Chef</p>
                <p class="recipe-category">${recipe.category} • ${recipe.area}</p>
                <p class="recipe-desc">${description}</p>
            </div>
        </div>
    `;
}

// View Recipe Details
function viewRecipe(recipeId) {
    // Navigate to recipe detail page or show modal
    window.location.href = `/recipe?id=${recipeId}`;
}

// Display Sample Recipes (fallback when API is not available)
function displaySampleRecipes() {
    const sampleRecipes = [
        {
            id: '1',
            title: 'The Secret to Perfectly Make Avocado Tofu',
            time: '30 mins',
            author: 'Emily Carter',
            description: 'A delicious and healthy recipe',
            difficulty: 'easy',
            rating: 5,
            reviews: 25,
            image: 'assets/images/thai-green-curry.png'
        },
        {
            id: '2',
            title: 'Make sesame fulfilling dumplings',
            time: '10 mins',
            author: 'James Mitchell',
            description: 'Quick and tasty dumplings',
            difficulty: 'easy',
            rating: 5,
            reviews: 5,
            image: 'assets/images/scrambled-eggs.png'
        },
        {
            id: '3',
            title: 'Mastering the Art of Homemade Pizza',
            time: '40 mins',
            author: 'Hannah brooks',
            description: 'Learn to make perfect pizza at home',
            difficulty: 'medium',
            rating: 5,
            reviews: 21,
            image: 'assets/images/margherita-pizza.png'
        },
        {
            id: '4',
            title: 'How to Make the Perfect Fruit Mix',
            time: '15 mins',
            author: 'Rachel Adams',
            description: 'Refreshing fruit salad',
            difficulty: 'easy',
            rating: 5,
            reviews: 30,
            image: 'assets/images/thai-green-curry.png'
        }
    ];

    displayRecipes(sampleRecipes);
}

// Loading State
function showLoading() {
    if (recipesContainer) {
        recipesContainer.innerHTML = '<div class="loading">Loading...</div>';
    }
}

function hideLoading() {
    // Loading will be replaced by recipes or error message
}

// Error Handling
function showError(message) {
    if (recipesContainer) {
        recipesContainer.innerHTML = `<div class="error">${message}</div>`;
    }
}

// Utility Functions
function formatTime(minutes) {
    if (minutes < 60) {
        return `${minutes} mins`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

function sanitizeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions for use in other scripts
window.recipeApp = {
    loadLocalRecipes,
    handleSearch,
    viewRecipe,
    displayRecipes
};
