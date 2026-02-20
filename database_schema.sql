CREATE TABLE IF NOT EXISTS zones (
    location_id INTEGER PRIMARY KEY,
    borough TEXT NOT NULL,
    zone TEXT NOT NULL,
    service_zone TEXT
);


CREATE TABLE IF NOT EXISTS dates (
    date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS rate_codes (
    rate_code_id INTEGER PRIMARY KEY,
    rate_name TEXT NOT NULL
);

INSERT OR IGNORE INTO rate_codes (rate_code_id, rate_name) VALUES
(1, 'Standard rate'),
(2, 'JFK'),
(3, 'Newark'),
(4, 'Nassau or Westchester'),
(5, 'Negotiated fare'),
(6, 'Group ride');


CREATE TABLE IF NOT EXISTS payment_types (
    payment_type_id INTEGER PRIMARY KEY,
    payment_name TEXT NOT NULL
);

INSERT OR IGNORE INTO payment_types (payment_type_id, payment_name) VALUES
(1, 'Credit card'),
(2, 'Cash'),
(3, 'No charge'),
(4, 'Dispute'),
(5, 'Unknown'),
(6, 'Voided trip');


CREATE TABLE IF NOT EXISTS trips (
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
);


CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_datetime ON trips(dropoff_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_location ON trips(pickup_location_id);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_location ON trips(dropoff_location_id);
CREATE INDEX IF NOT EXISTS idx_trips_fare_amount ON trips(fare_amount);
CREATE INDEX IF NOT EXISTS idx_trips_trip_distance ON trips(trip_distance);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_hour ON trips(pickup_hour);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_date ON trips(pickup_date);
CREATE INDEX IF NOT EXISTS idx_zones_borough ON zones(borough);