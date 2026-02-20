// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// API Client - All endpoints are 100% data-driven
const API = {
    // ========================================================================
    // OVERVIEW STATS - Get all KPIs
    // ========================================================================
    async getStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching stats:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // HOURLY STATS - For hourly charts
    // ========================================================================
    async getHourlyStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats/hourly`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching hourly stats:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // BOROUGH STATS - For borough charts
    // ========================================================================
    async getBoroughStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats/borough`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching borough stats:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // PAYMENT STATS - For payment method chart
    // ========================================================================
    async getPaymentStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats/payment`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching payment stats:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // DISTANCE DISTRIBUTION - For distance spread chart
    // ========================================================================
    async getDistanceDistribution() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats/distance-distribution`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching distance distribution:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // FARE DISTRIBUTION - For fare distribution chart
    // ========================================================================
    async getFareDistribution() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats/fare-distribution`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching fare distribution:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // DAY OF WEEK STATS - For weekly pattern chart
    // ========================================================================
    async getDayOfWeekStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats/day-of-week`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching day-of-week stats:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // WEEKLY TREND - For January 2019 weekly trend chart
    // ========================================================================
    async getWeeklyTrend() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats/weekly-trend`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching weekly trend:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // TOP ROUTES - For most popular routes chart
    // ========================================================================
    async getTopRoutes(limit = 8) {
        try {
            const response = await fetch(`${API_BASE_URL}/routes/top?limit=${limit}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching top routes:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // DYNAMIC INSIGHTS - Get data-driven insights
    // ========================================================================
    async getInsights() {
        try {
            const response = await fetch(`${API_BASE_URL}/insights`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching insights:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // TRIPS WITH FILTERS - For filtered trips table
    // ========================================================================
    async getTrips(filters = {}, limit = 100) {
        try {
            const params = new URLSearchParams();

            if (filters.min_fare) params.append('min_fare', filters.min_fare);
            if (filters.max_fare) params.append('max_fare', filters.max_fare);
            if (filters.pickup_borough) params.append('pickup_borough', filters.pickup_borough);
            if (filters.payment_type) params.append('payment_type', filters.payment_type);
            params.append('limit', limit);

            const response = await fetch(`${API_BASE_URL}/trips?${params}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching trips:', error);
            return { success: false, error: error.message };
        }
    },

    // ========================================================================
    // RANKED TRIPS - Using custom QuickSort algorithm
    // ========================================================================
    async getRankedTrips(rankBy = 'fare', order = 'desc', limit = 100) {
        try {
            const params = new URLSearchParams({
                rank_by: rankBy,
                order: order,
                limit: limit
            });

            const response = await fetch(`${API_BASE_URL}/trips/ranked?${params}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching ranked trips:', error);
            return { success: false, error: error.message };
        }
    }
};

// Utility Functions for Formatting
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k';
    }
    return num.toLocaleString();
}

function formatCurrency(amount) {
    return '$' + amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

function formatDistance(miles) {
    return miles.toFixed(2) + ' mi';
}

function formatDuration(minutes) {
    if (minutes >= 60) {
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);
        return `${hours}h ${mins}m`;
    }
    return Math.round(minutes) + ' min';
}

function formatPercentage(percent) {
    return percent.toFixed(1) + '%';
}