// This file serves as the main entry point for project2, initializing the application and setting up configurations and routes.

import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware and configurations can be set up here
app.use(express.json());

// Example route
app.get('/', (req, res) => {
    res.send('Welcome to Project 2!');
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});