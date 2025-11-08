// Express server for NomNom frontend with clean URLs
const express = require('express');
const path = require('path');

const app = express();
const PORT = 5173;

// Serve static files (CSS, JS, images, etc.)
app.use(express.static(__dirname));

// Route for homepage - both / and /home
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/home', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Route for recipe detail page
app.get('/recipe', (req, res) => {
    res.sendFile(path.join(__dirname, 'recipe.html'));
});

// Fallback for .html extensions (redirect to clean URLs)
app.get('/index.html', (req, res) => res.redirect('/'));
app.get('/recipe.html', (req, res) => res.redirect('/recipe'));

// 404 handler
app.use((req, res) => {
    res.status(404).send('<h1>404 - Page Not Found</h1><p>The page you are looking for does not exist.</p><a href="/">Go to Homepage</a>');
});

app.listen(PORT, () => {
    console.log(`🚀 NomNom server running at http://localhost:${PORT}/`);
    console.log(`📁 Serving files from: ${__dirname}`);
    console.log(`\n✨ Clean URLs enabled!`);
    console.log(`   - Homepage:  http://localhost:${PORT}/`);
    console.log(`   - Recipe:    http://localhost:${PORT}/recipe?id=<recipe_id>\n`);
});
