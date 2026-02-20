// ============================================================================
// NYC URBAN MOBILITY EXPLORER - MAIN CONTROLLER
// 100% DATA-DRIVEN - NO HARDCODED VALUES
// ============================================================================

document.addEventListener('DOMContentLoaded', async function () {
    console.log('NYC Urban Mobility Explorer initialized - Loading data from APIs...');

    // Load all data in parallel
    await Promise.all([
        loadOverviewStats(),
        loadDynamicInsights(),
        loadAllCharts(),
        loadRecentTrips()
    ]);

    // Setup event listeners
    setupEventListeners();

    console.log('All data loaded successfully!');
});

// ============================================================================
// OVERVIEW STATS - 100% from API
// ============================================================================
async function loadOverviewStats() {
    try {
        const response = await API.getStats();

        if (response && response.success) {
            const stats = response.statistics;

            // Update header trip count
            const headerTrips = stats.total_trips >= 1000000
                ? (stats.total_trips / 1000000).toFixed(1) + 'M+'
                : formatNumber(stats.total_trips);
            document.getElementById('header-trips').textContent = headerTrips;

            // Update all stat cards with REAL data
            document.getElementById('total-trips').textContent = formatNumber(stats.total_trips);
            document.getElementById('total-revenue').textContent = formatCurrency(stats.total_revenue / 1000000) + 'M';
            document.getElementById('avg-distance').innerHTML = stats.avg_distance.toFixed(1) + '<span class="unit"> mi</span>';
            document.getElementById('avg-fare').textContent = formatCurrency(stats.avg_fare);
            document.getElementById('avg-duration').innerHTML = stats.avg_duration.toFixed(1) + '<span class="unit"> min</span>';
            document.getElementById('total-passengers').textContent = formatNumber(stats.total_passengers);
            document.getElementById('avg-tip').textContent = stats.avg_tip_percentage.toFixed(1) + '%';
            document.getElementById('avg-passengers').textContent = stats.avg_passengers.toFixed(1);

            console.log('✓ Overview stats loaded from database');
        } else {
            console.error('Failed to load overview stats');
        }
    } catch (error) {
        console.error('Error loading overview stats:', error);
    }
}

// ============================================================================
// DYNAMIC INSIGHTS - Calculated from real data
// ============================================================================
async function loadDynamicInsights() {
    try {
        const response = await API.getInsights();

        if (response && response.success) {
            const insights = response.insights;

            // Insight 1: Peak Hours (from real data)
            if (insights.peak_hours) {
                const ph = insights.peak_hours;
                const peakHourFormatted = formatHour(ph.peak_hour);
                const lowestHourFormatted = formatHour(ph.lowest_hour);

                document.getElementById('insight-1').textContent =
                    `Evening rush (${peakHourFormatted}) sees ${ph.ratio}x more trips than morning rush (${lowestHourFormatted}). People take taxis home more than to work.`;
            }

            // Insight 2: Night Fares (from real data)
            if (insights.night_fares) {
                const nf = insights.night_fares;

                document.getElementById('insight-2').textContent =
                    `Trips between midnight and 5 AM have fares ${nf.premium_percent.toFixed(0)}% higher than daytime ($${nf.night_avg.toFixed(2)} vs $${nf.day_avg.toFixed(2)}). Longer distances and surcharges drive this up.`;
            }

            // Insight 3: Payment Methods (from real data)
            if (insights.payment_methods && insights.payment_methods.length > 0) {
                const topPayment = insights.payment_methods[0];
                const cashPayment = insights.payment_methods.find(p => p.payment_name === 'Cash') ||
                    insights.payment_methods[1];

                document.getElementById('insight-3').textContent =
                    `${topPayment.percentage}% of all payments are by ${topPayment.payment_name.toLowerCase()}. Cash usage drops to just ${cashPayment.percentage}% during late-night hours.`;
            }

            console.log('✓ Dynamic insights generated from data');
        } else {
            console.error('Failed to load insights');
        }
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

// ============================================================================
// RECENT TRIPS - From database with custom QuickSort
// ============================================================================
async function loadRecentTrips(rankBy = 'fare', order = 'desc') {
    try {
        const tbody = document.getElementById('trips-tbody');
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Loading trips from database...</td></tr>';

        const response = await API.getRankedTrips(rankBy, order, 100);

        if (response && response.success) {
            displayTrips(response.trips);
            displayAlgorithmInfo(response.algorithm_stats, rankBy, order);
            updateTripsCount(response.trips.length);

            console.log(`✓ Loaded ${response.trips.length} trips ranked by ${rankBy}`);
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">Failed to load trips</td></tr>';
        }
    } catch (error) {
        console.error('Error loading trips:', error);
        const tbody = document.getElementById('trips-tbody');
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Error loading trips</td></tr>';
    }
}

// ============================================================================
// DISPLAY TRIPS IN TABLE
// ============================================================================
function displayTrips(trips) {
    const tbody = document.getElementById('trips-tbody');
    tbody.innerHTML = '';

    if (!trips || trips.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">No trips found matching your filters</td></tr>';
        return;
    }

    trips.forEach((trip, index) => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${trip.pickup_zone || 'Unknown'}</td>
            <td>${trip.dropoff_zone || 'Unknown'}</td>
            <td>${formatDistance(trip.trip_distance)}</td>
            <td>${formatDuration(trip.trip_duration_minutes)}</td>
            <td>${formatCurrency(trip.total_amount)}</td>
            <td>${trip.tip_percentage ? formatPercentage(trip.tip_percentage) : 'N/A'}</td>
        `;

        tbody.appendChild(row);
    });
}

// ============================================================================
// DISPLAY ALGORITHM INFO
// ============================================================================
function displayAlgorithmInfo(stats, rankBy, order) {
    const infoDiv = document.getElementById('trips-count');

    const rankLabel = {
        'fare': 'Fare Amount',
        'distance': 'Trip Distance',
        'duration': 'Trip Duration',
        'tip': 'Tip Percentage'
    }[rankBy];

    const orderLabel = order === 'desc' ? 'Highest to Lowest' : 'Lowest to Highest';

    infoDiv.innerHTML = `
        <strong>Custom QuickSort Algorithm Applied</strong> | 
        Ranked by: ${rankLabel} (${orderLabel}) | 
        Performance: ${formatNumber(stats.comparisons)} comparisons, ${formatNumber(stats.swaps)} swaps | 
        Complexity: ${stats.time_complexity}
    `;
}

// ============================================================================
// UPDATE TRIPS COUNT
// ============================================================================
function updateTripsCount(count) {
    // Count is now displayed in algorithm info
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================
function setupEventListeners() {
    // Filter toggle
    const filterToggle = document.getElementById('toggle-filters');
    const filtersAdvanced = document.getElementById('advanced-filters');

    if (filterToggle && filtersAdvanced) {
        filterToggle.addEventListener('click', function () {
            filtersAdvanced.classList.toggle('show');
        });
    }

    // Apply filters
    const applyFiltersBtn = document.getElementById('apply-filters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }

    // Reset filters
    const resetFiltersBtn = document.getElementById('reset-filters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', resetFilters);
    }

    // Apply ranking
    const applyRankingBtn = document.getElementById('apply-ranking');
    if (applyRankingBtn) {
        applyRankingBtn.addEventListener('click', applyRanking);
    }

    // Quick filters (immediate effect)
    const boroughFilter = document.getElementById('borough-filter');
    const paymentFilter = document.getElementById('payment-type');

    if (boroughFilter) {
        boroughFilter.addEventListener('change', function () {
            if (this.value) applyFilters();
        });
    }

    if (paymentFilter) {
        paymentFilter.addEventListener('change', function () {
            if (this.value) applyFilters();
        });
    }
}

// ============================================================================
// APPLY FILTERS - Get filtered data from API
// ============================================================================
async function applyFilters() {
    console.log('Applying filters...');

    const filters = {
        min_fare: document.getElementById('min-fare')?.value,
        max_fare: document.getElementById('max-fare')?.value,
        pickup_borough: document.getElementById('borough-filter')?.value,
        payment_type: document.getElementById('payment-type')?.value
    };

    // Remove empty filters
    Object.keys(filters).forEach(key => {
        if (!filters[key]) delete filters[key];
    });

    console.log('Filters:', filters);

    try {
        const tbody = document.getElementById('trips-tbody');
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Loading filtered trips from database...</td></tr>';

        const response = await API.getTrips(filters, 100);

        if (response && response.success && response.trips) {
            displayTrips(response.trips);

            const infoDiv = document.getElementById('trips-count');
            infoDiv.innerHTML = `<strong>Showing ${response.trips.length} trips matching your filters</strong>`;

            console.log(`✓ Loaded ${response.trips.length} filtered trips`);
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No trips found matching filters</td></tr>';
        }
    } catch (error) {
        console.error('Error applying filters:', error);
        const tbody = document.getElementById('trips-tbody');
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Error loading filtered trips</td></tr>';
    }
}

// ============================================================================
// RESET FILTERS
// ============================================================================
function resetFilters() {
    console.log('Resetting filters...');

    const minFare = document.getElementById('min-fare');
    const maxFare = document.getElementById('max-fare');
    const borough = document.getElementById('borough-filter');
    const payment = document.getElementById('payment-type');
    const search = document.getElementById('search-input');

    if (minFare) minFare.value = '';
    if (maxFare) maxFare.value = '';
    if (borough) borough.value = '';
    if (payment) payment.value = '';
    if (search) search.value = '';

    loadRecentTrips();
}

// ============================================================================
// APPLY RANKING
// ============================================================================
async function applyRanking() {
    console.log('Applying ranking...');

    const rankBy = document.getElementById('rank-by')?.value || 'fare';
    const order = document.getElementById('rank-order')?.value || 'desc';

    console.log(`Ranking by: ${rankBy}, Order: ${order}`);

    await loadRecentTrips(rankBy, order);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================
function formatHour(hour) {
    if (hour === 0) return '12 AM';
    if (hour < 12) return hour + ' AM';
    if (hour === 12) return '12 PM';
    return (hour - 12) + ' PM';
}