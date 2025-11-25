import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Upload image for processing
export const uploadImage = async (file, onProgress) => {
    const formData = new FormData();
    formData.append('image', file);

    return api.post('/upload-image', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            if (onProgress) {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                );
                onProgress(percentCompleted);
            }
        },
    });
};

// Get all violations with pagination
export const getViolations = async (page = 1, pageSize = 50, filters = {}) => {
    const params = { page, page_size: pageSize, ...filters };
    return api.get('/violations', { params });
};

// Get specific violation
export const getViolation = async (id) => {
    return api.get(`/violations/${id}`);
};

// Delete violation
export const deleteViolation = async (id) => {
    return api.delete(`/violations/${id}`);
};

// Get statistics
export const getStatistics = async () => {
    return api.get('/statistics');
};

// Get configuration
export const getConfig = async () => {
    return api.get('/config');
};

// Update configuration
export const updateConfig = async (config) => {
    return api.put('/config', config);
};

// Get image URL
export const getImageUrl = (path) => {
    if (!path) return null;
    return `http://localhost:5000${path}`;
};

export default api;
