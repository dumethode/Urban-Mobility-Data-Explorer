from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), '..',
                       'data', 'database', 'taxi_data.db')


def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    print(f"Connected to database: {DB_PATH}")
    return conn


def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))


try:
    from custom_algorithm import quicksort
except ImportError:
    def quicksort(arr, key, reverse=False):
        """Fallback sort using custom implementation"""
        comparisons = 0
        swaps = 0

        def partition(low, high):
            nonlocal comparisons, swaps
            pivot = arr[high][key]
            i = low - 1

            for j in range(low, high):
                comparisons += 1
                if (reverse and arr[j][key] > pivot) or (not reverse and arr[j][key] < pivot):
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps += 1

            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            swaps += 1
            return i + 1

        def quicksort_helper(low, high):
            if low < high:
                pi = partition(low, high)
                quicksort_helper(low, pi - 1)
                quicksort_helper(pi + 1, high)

        if len(arr) > 0:
            quicksort_helper(0, len(arr) - 1)

        return arr, comparisons, swaps


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get all overview statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                COUNT(*) as total_trips,
                SUM(total_amount) as total_revenue,
                AVG(trip_distance) as avg_distance,
                AVG(total_amount) as avg_fare,
                AVG(trip_duration_minutes) as avg_duration,
                SUM(passenger_count) as total_passengers,
                AVG(passenger_count) as avg_passengers,
                AVG(tip_percentage) as avg_tip_percentage
            FROM trips
        ''')

        stats = dict_from_row(cursor.fetchone())
        conn.close()

        return jsonify({
            'success': True,
            'statistics': {
                'total_trips': int(stats['total_trips']),
                'total_revenue': float(stats['total_revenue'] or 0),
                'avg_distance': float(stats['avg_distance'] or 0),
                'avg_fare': float(stats['avg_fare'] or 0),
                'avg_duration': float(stats['avg_duration'] or 0),
                'total_passengers': int(stats['total_passengers'] or 0),
                'avg_passengers': float(stats['avg_passengers'] or 0),
                'avg_tip_percentage': float(stats['avg_tip_percentage'] or 0)
            }
        })
    except Exception as e:
        print(f"Error in /api/stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/hourly', methods=['GET'])
def get_hourly_stats():
    """Get statistics by hour of day"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                pickup_hour,
                COUNT(*) as trip_count,
                AVG(total_amount) as avg_fare,
                AVG(trip_distance) as avg_distance,
                AVG(trip_duration_minutes) as avg_duration,
                AVG(tip_percentage) as avg_tip_percentage
            FROM trips
            WHERE pickup_hour IS NOT NULL
            GROUP BY pickup_hour
            ORDER BY pickup_hour
        ''')

        hourly_stats = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'statistics': hourly_stats
        })
    except Exception as e:
        print(f"Error in /api/stats/hourly: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/borough', methods=['GET'])
def get_borough_stats():
    """Get statistics by borough"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                z.borough,
                COUNT(*) as trip_count,
                AVG(t.total_amount) as avg_fare,
                AVG(t.trip_distance) as avg_distance,
                AVG(t.trip_duration_minutes) as avg_duration
            FROM trips t
            JOIN zones z ON t.pickup_location_id = z.location_id
            WHERE z.borough IS NOT NULL AND z.borough != 'Unknown'
            GROUP BY z.borough
            ORDER BY trip_count DESC
        ''')

        borough_stats = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'statistics': borough_stats
        })
    except Exception as e:
        print(f"Error in /api/stats/borough: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/payment', methods=['GET'])
def get_payment_stats():
    """Get statistics by payment type"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                pt.payment_name,
                COUNT(*) as trip_count,
                AVG(t.total_amount) as avg_fare
            FROM trips t
            JOIN payment_types pt ON t.payment_type_id = pt.payment_type_id
            GROUP BY pt.payment_name
            ORDER BY trip_count DESC
        ''')

        payment_stats = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'statistics': payment_stats
        })
    except Exception as e:
        print(f"Error in /api/stats/payment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/distance-distribution', methods=['GET'])
def get_distance_distribution():
    """Get distance distribution"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                CASE 
                    WHEN trip_distance <= 2 THEN '0-2 mi'
                    WHEN trip_distance <= 5 THEN '2-5 mi'
                    WHEN trip_distance <= 10 THEN '5-10 mi'
                    WHEN trip_distance <= 20 THEN '10-20 mi'
                    WHEN trip_distance <= 50 THEN '20-50 mi'
                    ELSE '50+ mi'
                END as distance_range,
                COUNT(*) as trip_count
            FROM trips
            GROUP BY distance_range
            ORDER BY 
                CASE distance_range
                    WHEN '0-2 mi' THEN 1
                    WHEN '2-5 mi' THEN 2
                    WHEN '5-10 mi' THEN 3
                    WHEN '10-20 mi' THEN 4
                    WHEN '20-50 mi' THEN 5
                    WHEN '50+ mi' THEN 6
                END
        ''')

        distribution = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'distribution': distribution
        })
    except Exception as e:
        print(f"Error in /api/stats/distance-distribution: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/fare-distribution', methods=['GET'])
def get_fare_distribution():
    """Get fare distribution"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                CASE 
                    WHEN total_amount <= 10 THEN '$0-10'
                    WHEN total_amount <= 20 THEN '$10-20'
                    WHEN total_amount <= 30 THEN '$20-30'
                    WHEN total_amount <= 50 THEN '$30-50'
                    WHEN total_amount <= 100 THEN '$50-100'
                    ELSE '$100+'
                END as fare_range,
                COUNT(*) as trip_count
            FROM trips
            GROUP BY fare_range
            ORDER BY 
                CASE fare_range
                    WHEN '$0-10' THEN 1
                    WHEN '$10-20' THEN 2
                    WHEN '$20-30' THEN 3
                    WHEN '$30-50' THEN 4
                    WHEN '$50-100' THEN 5
                    WHEN '$100+' THEN 6
                END
        ''')

        distribution = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'distribution': distribution
        })
    except Exception as e:
        print(f"Error in /api/stats/fare-distribution: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/day-of-week', methods=['GET'])
def get_day_of_week_stats():
    """Get statistics by day of week"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                CASE CAST(strftime('%w', pickup_datetime) AS INTEGER)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as pickup_day_of_week,
                COUNT(*) as trip_count,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_fare
            FROM trips
            GROUP BY pickup_day_of_week
            ORDER BY 
                CASE pickup_day_of_week
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                    WHEN 'Sunday' THEN 7
                END
        ''')

        day_stats = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'statistics': day_stats
        })
    except Exception as e:
        print(f"Error in /api/stats/day-of-week: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/weekly-trend', methods=['GET'])
def get_weekly_trend():
    """Get weekly trend for the month"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                CASE 
                    WHEN CAST(strftime('%d', pickup_datetime) AS INTEGER) <= 7 THEN 'Week 1'
                    WHEN CAST(strftime('%d', pickup_datetime) AS INTEGER) <= 14 THEN 'Week 2'
                    WHEN CAST(strftime('%d', pickup_datetime) AS INTEGER) <= 21 THEN 'Week 3'
                    ELSE 'Week 4'
                END as week,
                COUNT(*) as trip_count,
                SUM(total_amount) as total_revenue
            FROM trips
            GROUP BY week
            ORDER BY week
        ''')

        weekly_trend = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'trend': weekly_trend
        })
    except Exception as e:
        print(f"Error in /api/stats/weekly-trend: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/routes/top', methods=['GET'])
def get_top_routes():
    """Get most popular routes"""
    try:
        limit = request.args.get('limit', 10, type=int)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                z1.zone as pickup_zone,
                z2.zone as dropoff_zone,
                COUNT(*) as trip_count,
                AVG(t.total_amount) as avg_fare,
                AVG(t.trip_distance) as avg_distance
            FROM trips t
            JOIN zones z1 ON t.pickup_location_id = z1.location_id
            JOIN zones z2 ON t.dropoff_location_id = z2.location_id
            WHERE z1.zone IS NOT NULL AND z2.zone IS NOT NULL 
              AND z1.zone != 'Unknown' AND z2.zone != 'Unknown'
            GROUP BY z1.zone, z2.zone
            ORDER BY trip_count DESC
            LIMIT ?
        ''', (limit,))

        routes = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'routes': routes
        })
    except Exception as e:
        print(f"Error in /api/routes/top: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Generate dynamic insights from data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insights = {}

        cursor.execute('''
            SELECT 
                pickup_hour,
                COUNT(*) as trip_count
            FROM trips
            WHERE pickup_hour IS NOT NULL
            GROUP BY pickup_hour
            ORDER BY trip_count DESC
            LIMIT 1
        ''')
        peak_hour = dict_from_row(cursor.fetchone())

        cursor.execute('''
            SELECT 
                pickup_hour,
                COUNT(*) as trip_count
            FROM trips
            WHERE pickup_hour IS NOT NULL
            GROUP BY pickup_hour
            ORDER BY trip_count ASC
            LIMIT 1
        ''')
        lowest_hour = dict_from_row(cursor.fetchone())

        ratio = peak_hour['trip_count'] / \
            lowest_hour['trip_count'] if lowest_hour['trip_count'] > 0 else 0
        insights['peak_hours'] = {
            'peak_hour': peak_hour['pickup_hour'],
            'peak_count': peak_hour['trip_count'],
            'lowest_hour': lowest_hour['pickup_hour'],
            'lowest_count': lowest_hour['trip_count'],
            'ratio': round(ratio, 1)
        }

        cursor.execute('''
            SELECT 
                AVG(CASE WHEN pickup_hour >= 0 AND pickup_hour < 6 
                    THEN total_amount END) as night_avg,
                AVG(CASE WHEN pickup_hour >= 6 AND pickup_hour < 18 
                    THEN total_amount END) as day_avg
            FROM trips
            WHERE pickup_hour IS NOT NULL
        ''')
        fare_comparison = dict_from_row(cursor.fetchone())

        night_premium = ((fare_comparison['night_avg'] / fare_comparison['day_avg']
                          ) - 1) * 100 if fare_comparison['day_avg'] > 0 else 0
        insights['night_fares'] = {
            'night_avg': round(fare_comparison['night_avg'] or 0, 2),
            'day_avg': round(fare_comparison['day_avg'] or 0, 2),
            'premium_percent': round(night_premium, 1)
        }

        cursor.execute('''
            SELECT 
                pt.payment_name,
                COUNT(*) as trip_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips), 1) as percentage
            FROM trips t
            JOIN payment_types pt ON t.payment_type_id = pt.payment_type_id
            GROUP BY pt.payment_name
            ORDER BY trip_count DESC
        ''')
        payment_dist = [dict_from_row(row) for row in cursor.fetchall()]
        insights['payment_methods'] = payment_dist

        conn.close()

        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        print(f"Error in /api/insights: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trips', methods=['GET'])
def get_trips():
    """Get trips with optional filters"""
    try:
        min_fare = request.args.get('min_fare', type=float)
        max_fare = request.args.get('max_fare', type=float)
        pickup_borough = request.args.get('pickup_borough')
        payment_type = request.args.get('payment_type')
        limit = request.args.get('limit', 100, type=int)

        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT 
                t.*,
                z1.borough as pickup_borough,
                z1.zone as pickup_zone,
                z2.zone as dropoff_zone
            FROM trips t
            JOIN zones z1 ON t.pickup_location_id = z1.location_id
            JOIN zones z2 ON t.dropoff_location_id = z2.location_id
            WHERE 1=1
        '''

        params = []

        if min_fare is not None:
            query += ' AND t.total_amount >= ?'
            params.append(min_fare)

        if max_fare is not None:
            query += ' AND t.total_amount <= ?'
            params.append(max_fare)

        if pickup_borough:
            query += ' AND z1.borough = ?'
            params.append(pickup_borough)

        if payment_type:
            if payment_type.lower() == 'cash':
                query += ' AND t.payment_type_id = 2'
            elif payment_type.lower() == 'credit':
                query += ' AND t.payment_type_id = 1'

        query += ' LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        trips = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'trips': trips,
            'count': len(trips)
        })
    except Exception as e:
        print(f"Error in /api/trips: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trips/ranked', methods=['GET'])
def get_ranked_trips():
    """Get trips ranked using custom QuickSort"""
    try:
        rank_by = request.args.get('rank_by', 'fare')
        order = request.args.get('order', 'desc')
        limit = request.args.get('limit', 100, type=int)

        conn = get_db_connection()
        cursor = conn.cursor()

        column_map = {
            'fare': 'total_amount',
            'distance': 'trip_distance',
            'duration': 'trip_duration_minutes',
            'tip': 'tip_percentage'
        }

        cursor.execute(f'''
            SELECT 
                t.*,
                z1.zone as pickup_zone,
                z2.zone as dropoff_zone
            FROM trips t
            JOIN zones z1 ON t.pickup_location_id = z1.location_id
            JOIN zones z2 ON t.dropoff_location_id = z2.location_id
            LIMIT ?
        ''', (limit * 10,))

        trips = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        sort_column = column_map.get(rank_by, 'total_amount')
        sorted_trips, comparisons, swaps = quicksort(
            trips, sort_column, order == 'desc')

        sorted_trips = sorted_trips[:limit]

        print(f"Ranking {len(trips)} trips by {rank_by}...")
        print(f"Sorting completed: {comparisons} comparisons, {swaps} swaps")

        return jsonify({
            'success': True,
            'trips': sorted_trips,
            'algorithm_stats': {
                'comparisons': comparisons,
                'swaps': swaps,
                'algorithm': 'QuickSort',
                'time_complexity': 'O(n log n)',
                'space_complexity': 'O(log n)'
            }
        })
    except Exception as e:
        print(f"Error in /api/trips/ranked: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting NYC Taxi Data Explorer API...")
    print(f"Database: {DB_PATH}")
    app.run(debug=True, port=5000)
