// API Service for handling all backend communications
class ApiService {
    constructor(baseUrl) {
        this.baseUrl = baseUrl || 'http://localhost:8000';
        this.timeout = 5000; // 5 seconds
    }

    // Generic fetch with timeout
    async fetchWithTimeout(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    // Search recipes
    async searchRecipes(query) {
        try {
            const url = `${this.baseUrl}/search?q=${encodeURIComponent(query)}`;
            const response = await this.fetchWithTimeout(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                data: data.recipes || [],
                error: null
            };
        } catch (error) {
            console.error('Search error:', error);
            return {
                success: false,
                data: [],
                error: error.message
            };
        }
    }

    // Get recipes by category
    async getRecipes(category = 'all', page = 1, limit = 12) {
        try {
            const url = `${this.baseUrl}/recipes?category=${category}&page=${page}&limit=${limit}`;
            const response = await this.fetchWithTimeout(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                data: data.recipes || [],
                total: data.total || 0,
                error: null
            };
        } catch (error) {
            console.error('Get recipes error:', error);
            return {
                success: false,
                data: [],
                total: 0,
                error: error.message
            };
        }
    }

    // Get recipe by ID
    async getRecipeById(id) {
        try {
            const url = `${this.baseUrl}/recipes/${id}`;
            const response = await this.fetchWithTimeout(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                data: data.recipe || null,
                error: null
            };
        } catch (error) {
            console.error('Get recipe error:', error);
            return {
                success: false,
                data: null,
                error: error.message
            };
        }
    }

    // Subscribe to newsletter
    async subscribeNewsletter(email) {
        try {
            const url = `${this.baseUrl}/newsletter/subscribe`;
            const response = await this.fetchWithTimeout(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                message: data.message || 'Subscribed successfully',
                error: null
            };
        } catch (error) {
            console.error('Newsletter subscription error:', error);
            return {
                success: false,
                message: null,
                error: error.message
            };
        }
    }

    // Get categories
    async getCategories() {
        try {
            const url = `${this.baseUrl}/categories`;
            const response = await this.fetchWithTimeout(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                data: data.categories || [],
                error: null
            };
        } catch (error) {
            console.error('Get categories error:', error);
            return {
                success: false,
                data: [],
                error: error.message
            };
        }
    }

    // Health check
    async healthCheck() {
        try {
            const url = `${this.baseUrl}/health`;
            const response = await this.fetchWithTimeout(url);
            return response.ok;
        } catch (error) {
            return false;
        }
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiService;
}
