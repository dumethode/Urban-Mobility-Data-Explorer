// ============================================================================
// NYC URBAN MOBILITY EXPLORER - CHARTS CONTROLLER
// 100% DATA-DRIVEN - NO HARDCODED VALUES - NO FALLBACK DATA
// ============================================================================

const COLORS = {
    blue: '#1e4a8a',
    orange: '#f97316',
    green: '#10b981',
    purple: '#8b5cf6',
    teal: '#14b8a6'
};

let charts = {};

// ============================================================================
// MAIN CHART LOADER - Called from main.js
// ============================================================================
async function loadAllCharts() {
    console.log('Loading all charts from database...');

    try {
        // Load all chart data in parallel from APIs
        const [
            hourlyData,
            boroughData,
            paymentData,
            distanceData,
            fareData,
            dayOfWeekData,
            weeklyTrendData,
            routesData
        ] = await Promise.all([
            API.getHourlyStats(),
            API.getBoroughStats(),
            API.getPaymentStats(),
            API.getDistanceDistribution(),
            API.getFareDistribution(),
            API.getDayOfWeekStats(),
            API.getWeeklyTrend(),
            API.getTopRoutes(8)
        ]);

        // Create charts from real data
        if (hourlyData?.success) {
            createHourlyTripsChart(hourlyData.statistics);
            createFareByHourChart(hourlyData.statistics);
            createTipByHourChart(hourlyData.statistics);
        }

        if (boroughData?.success) {
            createBoroughChart(boroughData.statistics);
            createBoroughTable(boroughData.statistics);
        }

        if (paymentData?.success) {
            createPaymentChart(paymentData.statistics);
        }

        if (distanceData?.success) {
            createDistanceChart(distanceData.distribution);
        }

        if (fareData?.success) {
            createFareDistributionChart(fareData.distribution);
        }

        if (dayOfWeekData?.success) {
            createWeeklyPatternChart(dayOfWeekData.statistics);
        }

        if (weeklyTrendData?.success) {
            createMonthlyTrendChart(weeklyTrendData.trend);
        }

        if (routesData?.success) {
            createRoutesChart(routesData.routes);
        }

        console.log('✓ All charts created from database');
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

// ============================================================================
// HOURLY TRIPS CHART - From /api/stats/hourly
// ============================================================================
function createHourlyTripsChart(data) {
    const ctx = document.getElementById('hourly-trips-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    const labels = data.map(d => formatHourShort(d.pickup_hour));
    const values = data.map(d => d.trip_count);

    if (charts.hourlyTrips) charts.hourlyTrips.destroy();

    charts.hourlyTrips = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.blue,
                borderRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => (value / 1000).toFixed(0) + 'k'
                    }
                }
            }
        }
    });
}

// ============================================================================
// FARE BY HOUR CHART - From /api/stats/hourly
// ============================================================================
function createFareByHourChart(data) {
    const ctx = document.getElementById('fare-hour-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    const labels = data.map(d => formatHourShort(d.pickup_hour));
    const values = data.map(d => d.avg_fare);

    if (charts.fareHour) charts.fareHour.destroy();

    charts.fareHour = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                borderColor: COLORS.orange,
                backgroundColor: 'rgba(249, 115, 22, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    ticks: {
                        callback: value => '$' + value.toFixed(0)
                    }
                }
            }
        }
    });
}

// ============================================================================
// TIP BY HOUR CHART - From /api/stats/hourly
// ============================================================================
function createTipByHourChart(data) {
    const ctx = document.getElementById('tip-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    const labels = data.map(d => formatHourShort(d.pickup_hour));
    const values = data.map(d => d.avg_tip_percentage);

    if (charts.tip) charts.tip.destroy();

    charts.tip = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                borderColor: COLORS.green,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    ticks: {
                        callback: value => value.toFixed(1) + '%'
                    }
                }
            }
        }
    });
}

// ============================================================================
// PAYMENT METHODS CHART - From /api/stats/payment
// ============================================================================
function createPaymentChart(data) {
    const ctx = document.getElementById('payment-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    const labels = data.map(d => d.payment_name);
    const values = data.map(d => d.trip_count);
    const total = values.reduce((a, b) => a + b, 0);
    const percentages = values.map(v => ((v / total) * 100).toFixed(1));

    if (charts.payment) charts.payment.destroy();

    charts.payment = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [COLORS.blue, COLORS.orange, COLORS.green, COLORS.purple, COLORS.teal],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 12,
                        font: { size: 11 },
                        generateLabels: chart => {
                            const data = chart.data;
                            return data.labels.map((label, i) => ({
                                text: `${label}  ${percentages[i]}%`,
                                fillStyle: data.datasets[0].backgroundColor[i],
                                hidden: false,
                                index: i
                            }));
                        }
                    }
                }
            }
        }
    });
}

// ============================================================================
// DISTANCE DISTRIBUTION CHART - From /api/stats/distance-distribution
// ============================================================================
function createDistanceChart(data) {
    const ctx = document.getElementById('distance-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    const labels = data.map(d => d.distance_range);
    const values = data.map(d => d.trip_count);

    if (charts.distance) charts.distance.destroy();

    charts.distance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.green,
                borderRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => (value / 1000000).toFixed(1) + 'M'
                    }
                }
            }
        }
    });
}

// ============================================================================
// FARE DISTRIBUTION CHART - From /api/stats/fare-distribution
// ============================================================================
function createFareDistributionChart(data) {
    const ctx = document.getElementById('fare-dist-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    const labels = data.map(d => d.fare_range);
    const values = data.map(d => d.trip_count);

    if (charts.fareDist) charts.fareDist.destroy();

    charts.fareDist = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.purple,
                borderRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => (value / 1000000).toFixed(1) + 'M'
                    }
                }
            }
        }
    });
}

// ============================================================================
// BOROUGH CHART - From /api/stats/borough
// ============================================================================
function createBoroughChart(data) {
    const ctx = document.getElementById('borough-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    const sortedData = data.sort((a, b) => b.trip_count - a.trip_count);
    const labels = sortedData.map(d => d.borough);
    const values = sortedData.map(d => d.trip_count);

    if (charts.borough) charts.borough.destroy();

    charts.borough = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.blue,
                borderRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => (value / 1000000).toFixed(1) + 'M'
                    }
                }
            }
        }
    });
}

// ============================================================================
// BOROUGH TABLE - From /api/stats/borough
// ============================================================================
function createBoroughTable(data) {
    const tbody = document.getElementById('borough-table-body');
    if (!tbody || !data || data.length === 0) {
        if (tbody) tbody.innerHTML = '<tr><td colspan="5">No data available</td></tr>';
        return;
    }

    tbody.innerHTML = '';

    const sortedData = data.sort((a, b) => b.trip_count - a.trip_count);
    const colors = {
        'Manhattan': COLORS.blue,
        'Queens': COLORS.orange,
        'Brooklyn': COLORS.green,
        'Bronx': COLORS.purple,
        'Staten Island': COLORS.teal
    };

    sortedData.forEach(borough => {
        const row = document.createElement('tr');
        const color = colors[borough.borough] || COLORS.blue;

        row.innerHTML = `
            <td>
                <span style="display: inline-block; width: 8px; height: 8px; background: ${color}; border-radius: 50%; margin-right: 8px;"></span>
                ${borough.borough}
            </td>
            <td>${formatNumber(borough.trip_count)}</td>
            <td>${formatCurrency(borough.avg_fare)}</td>
            <td>${formatDistance(borough.avg_distance)}</td>
            <td>${borough.avg_duration.toFixed(1)} min</td>
        `;

        tbody.appendChild(row);
    });
}

// ============================================================================
// WEEKLY PATTERN CHART - From /api/stats/day-of-week
// ============================================================================
function createWeeklyPatternChart(data) {
    const ctx = document.getElementById('weekly-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    // Map day names to short labels
    const dayMap = {
        'Monday': 'Mon',
        'Tuesday': 'Tue',
        'Wednesday': 'Wed',
        'Thursday': 'Thu',
        'Friday': 'Fri',
        'Saturday': 'Sat',
        'Sunday': 'Sun'
    };

    const labels = data.map(d => dayMap[d.pickup_day_of_week] || d.pickup_day_of_week);
    const tripsData = data.map(d => d.trip_count);
    const revenueData = data.map(d => d.total_revenue / 1000000); // Convert to millions

    if (charts.weekly) charts.weekly.destroy();

    charts.weekly = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Trips',
                    data: tripsData,
                    backgroundColor: COLORS.blue,
                    borderRadius: 2,
                    yAxisID: 'y'
                },
                {
                    label: 'Revenue ($M)',
                    data: revenueData,
                    backgroundColor: COLORS.orange,
                    borderRadius: 2,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { size: 11 }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    beginAtZero: true,
                    ticks: {
                        callback: value => (value / 1000000).toFixed(1) + 'M'
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    beginAtZero: true,
                    grid: { drawOnChartArea: false },
                    ticks: {
                        callback: value => '$' + value.toFixed(1) + 'M'
                    }
                }
            }
        }
    });
}

// ============================================================================
// MONTHLY TREND CHART - From /api/stats/weekly-trend
// ============================================================================
function createMonthlyTrendChart(data) {
    const ctx = document.getElementById('monthly-trend-chart')?.getContext('2d');
    if (!ctx || !data || data.length === 0) return;

    const labels = data.map(d => d.week);
    const tripsData = data.map(d => d.trip_count);
    const revenueData = data.map(d => d.total_revenue / 1000000); // Convert to millions

    if (charts.monthlyTrend) charts.monthlyTrend.destroy();

    charts.monthlyTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Trips',
                    data: tripsData,
                    borderColor: COLORS.blue,
                    backgroundColor: 'rgba(30, 74, 138, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    yAxisID: 'y'
                },
                {
                    label: 'Revenue ($M)',
                    data: revenueData,
                    borderColor: COLORS.orange,
                    backgroundColor: 'rgba(249, 115, 22, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { size: 11 }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    ticks: {
                        callback: value => (value / 1000000).toFixed(1) + 'M'
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: {
                        callback: value => '$' + value.toFixed(1) + 'M'
                    }
                }
            }
        }
    });
}

// ============================================================================
// ROUTES CHART - From /api/routes/top
// ============================================================================
function createRoutesChart(routes) {
    const ctx = document.getElementById('routes-chart')?.getContext('2d');
    if (!ctx || !routes || routes.length === 0) return;

    const labels = routes.map(r => `${shortenName(r.pickup_zone)} → ${shortenName(r.dropoff_zone)}`);
    const values = routes.map(r => r.trip_count);

    if (charts.routes) charts.routes.destroy();

    charts.routes = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.blue,
                borderRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => (value / 1000).toFixed(1) + 'k'
                    }
                }
            }
        }
    });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================
function formatHourShort(hour) {
    if (hour === 0) return '00:00';
    if (hour < 10) return '0' + hour + ':00';
    return hour + ':00';
}

function shortenName(name) {
    if (name && name.length > 20) return name.substring(0, 17) + '...';
    return name || 'Unknown';
}
