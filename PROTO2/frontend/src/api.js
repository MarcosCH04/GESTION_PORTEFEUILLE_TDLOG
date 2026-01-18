/**
 * api.js - Authentication API Handler
 * 
 * This module handles HTTP requests to the backend for user authentication.
 * It manages login and registration by communicating with FastAPI endpoints.
 */
import axios from 'axios';

// Backend API base URL (connects to FastAPI server)
const API_BASE_URL = 'http://localhost:8000/api';

// Configure axios to always send cookies with requests
axios.defaults.withCredentials = true;

/**
 * Executes a POST request for authentication (register or login).
 * @param {string} endpoint - 'register' or 'login'
 * @param {object} credentials - {username, password}
 * @returns {Promise<object>} The JSON response data
 */
export async function authRequest(endpoint, credentials) {
    try {
        const response = await axios.post(`${API_BASE_URL}/${endpoint}`, credentials);
        
        // The login request sets the cookie, which is all we need.
        // The register request returns UserInDB data.
        return response.data;
        
    } catch (error) {
        // Handle HTTP errors
        throw new Error(error.response?.data?.detail || 'Authentication failed.');
    }
}