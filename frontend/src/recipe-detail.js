// Recipe Detail Page Logic
const API_BASE_URL = 'http://localhost:8000'; // Backend API URL
const LOCAL_RECIPES_PATH = 'data/recipes_with_local_images.json'; // Fallback

// Get recipe ID and search query from URL
const urlParams = new URLSearchParams(window.location.search);
const recipeId = urlParams.get('id');
const searchQuery = urlParams.get('q'); // Get search keyword for highlighting

// DOM Elements
const loadingState = document.getElementById('loadingState');
const recipeDetail = document.getElementById('recipeDetail');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (recipeId) {
        loadRecipeDetail(recipeId);
    } else {
        showError('Recipe ID not found');
    }
});

// Load Recipe Detail using Backend API
async function loadRecipeDetail(id) {
    try {
        showLoading();

        // Try to get recipe from backend API
        const response = await fetch(`${API_BASE_URL}/recipes/${id}`);
        if (response.ok) {
            const recipe = await response.json();
            displayRecipeDetail(recipe);
            return;
        } else if (response.status === 404) {
            throw new Error('Recipe not found');
        }
    } catch (error) {
        console.error('API load recipe error:', error);
    }

    // Fallback to local JSON if API fails
    try {
        const response = await fetch(LOCAL_RECIPES_PATH);
        if (!response.ok) {
            throw new Error('Unable to load recipe data');
        }

        const recipes = await response.json();
        const recipe = recipes.find(r => r.id === id);

        if (!recipe) {
            throw new Error('Recipe not found');
        }

        displayRecipeDetail(recipe);
    } catch (fallbackError) {
        console.error('Fallback load recipe error:', fallbackError);
        showError(fallbackError.message || 'Unable to load recipe. Please try again later.');
    }
}

// Highlight keyword in text
function highlightText(text, keyword) {
    if (!keyword || !text) return text;
    
    // Escape special regex characters in keyword
    const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedKeyword})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// Display Recipe Detail
function displayRecipeDetail(recipe) {
    hideLoading();
    
    // Calculate estimated time
    const estimatedTime = recipe.instructions 
        ? Math.max(15, Math.min(120, Math.floor(recipe.instructions.length / 10)))
        : 30;
    
    // Build ingredients list HTML
    let ingredientsList = '';
    if (recipe.ingredients && Array.isArray(recipe.ingredients)) {
        ingredientsList = recipe.ingredients
            .filter(ing => {
                if (typeof ing === 'string') return ing.trim() !== '';
                if (typeof ing === 'object') return ing.ingredient && ing.ingredient.trim() !== '';
                return false;
            })
            .map(ing => {
                if (typeof ing === 'string') {
                    return `
                        <li>
                            <span class="ingredient-name">${highlightText(ing, searchQuery)}</span>
                        </li>
                    `;
                } else {
                    const measure = ing.measure && ing.measure.trim() !== '' 
                        ? `<span class="ingredient-measure">${highlightText(ing.measure, searchQuery)}</span>` 
                        : '';
                    return `
                        <li>
                            ${measure}
                            <span class="ingredient-name">${highlightText(ing.ingredient, searchQuery)}</span>
                        </li>
                    `;
                }
            })
            .join('');
    }
    
    if (!ingredientsList) {
        ingredientsList = '<li>Ingredient information not available</li>';
    }
    
    // Format instructions with line breaks and bold steps
    let formattedInstructions = recipe.instructions 
        ? recipe.instructions.replace(/\r\n/g, '\n')
        : 'Cooking instructions not available.';
    
    // Make STEP headers bold
    formattedInstructions = formattedInstructions
        .replace(/STEP\s+\d+\s*[-–—:]\s*[^\n]+/gi, (match) => `<strong>${match}</strong>`)
        .split('\n')
        .filter(line => line.trim())
        .map(line => `<p>${highlightText(line, searchQuery)}</p>`)
        .join('');
    
    const html = `
        <a href="/" class="back-button">← Back</a>
        
        <div class="recipe-header">
            <h1>${highlightText(recipe.title, searchQuery)}</h1>
            <div class="recipe-meta">
                <div class="recipe-meta-item">
                    <strong>Category:</strong> ${highlightText(recipe.category, searchQuery)}
                </div>
                <div class="recipe-meta-item">
                    <strong>Cuisine:</strong> ${highlightText(recipe.area, searchQuery)}
                </div>
                <div class="recipe-meta-item">
                    <strong>Time:</strong> ~${estimatedTime} mins
                </div>
            </div>
        </div>
        
        <div class="recipe-image-container">
            <img src="${recipe.image}" 
                 alt="${recipe.title}"
                 onerror="this.src='assets/images/thai-green-curry.png'" />
        </div>
        
        <div class="recipe-content">
            <div class="recipe-sidebar">
                <h2>Ingredients</h2>
                <ul class="ingredients-list">
                    ${ingredientsList}
                </ul>
            </div>
            
            <div class="recipe-main">
                <h2>Instructions</h2>
                <div class="instructions">
                    ${formattedInstructions}
                </div>
            </div>
        </div>
    `;
    
    recipeDetail.innerHTML = html;
    recipeDetail.style.display = 'block';
}

// Loading State
function showLoading() {
    loadingState.style.display = 'block';
    recipeDetail.style.display = 'none';
}

function hideLoading() {
    loadingState.style.display = 'none';
}

// Error Handling
function showError(message) {
    hideLoading();
    recipeDetail.innerHTML = `
        <div class="error">
            <p>${message}</p>
            <a href="/" class="back-button">← Back to Home</a>
        </div>
    `;
    recipeDetail.style.display = 'block';
}
