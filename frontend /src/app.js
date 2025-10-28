// API Configuration
const API_BASE_URL = 'http://localhost:5000/api'; // Update với địa chỉ backend của bạn
const LOCAL_RECIPES_PATH = 'data/recipes_with_local_images.json';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const recipesContainer = document.getElementById('recipesContainer');
const filterBtns = document.querySelectorAll('.filter-btn');

// State
let currentFilter = 'all';
let allRecipes = [];
let filteredRecipes = [];
let currentPage = 1;
const recipesPerPage = 12;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadLocalRecipes();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Search functionality
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    // Filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');
            currentFilter = btn.textContent;
            filterRecipesByCategory(currentFilter);
        });
    });
}

// Load Local Recipes from JSON file
async function loadLocalRecipes() {
    try {
        showLoading();
        const response = await fetch(LOCAL_RECIPES_PATH);
        
        if (!response.ok) {
            throw new Error('Không thể tải dữ liệu công thức');
        }

        allRecipes = await response.json();
        filteredRecipes = [...allRecipes];
        console.log(`Loaded ${allRecipes.length} recipes`);
        displayRecipesWithPagination();
        
        // Fill other sections with data
        fillPopularRecipes();
    } catch (error) {
        console.error('Load local recipes error:', error);
        displaySampleRecipes();
    } finally {
        hideLoading();
    }
}

// Fill Popular Recipes Section
function fillPopularRecipes() {
    const containers = document.querySelectorAll('.section-title-wrapper .recipes-slider');
    if (containers.length < 1) return;
    
    const popularContainer = containers[0];
    // Take recipes with longer instructions as "popular"
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
        : 'Món ăn ngon và dễ làm.';
    
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
                <div class="recipe-reviews">
                    <div class="stars">★★★★★</div>
                    <span>(${Math.floor(Math.random() * 50) + 10})</span>
                </div>
            </div>
        </div>
    `;
}

// Handle Search
async function handleSearch() {
    const query = searchInput.value.trim().toLowerCase();
    
    if (query === '') {
        // Reset to show all recipes
        filteredRecipes = [...allRecipes];
        currentPage = 1;
        displayRecipesWithPagination();
        return;
    }

    try {
        showLoading();
        
        // Search in local recipes
        filteredRecipes = allRecipes.filter(recipe => 
            recipe.title.toLowerCase().includes(query) ||
            recipe.category.toLowerCase().includes(query) ||
            recipe.area.toLowerCase().includes(query) ||
            (recipe.ingredients && recipe.ingredients.some(ing => 
                (typeof ing === 'string' && ing.toLowerCase().includes(query)) ||
                (typeof ing === 'object' && ing.ingredient && ing.ingredient.toLowerCase().includes(query))
            ))
        );
        
        currentPage = 1;
        displayRecipesWithPagination();
        
        if (filteredRecipes.length === 0) {
            showError(`Không tìm thấy công thức nào cho "${query}"`);
        }
    } catch (error) {
        console.error('Search error:', error);
        showError('Không thể tìm kiếm công thức. Vui lòng thử lại sau.');
    } finally {
        hideLoading();
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
        recipesContainer.innerHTML = '<p class="no-results">Không tìm thấy công thức nào.</p>';
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
                Hiển thị ${(currentPage - 1) * recipesPerPage + 1}-${Math.min(currentPage * recipesPerPage, filteredRecipes.length)} 
                trong tổng số ${filteredRecipes.length} công thức
            </div>
            <div class="pagination-buttons">
                <button class="pagination-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
                    ← Trước
                </button>
                ${generatePageNumbers(currentPage, totalPages)}
                <button class="pagination-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
                    Sau →
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

// Create Recipe Card HTML from TheMealDB data
function createRecipeCard(recipe) {
    // Determine difficulty based on instructions length
    let difficulty = 'easy';
    if (recipe.instructions) {
        const instructionsLength = recipe.instructions.length;
        if (instructionsLength > 500) difficulty = 'hard';
        else if (instructionsLength > 250) difficulty = 'medium';
    }
    
    // Generate random rating and reviews for demo
    const rating = 5;
    const reviews = Math.floor(Math.random() * 100) + 5;
    
    // Truncate instructions for preview
    const description = recipe.instructions 
        ? recipe.instructions.substring(0, 120) + '...' 
        : 'Công thức nấu ăn ngon.';
    
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
                <div class="recipe-reviews">
                    <div class="stars">${'★'.repeat(rating)}${'☆'.repeat(5-rating)}</div>
                    <span>(${reviews})</span>
                </div>
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
        recipesContainer.innerHTML = '<div class="loading">Đang tải...</div>';
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
