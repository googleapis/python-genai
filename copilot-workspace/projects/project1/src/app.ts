import express from 'express';
import { json } from 'body-parser';
import { routes } from './routes'; // Assuming you have a routes file

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(json());

// Routes
app.use('/api', routes);

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});