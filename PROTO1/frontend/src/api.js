// Configuration for API calls
const API_BASE_URL = 'http://backend:8000/api';

/**
 * Executes a POST request for authentication (register or login).
 * @param {string} endpoint - 'register' or 'login'
 * @param {object} credentials - {username, password}
 * @returns {Promise<object>} The JSON response data
 */
export async function authRequest(endpoint, credentials) {
    const url = `${API_BASE_URL}/${endpoint}`;
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // IMPORTANT: We must include credentials to allow the browser 
        // to send and receive the HTTP-only session cookie.
        credentials: 'include', 
        body: JSON.stringify(credentials),
    });

    if (!response.ok) {
        // Parse the error message from the backend (e.g., "Username already registered")
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Authentication failed.');
    }

    // The login request sets the cookie, which is all we need.
    // The register request returns UserInDB data.
    return response.json();
}