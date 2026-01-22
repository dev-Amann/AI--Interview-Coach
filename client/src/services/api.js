import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to include the Clerk token in headers if needed
// For now, we are using session based or simple requests, but typically we'd attach the token here.
/*
api.interceptors.request.use(async (config) => {
    // Logic to get token from Clerk if needed for backend validation
    return config;
});
*/

export default api;
