"""
Taxi Data Processor
Cleans and validates NYC taxi trip data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os


class TaxiDataProcessor:
    """Process and clean NYC taxi trip data"""

    def __init__(self, raw_data_path, zone_lookup_path):
        self.raw_data_path = raw_data_path
        self.zone_lookup_path = zone_lookup_path
        self.quality_log = []

    def log_quality_issue(self, issue_type, count, description):
        """Log data quality issues"""
        self.quality_log.append({
            'issue_type': issue_type,
            'count': count,
            'description': description
        })

    def load_raw_data(self):
        """Load raw trip data from CSV or Parquet"""
        print(f"Loading data from {self.raw_data_path}...")

        if self.raw_data_path.endswith('.parquet'):
            df = pd.read_parquet(self.raw_data_path)
        else:
            chunk_size = 100000
            chunks = []
            total_rows = 0

            for chunk in pd.read_csv(self.raw_data_path, chunksize=chunk_size, low_memory=False):
                chunks.append(chunk)
                total_rows += len(chunk)
                print(f"  Loaded {total_rows:,} rows...", end='\r')

            df = pd.concat(chunks, ignore_index=True)
            print(f"\nLoaded {len(df):,} total rows")

        return df

    def load_zone_lookup(self):
        """Load zone lookup data"""
        print(f"Loading zone lookup from {self.zone_lookup_path}...")
        zones = pd.read_csv(self.zone_lookup_path)
        print(f"Loaded {len(zones)} zones")
        return zones

    def clean_data(self, df):
        """Clean and validate trip data"""
        print("\nCleaning data...")
        original_count = len(df)

        column_mapping = {
            'tpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime',
            'RatecodeID': 'rate_code_id',
            'PULocationID': 'pickup_location_id',
            'DOLocationID': 'dropoff_location_id',
            'VendorID': 'vendor_id'
        }
        df = df.rename(columns=column_mapping)

        df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
        df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

        required_fields = ['pickup_datetime', 'dropoff_datetime', 'pickup_location_id',
                           'dropoff_location_id', 'total_amount']
        missing_before = df[required_fields].isnull().any(axis=1).sum()
        df = df.dropna(subset=required_fields)
        if missing_before > 0:
            self.log_quality_issue('missing_data', missing_before,
                                   'Records with missing critical fields')

        invalid_times = (df['dropoff_datetime'] <= df['pickup_datetime']).sum()
        df = df[df['dropoff_datetime'] > df['pickup_datetime']]
        if invalid_times > 0:
            self.log_quality_issue('invalid_datetime', invalid_times,
                                   'Pickup time after dropoff time')

        invalid_distance = (df['trip_distance'] <= 0).sum()
        df = df[df['trip_distance'] > 0]
        if invalid_distance > 0:
            self.log_quality_issue('invalid_distance', invalid_distance,
                                   'Zero or negative trip distance')

        invalid_fare = (df['fare_amount'] <= 0).sum()
        df = df[df['fare_amount'] > 0]
        if invalid_fare > 0:
            self.log_quality_issue('invalid_fare', invalid_fare,
                                   'Zero or negative fare amount')

        df['passenger_count'] = df['passenger_count'].fillna(1)
        invalid_passengers = ((df['passenger_count'] <= 0) | (
            df['passenger_count'] > 6)).sum()
        df.loc[df['passenger_count'] <= 0, 'passenger_count'] = 1
        df.loc[df['passenger_count'] > 6, 'passenger_count'] = 6
        if invalid_passengers > 0:
            self.log_quality_issue('invalid_passengers', invalid_passengers,
                                   'Adjusted unrealistic passenger counts')

        extreme_distance = (df['trip_distance'] > 100).sum()
        df = df[df['trip_distance'] <= 100]
        if extreme_distance > 0:
            self.log_quality_issue('extreme_distance', extreme_distance,
                                   'Trips over 100 miles removed')

        extreme_fare = (df['total_amount'] > 500).sum()
        df = df[df['total_amount'] <= 500]
        if extreme_fare > 0:
            self.log_quality_issue('extreme_fare', extreme_fare,
                                   'Fares over $500 removed')

        cleaned_count = len(df)
        removed_count = original_count - cleaned_count
        removal_pct = (removed_count / original_count) * 100

        print(f"Cleaned {original_count:,} -> {cleaned_count:,} records")
        print(
            f"Removed {removed_count:,} ({removal_pct:.2f}%) invalid records")

        return df

    def enrich_data(self, df, zones):
        """Add derived fields and join with zone data"""
        print("\nEnriching data...")

        df['trip_duration_minutes'] = (
            (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60
        )

        df['speed_mph'] = df['trip_distance'] / \
            (df['trip_duration_minutes'] / 60)
        df.loc[df['speed_mph'] > 100, 'speed_mph'] = np.nan

        df['tip_percentage'] = (
            df['tip_amount'] / df['fare_amount'] * 100).round(2)
        df.loc[df['tip_percentage'] < 0, 'tip_percentage'] = 0
        df.loc[df['tip_percentage'] > 100, 'tip_percentage'] = 100

        df['cost_per_mile'] = (df['total_amount'] /
                               df['trip_distance']).round(2)

        df['pickup_hour'] = df['pickup_datetime'].dt.hour
        df['pickup_date'] = df['pickup_datetime'].dt.date

        zone_cols = ['LocationID', 'Borough', 'Zone']
        zones_clean = zones[zone_cols].copy()
        zones_clean.columns = ['location_id', 'borough', 'zone']

        df = df.merge(
            zones_clean,
            left_on='pickup_location_id',
            right_on='location_id',
            how='left',
            suffixes=('', '_pickup')
        )
        df = df.rename(
            columns={'borough': 'pickup_borough', 'zone': 'pickup_zone'})
        df = df.drop(columns=['location_id'])

        df = df.merge(
            zones_clean,
            left_on='dropoff_location_id',
            right_on='location_id',
            how='left',
            suffixes=('', '_dropoff')
        )
        df = df.rename(
            columns={'borough': 'dropoff_borough', 'zone': 'dropoff_zone'})
        df = df.drop(columns=['location_id'])

        # Remove trips with unknown zones (invalid location IDs)
        before_zone_filter = len(df)
        df = df[
            (df['pickup_borough'].notna()) &
            (df['dropoff_borough'].notna()) &
            (df['pickup_borough'] != 'Unknown') &
            (df['dropoff_borough'] != 'Unknown')
        ]
        removed_unknown_zones = before_zone_filter - len(df)
        if removed_unknown_zones > 0:
            self.log_quality_issue('unknown_zones', removed_unknown_zones,
                                   'Trips with invalid location IDs removed')

        print(f"Added derived fields and zone information")

        return df

    def save_cleaned_data(self, df, output_path):
        """Save cleaned data to CSV"""
        print(f"\nSaving cleaned data to {output_path}...")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        df.to_csv(output_path, index=False)
        print(f"Saved {len(df):,} records")

        log_path = output_path.replace('.csv', '_quality_log.txt')
        with open(log_path, 'w') as f:
            f.write("DATA QUALITY LOG\n")
            f.write("=" * 80 + "\n\n")
            for log in self.quality_log:
                f.write(f"{log['issue_type']}: {log['count']:,} records\n")
                f.write(f"  {log['description']}\n\n")
        print(f"Quality log saved to {log_path}")

    def process_all(self, output_path):
        """Run complete data processing pipeline"""
        print("\n" + "=" * 80)
        print("DATA PROCESSING PIPELINE")
        print("=" * 80)

        df = self.load_raw_data()
        zones = self.load_zone_lookup()

        df = self.clean_data(df)
        df = self.enrich_data(df, zones)

        self.save_cleaned_data(df, output_path)

        print("\n" + "=" * 80)
        print("DATA PROCESSING COMPLETE")
        print("=" * 80)

        return df
