"""
Database Manager for NYC Taxi Data Explorer
Handles all database operations with SQLite
"""

import sqlite3
import pandas as pd
from datetime import datetime


class DatabaseManager:
    """Manage SQLite database for taxi trip data"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            print("Database connection closed")

    def create_schema(self):
        """Create database schema programmatically"""
        print("Creating database schema...")

        tables = ['trips', 'zones', 'dates', 'rate_codes', 'payment_types']
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table}")

        self.cursor.execute("""
            CREATE TABLE zones (
                location_id INTEGER PRIMARY KEY,
                borough TEXT NOT NULL,
                zone TEXT NOT NULL,
                service_zone TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE dates (
                date_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                is_weekend INTEGER NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE rate_codes (
                rate_code_id INTEGER PRIMARY KEY,
                rate_name TEXT NOT NULL
            )
        """)

        rate_codes = [
            (1, 'Standard rate'),
            (2, 'JFK'),
            (3, 'Newark'),
            (4, 'Nassau or Westchester'),
            (5, 'Negotiated fare'),
            (6, 'Group ride')
        ]
        self.cursor.executemany(
            "INSERT INTO rate_codes (rate_code_id, rate_name) VALUES (?, ?)",
            rate_codes
        )

        self.cursor.execute("""
            CREATE TABLE payment_types (
                payment_type_id INTEGER PRIMARY KEY,
                payment_name TEXT NOT NULL
            )
        """)

        payment_types = [
            (1, 'Credit card'),
            (2, 'Cash'),
            (3, 'No charge'),
            (4, 'Dispute'),
            (5, 'Unknown'),
            (6, 'Voided trip')
        ]
        self.cursor.executemany(
            "INSERT INTO payment_types (payment_type_id, payment_name) VALUES (?, ?)",
            payment_types
        )

        self.cursor.execute("""
            CREATE TABLE trips (
                trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER NOT NULL,
                pickup_datetime DATETIME NOT NULL,
                dropoff_datetime DATETIME NOT NULL,
                passenger_count INTEGER NOT NULL,
                trip_distance REAL NOT NULL,
                rate_code_id INTEGER NOT NULL,
                store_and_fwd_flag TEXT,
                pickup_location_id INTEGER NOT NULL,
                dropoff_location_id INTEGER NOT NULL,
                payment_type_id INTEGER NOT NULL,
                fare_amount REAL NOT NULL,
                extra REAL,
                mta_tax REAL,
                tip_amount REAL,
                tolls_amount REAL,
                improvement_surcharge REAL,
                total_amount REAL NOT NULL,
                congestion_surcharge REAL,
                trip_duration_minutes REAL,
                speed_mph REAL,
                tip_percentage REAL,
                cost_per_mile REAL,
                pickup_hour INTEGER,
                pickup_date DATE,
                FOREIGN KEY (pickup_location_id) REFERENCES zones(location_id),
                FOREIGN KEY (dropoff_location_id) REFERENCES zones(location_id),
                FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id),
                FOREIGN KEY (payment_type_id) REFERENCES payment_types(payment_type_id)
            )
        """)

        print("Creating indexes...")
        self.cursor.execute(
            "CREATE INDEX idx_pickup_datetime ON trips(pickup_datetime)")
        self.cursor.execute(
            "CREATE INDEX idx_pickup_location ON trips(pickup_location_id)")
        self.cursor.execute(
            "CREATE INDEX idx_dropoff_location ON trips(dropoff_location_id)")
        self.cursor.execute(
            "CREATE INDEX idx_payment_type ON trips(payment_type_id)")
        self.cursor.execute(
            "CREATE INDEX idx_pickup_hour ON trips(pickup_hour)")

        self.conn.commit()
        print("Schema created successfully")

    def load_zones(self, zone_lookup_path):
        """Load zone lookup data"""
        print(f"Loading zones from {zone_lookup_path}...")

        zones_df = pd.read_csv(zone_lookup_path)

        loaded_count = 0
        for _, row in zones_df.iterrows():
            borough = row.get('Borough', 'Unknown')
            zone = row.get('Zone', 'Unknown')

            if pd.isna(borough) or borough == '':
                borough = 'Unknown'
            if pd.isna(zone) or zone == '':
                zone = 'Unknown'

            self.cursor.execute("""
                INSERT OR REPLACE INTO zones (location_id, borough, zone, service_zone)
                VALUES (?, ?, ?, ?)
            """, (
                row['LocationID'],
                borough,
                zone,
                row.get('service_zone', None)
            ))
            loaded_count += 1

        self.conn.commit()
        print(f"Loaded {loaded_count} zones")

    def load_trips(self, cleaned_data_path):
        """Load cleaned trip data in batches"""
        print(f"Loading trips from {cleaned_data_path}...")
        print("This may take 5-10 minutes for large datasets...")

        chunk_size = 10000
        total_inserted = 0

        for chunk_num, chunk in enumerate(pd.read_csv(cleaned_data_path, chunksize=chunk_size), 1):
            records = []
            for _, row in chunk.iterrows():
                records.append((
                    row.get('vendor_id', 1),
                    row['pickup_datetime'],
                    row['dropoff_datetime'],
                    int(row['passenger_count']),
                    float(row['trip_distance']),
                    int(row.get('rate_code_id', 1)),
                    row.get('store_and_fwd_flag', 'N'),
                    int(row['pickup_location_id']),
                    int(row['dropoff_location_id']),
                    int(row['payment_type']),
                    float(row['fare_amount']),
                    float(row.get('extra', 0)),
                    float(row.get('mta_tax', 0)),
                    float(row.get('tip_amount', 0)),
                    float(row.get('tolls_amount', 0)),
                    float(row.get('improvement_surcharge', 0)),
                    float(row['total_amount']),
                    float(row.get('congestion_surcharge', 0)),
                    float(row.get('trip_duration_minutes', 0)),
                    float(row.get('speed_mph', 0)) if pd.notna(
                        row.get('speed_mph')) else None,
                    float(row.get('tip_percentage', 0)),
                    float(row.get('cost_per_mile', 0)),
                    int(row.get('pickup_hour', 0)),
                    row.get('pickup_date')
                ))

            self.cursor.executemany("""
                INSERT INTO trips (
                    vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
                    trip_distance, rate_code_id, store_and_fwd_flag,
                    pickup_location_id, dropoff_location_id, payment_type_id,
                    fare_amount, extra, mta_tax, tip_amount, tolls_amount,
                    improvement_surcharge, total_amount, congestion_surcharge,
                    trip_duration_minutes, speed_mph, tip_percentage, cost_per_mile,
                    pickup_hour, pickup_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)

            total_inserted += len(records)

            if chunk_num % 10 == 0:
                self.conn.commit()
                print(
                    f"  Progress: {total_inserted:,} trips inserted...", end='\r')

        self.conn.commit()
        print(f"\nLoaded {total_inserted:,} trips into database")

    def get_summary_statistics(self):
        """Get basic statistics from the database"""
        query = """
            SELECT 
                COUNT(*) as total_trips,
                SUM(total_amount) as total_revenue,
                AVG(fare_amount) as avg_fare,
                AVG(trip_distance) as avg_distance,
                AVG(trip_duration_minutes) as avg_duration,
                SUM(passenger_count) as total_passengers,
                AVG(tip_percentage) as avg_tip_percentage,
                AVG(passenger_count) as avg_passengers
            FROM trips
        """

        self.cursor.execute(query)
        row = self.cursor.fetchone()

        return {
            'total_trips': row[0],
            'total_revenue': row[1],
            'avg_fare': row[2],
            'avg_distance': row[3],
            'avg_duration': row[4],
            'total_passengers': row[5],
            'avg_tip_percentage': row[6],
            'avg_passengers': row[7]
        }

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return []
