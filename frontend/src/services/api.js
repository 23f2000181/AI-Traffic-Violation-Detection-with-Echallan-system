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

// ============================================================================
// E-CHALLAN APIs
// ============================================================================

// Get all challans with pagination and filters
export const getAllChallans = async (page = 1, pageSize = 50, filters = {}) => {
    const params = { page, page_size: pageSize, ...filters };
    return api.get('/challans', { params });
};

// Get specific challan by challan number
export const getChallan = async (challanNo) => {
    return api.get(`/challans/${challanNo}`);
};

// Update challan status
export const updateChallanStatus = async (challanNo, status) => {
    return api.put(`/challans/${challanNo}/status`, { status });
};

// Resend notification for a challan
export const resendNotification = async (challanNo, methods = ['sms']) => {
    return api.post(`/challans/${challanNo}/notify`, { methods });
};

// Get challan statistics
export const getChallanStatistics = async () => {
    return api.get('/challans/statistics');
};

// Lookup vehicle by license plate
export const lookupVehicle = async (plateNumber) => {
    return api.get(`/vehicles/${plateNumber}`);
};

// Get all vehicles
export const getAllVehicles = async (page = 1, pageSize = 50) => {
    const params = { page, page_size: pageSize };
    return api.get('/vehicles', { params });
};

// Get all owners
export const getAllOwners = async (page = 1, pageSize = 50) => {
    const params = { page, page_size: pageSize };
    return api.get('/owners', { params });
};

export default api;
