#!/usr/bin/env python3
"""
NYC Taxi Data Explorer - Automated Setup Script
Processes raw CSV data and populates SQLite database
"""

from data_processor import TaxiDataProcessor
from database import DatabaseManager
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 80)
    print("NYC TAXI DATA EXPLORER - AUTOMATED SETUP")
    print("=" * 80)
    print()

    project_root = Path(__file__).parent.parent
    raw_data = project_root / "data" / "raw" / "yellow_tripdata_2019-01.csv"
    zone_lookup = project_root / "data" / "raw" / "taxi_zone_lookup.csv"
    output_csv = project_root / "data" / "processed" / "cleaned_taxi_data.csv"
    db_path = project_root / "data" / "database" / "taxi_data.db"

    if not raw_data.exists():
        print(f"Error: Raw data file not found: {raw_data}")
        return

    if not zone_lookup.exists():
        print(f"Error: Zone lookup file not found: {zone_lookup}")
        return

    print(f"Raw data: {raw_data}")
    print(f"Zone lookup: {zone_lookup}")
    print(f"Database: {db_path}")
    print()

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("STEP 1: PROCESSING RAW DATA")
    print("=" * 80)
    print()

    processor = TaxiDataProcessor(str(raw_data), str(zone_lookup))
    processor.process_all(str(output_csv))

    print()
    print("=" * 80)
    print("STEP 2: SETTING UP DATABASE")
    print("=" * 80)
    print()

    db = DatabaseManager(str(db_path))
    db.connect()

    print("Creating database schema...")
    db.create_schema()

    print("Loading taxi zones...")
    db.load_zones(str(zone_lookup))

    print("Loading trip data (this will take 5-10 minutes for 7.6M rows)...")
    db.load_trips(str(output_csv))

    print()
    print("=" * 80)
    print("STEP 3: VERIFICATION")
    print("=" * 80)
    print()

    stats = db.get_summary_statistics()

    print("Database Statistics:")
    print(f"  Total trips: {stats['total_trips']:,}")
    print(f"  Total revenue: ${stats['total_revenue']:,.2f}")
    print(f"  Average fare: ${stats['avg_fare']:.2f}")
    print(f"  Average distance: {stats['avg_distance']:.2f} miles")
    print(f"  Average duration: {stats['avg_duration']:.1f} minutes")

    db.close()

    print()
    print("=" * 80)
    print("SETUP COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Start the backend:")
    print("   cd backend")
    print("   source venv/bin/activate")
    print("   python3 app.py")
    print()
    print("2. Start the frontend (new terminal):")
    print("   cd frontend")
    print("   python3 -m http.server 8000")
    print()
    print("3. Open browser: http://localhost:8000")
    print()
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
