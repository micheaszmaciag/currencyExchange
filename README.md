# Currency Exchange REST API

## Project Overview

This Django application provides a REST API for managing and querying currency exchange rates.
The application fetches the latest rates from the NBP API (Narodowy Bank Polski)
and stores them in a local database. It also supports historical data tracking via
the admin panel, allowing users to view records from up to 30 days in the past while 
ignoring weekends when the market is closed. 

With Docker, Celery, and Redis integrated, the application provides efficient background 
processing for tasks such as fetching and storing historical exchange rates.

## Features

### API Endpoints:

1. **`GET /currency/<base_currency>/<quote_currency>/`**: Returns a currency pair and rates of asked currencies.

**Example Request:** ``/currency/EUR/USD/``

**Example Response:**

```json
{
  "currency_pair": "EURUSD",
  "exchange_rate": 1.034
}
```

## Admin interface:

The admin panel includes advanced functionality for managing and 
analyzing historical exchange rates. Key features include:

* **Filters:**
    * Filter records by **date ranges** (using ``django-admin-rangefilter``)
    * Filter records by **currency pair names** for easy navigation.

* **Export to Excel:**
    * Export filtered currency exchange rates directly to an Excel file for further analysis.
    * To export, select a currency pair from the filters and click 
      the "Export to Excel" button in the admin interface.
  
* **Enhanced Display:**
  * View detailed fields such as exchange rate, currency pair, and date directly in the admin panel.


## Technologies Used

* **Django:** Web framework used to create application.

* **Django REST Framework:** Used to implement the REST API.

* **SQLite:** Local database used in project.

* **Requests:** Python library used to make HTTP requests to the external NBP AP.

* **NBP API:** External API Narodowego Banku Polskiego used to fetch actual and historical rates.

* **Pytest:** Tool used to test application.

* **Django-admin-rangefilter:** A library that adds date range filter to the admin interface

* **Pandas:** Handles calendar-based working days, excluding weekends when the market is closed

* **Django Cache:** Used to optimize performance by caching frequently accessed exchange rate data, reducing API calls to the NBP API.

* **Docker:** Containerization for consistent runtime environments.

* **Redis:** Message broker used with Celery for task processing.

* **Celery:** Handles background tasks like fetching and saving historical exchange rates.

## Installation and Setup

1. **Clone the repository:**

```bash
git clone https://github.com/micheaszmaciag/currencyExchange
```

2. **Install dependencies:**

```shell
pip install -r requirements.txt
```

3. **Set your SECRET_KEY:**

    Open ``settings.py`` and set a unique, secret value for ``SECRET_KEY``. For example:

```bash
  SECRET_KEY = 'your-secret-key-and-unique-key' 
```

4. **Apply Database migrations:**

```shell
python manage.py migrate
```

5. **Load actual currency rates to the database:**

```shell
python manage.py load_rates
```

6. **Create a superuser to access the admin panel (recommended):**

   ```bash
   python manage.py createsuperuser
   ```

### Setting up Docker, Redis, and Celery

**Note:** These steps are required before running the development server. Without Redis and Celery, background tasks (e.g., fetching historical exchange rates) will not function properly.

1. **Install Docker (if not already installed):**
   - Follow the official Docker installation guide for your platform:  
     [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

2. **Run Redis in a Docker container:**
   - Run the following command to start a Redis container named `fetchDataRedis` on port `6379`:
     ```bash
     docker run -d -p 6379:6379 --name fetchDataRedis redis
     ```
   - After running this, you can verify Redis is running by:
     ```bash
     docker ps
     ```
   - In the Django settings (`settings.py`), ensure your Celery settings point to the local Redis:
     ```python
     CELERY_BROKER_URL = 'redis://localhost:6379/0'
     CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
     ```

3. **Start the Celery worker:** Open a new terminal window/tab in your project directory and run:
   ```bash
   celery -A currencyExchange worker --loglevel=info --pool=solo
   ```
   This will start a Celery worker that processes background tasks.


7. **Start the development server:**
   ```bash
   python manage.py runserver

## Running Test:

Run the following command to execute all tests:

```bash
pytest
```

## Design Decisions and Justifications:

### Why Use the NBP API?

The **NBP API** offers:

* **Ease of use:** No need for API keys, and it supports both real-time and historical data (up to 91 days).

* **Reliability:** Official source for exchange rates in Poland.

* **Simplicity for Polish users:** PLN-based rates are directly available.

### **Why Use** `django-admin-rangefilter`?:

This library enhances the admin interface by enabling users to filter
records by date range, which is particularly useful for managing historical currency data.

## AUTHOR

## Micheasz Maciąg
