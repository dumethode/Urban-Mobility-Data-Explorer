# NYC Taxi Data Explorer

A full-stack web application for analyzing 7.4 million NYC taxi trips from January 2019, revealing urban mobility patterns through interactive visualizations and data insights.

![Dashboard Preview](https://img.shields.io/badge/Status-Production-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Team 6**: Methode Duhujubumwe | Cindy Saro Teta | MUTONI Keira | Sylivie TUMUKUNDE

---

## Live Demo

**Frontend**: https://dumethode.github.io/nyc-taxi-explorer/

**Note**: The live site displays the user interface. For complete functionality with real-time data, follow the local installation instructions below.

**Video Walkthrough**: [Add your YouTube link here]

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Custom Algorithm](#custom-algorithm)
- [Data Insights](#data-insights)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Data Processing**: Clean and process 7.6M raw taxi trip records
- **Star Schema Database**: Normalized SQLite database with optimized indexes
- **REST API**: 8 endpoints serving statistics, filtering, and ranking
- **Custom Algorithm**: QuickSort implementation (O(n log n)) for trip ranking
- **Interactive Dashboard**: Real-time visualizations with Chart.js
- **Advanced Filtering**: Filter by borough, fare, payment type
- **Automated Insights**: Generate meaningful patterns from data
- **Responsive Design**: Mobile-friendly interface with ALU branding

---

## Tech Stack

**Backend**:
- Python 3.8+
- Flask 3.0+ (REST API)
- SQLite (Database)
- Pandas (Data processing)
- Custom QuickSort algorithm

**Frontend**:
- HTML5
- CSS3 (Vanilla, no frameworks)
- JavaScript (ES6+)
- Chart.js 4.4.0 (Visualizations)

**Design**:
- ALU Colors: #0066CC (Blue), #FF6B35 (Orange)
- Montserrat Font Family
- Responsive Grid Layout

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
  ```bash
  python3 --version  # Should show 3.8.0 or higher
  ```

- **pip** (Python package installer)
  ```bash
  pip3 --version
  ```

- **2GB free disk space** (for database and processed data)

- **Internet connection** (for initial data download)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/dumethode/nyc-taxi-explorer.git
cd nyc-taxi-explorer
```

### Step 2: Download Required Data

**Download the NYC Taxi Trip Data** (required, ~700MB):

```bash
# Go to the data directory
cd data/raw

# Download using curl (Mac/Linux)
curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2019-01.parquet

# OR download using wget
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2019-01.parquet
```

**Alternative**: Download manually from [NYC TLC Website](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) and save to `data/raw/`

**Verify**: The file should be approximately 700MB and named `yellow_tripdata_2019-01.parquet`

The zone lookup file is already included in the repository.

### Step 3: Set Up Python Environment

```bash
# Navigate to backend directory
cd ../../backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 4: Install Python Dependencies

```bash
# Make sure virtual environment is activated (you should see (venv))
pip install Flask Flask-CORS pandas pyarrow

# Verify installation
pip list
```

Expected packages:
- Flask (3.0+)
- Flask-CORS (4.0+)
- pandas (2.2+)
- pyarrow (17.0+)

### Step 5: Process Data and Build Database

**This step takes 15-20 minutes** to process 7.6 million records.

```bash
# Run the setup script
python3 setup.py
```

You'll be prompted for file paths. Enter:

```
Enter path to raw trip data file: ../data/raw/yellow_tripdata_2019-01.parquet
Enter path to zone lookup CSV: ../data/raw/taxi_zone_lookup.csv
```

**What happens during setup**:
1. Loads 7.6M trip records
2. Cleans data (handles missing values, removes outliers)
3. Creates 6 derived features (duration, speed, tip percentage, etc.)
4. Merges with zone lookup data
5. Creates SQLite database with star schema
6. Loads processed data (7.4M records)
7. Creates indexes for fast queries

**Expected output**:
```
✓ Loaded 7,667,792 records
✓ Cleaned to 7,461,945 records (97% retention)
✓ Database created successfully
✓ Total revenue: $115,218,316.52
```

---

## Running the Application

### Start Backend (Terminal 1)

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment if not already active
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Start Flask server
python3 app.py
```

**Expected output**:
```
================================================================================
NYC TAXI DATA EXPLORER API
================================================================================
Starting Flask server...
API will be available at: http://localhost:5000

Available endpoints:
  GET  /api/trips
  GET  /api/trips/ranked
  GET  /api/stats
  ...
================================================================================
 * Running on http://127.0.0.1:5000
```

**Keep this terminal running!**

### Start Frontend (Terminal 2)

Open a **new terminal window**:

```bash
# Navigate to frontend directory
cd frontend

# Start simple HTTP server
python3 -m http.server 8000
```

**Expected output**:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

**You should see**:
- Dashboard with 4 stat cards showing trip data
- Interactive charts (hourly trips, borough revenue, payment methods, distances)
- Filter controls (borough, fare range, payment type)
- Trip ranking table with custom algorithm
- Three automated insights

---

## Project Structure

```
nyc-taxi-explorer/
├── backend/
│   ├── app.py                    # Flask REST API (8 endpoints)
│   ├── database.py               # Database operations & queries
│   ├── data_processor.py         # Data cleaning & feature engineering
│   ├── custom_algorithm.py       # QuickSort implementation
│   ├── setup.py                  # Automated setup script
│   └── requirements.txt          # Python dependencies
│
├── frontend/
│   ├── index.html               # Main dashboard
│   ├── css/
│   │   └── styles.css           # ALU-branded styling
│   └── js/
│       ├── main.js              # Application logic
│       ├── api.js               # API communication
│       └── charts.js            # Chart.js visualizations
│
├── data/
│   ├── raw/                     # Original data files
│   ├── processed/               # Cleaned data
│   └── database/                # SQLite database
│
├── database_schema.sql          # Database schema definition
└── README.md                    # This file
```

---

## 🔌 API Documentation

Base URL: `http://localhost:5000`

### Available Endpoints

#### 1. Get Summary Statistics
```http
GET /api/stats
```

**Response**:
```json
{
  "success": true,
  "statistics": {
    "total_trips": 7461945,
    "total_revenue": 115218316.52,
    "avg_fare": 15.44,
    "avg_distance": 2.83
  }
}
```

#### 2. Get Hourly Statistics
```http
GET /api/stats/hourly
```

Returns trip counts and averages for each hour (0-23).

#### 3. Get Borough Statistics
```http
GET /api/stats/borough
```

Returns trip counts, revenue, and averages by NYC borough.

#### 4. Get Payment Statistics
```http
GET /api/stats/payment
```

Returns trip counts and tip averages by payment method.

#### 5. Get Filtered Trips
```http
GET /api/trips?min_fare=10&max_fare=50&pickup_borough=Manhattan&limit=100
```

**Query Parameters**:
- `min_fare`: Minimum fare amount
- `max_fare`: Maximum fare amount
- `pickup_borough`: Manhattan, Brooklyn, Queens, Bronx, Staten Island
- `dropoff_borough`: Same options as pickup
- `payment_type`: 1 (Credit), 2 (Cash), 3 (No Charge), 4 (Dispute)
- `limit`: Number of results (default: 100)

#### 6. Get Ranked Trips (Custom Algorithm)
```http
GET /api/trips/ranked?rank_by=fare&order=desc&limit=20
```

**Query Parameters**:
- `rank_by`: fare, distance, duration, tip
- `order`: asc (ascending) or desc (descending)
- `limit`: Number of results (default: 20)

**Response includes algorithm performance metrics**:
```json
{
  "success": true,
  "algorithm_stats": {
    "comparisons": 847,
    "swaps": 234
  },
  "trips": [...]
}
```

#### 7. Get Top Routes
```http
GET /api/routes/top?limit=10
```

Returns most popular pickup-dropoff combinations.

#### 8. Get All Zones
```http
GET /api/zones
```

Returns all 265 NYC taxi zones with borough information.

---

## Custom Algorithm

### QuickSort Implementation

We implemented QuickSort from scratch without using Python's built-in `sorted()` or `sort()` functions.

**Key Features**:
- Partition-based divide-and-conquer approach
- In-place sorting with minimal memory overhead
- Flexible key functions for different ranking criteria
- Performance tracking (comparisons, swaps)

**Complexity**:
- Time: O(n log n) average, O(n²) worst case
- Space: O(log n) for recursion stack

**Code Location**: `backend/custom_algorithm.py`

---

## Data Insights

Our analysis revealed three key insights:

### 1. Peak Hour Demand
- **Busiest**: 6 PM with 500,967 trips
- **Quietest**: 4 AM with 58,535 trips
- **Insight**: Evening rush hour shows 8.5x demand vs early morning

### 2. Manhattan Dominance
- **Revenue Share**: 82% of total revenue ($94.5M)
- **Average Trip**: Queens trips longer ($18.50) but less frequent
- **Insight**: Manhattan's economic center status drives taxi industry

### 3. Digital Payment Effects
- **Credit Card Tips**: 21.7% average
- **Cash Tips**: 0% (not recorded in system)
- **Insight**: Payment technology significantly impacts driver earnings

---

## 🐛 Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'flask'"**
```bash
# Solution: Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Verify
pip list | grep Flask
```

**"File not found: yellow_tripdata_2019-01.parquet"**
```bash
# Solution: Download data file
cd data/raw
curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2019-01.parquet
```

**"Address already in use (port 5000)"**
```bash
# Solution 1: Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Solution 2: Use different port
# Edit app.py, change port to 5001
python3 app.py
```

**"Database locked"**
```bash
# Solution: Close any DB browser tools and restart Flask
rm data/database/taxi_data.db
python3 setup.py
```

### Frontend Issues

**"Failed to fetch" or CORS errors**
```bash
# Solution: Make sure backend is running
# Check: http://localhost:5000/api/stats in browser
# Should see JSON response

# Verify Flask-CORS is installed
pip list | grep Flask-CORS
```

**Charts not displaying**
```bash
# Solution 1: Clear browser cache
# Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

# Solution 2: Check browser console (F12)
# Look for JavaScript errors
```

**"No data displayed"**
```bash
# Solution: Wait 30 seconds after starting backend
# Database queries can be slow on first run
# Refresh page
```

---

## License

This project was created for academic purposes at African Leadership University.

**Data Source**: NYC Taxi & Limousine Commission (TLC)

---

## Acknowledgments

- NYC TLC for providing open taxi trip data
- Chart.js for visualization library
- Flask team for excellent web framework
- ALU faculty for project guidance

---

**Built by Team 6**

*Methode Duhujubumwe | Cindy Saro Teta | MUTONI Keira | Sylivie TUMUKUNDE*
