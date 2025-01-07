// This file serves as a template for new projects, initializing a sample application structure.

import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware and routes can be set up here
app.use(express.json());

// Sample route
app.get('/', (req, res) => {
    res.send('Welcome to the Copilot Workspace Template!');
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});