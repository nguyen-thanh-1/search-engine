// API Configuration
const config = {
    // Backend API URL
    apiUrl: process.env.API_URL || 'http://localhost:8000',
    
    // API Endpoints
    endpoints: {
        search: '/search',
        recipes: '/recipes',
        recipeDetail: '/recipes/:id',
        categories: '/categories',
        newsletter: '/newsletter/subscribe'
    },
    
    // Pagination
    defaultPageSize: 12,
    
    // Timeouts
    requestTimeout: 5000,
    
    // Image placeholders
    placeholderImage: 'assets/images/placeholder.jpg',
    
    // Supported difficulty levels
    difficultyLevels: ['easy', 'medium', 'hard'],
    
    // Supported categories
    categories: [
        'Quick Meal',
        'Stir-fry Veggies',
        'Grilled Chicken',
        'Pasta',
        'Side Dishes',
        'Salads',
        'Red Meat Dishes',
        'Dessert',
        'Bakery',
        'Cold Meals'
    ]
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = config;
}
