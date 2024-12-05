# Currency Exchange REST API

## Project Overview

This Django application provides a REST API for managing and querying currency exchange rates.
The application fetches the latest rates from the NBP API (Narodowy Bank Polski)
and stores them in a local database. It also supports historical data tracking via
the admin panel, allowing users to view records from up to 30 days in the past.

## Features

### API Endpoints:

1. **`GET /currency/`**: Returns a list of all currencies in the database.

**Example Response:**

```json
[
  {
    "code": "USD"
  },
  {
    "code": "EUR"
  },
  {
    "code": "JPY"
  }
]
```

## Query Parameters:

* `code`: Filter currencies by code (e.g., `/currency/?code=USD/` or `/currency/?code=U/`
  for partial match like USD, AUD)

* `min_rate` **and** `max_rate`: Filter currencies by rate range (e.g., `/currency/?min_rate=1.0&max_rate=1.5/`)

* `sort_by` **and** `order`: Sort results by a specific field and order
  (e.g., `/currency/?sort_by=code&order=desc/`). Default order is **ascending**


- **`GET /currency/<base_currency>/<quote_currency>/`**: Fetches the exchange rate for a given currency pair.

- **Example Request:** **`/currency/EUR/USD/`**

**Example Response**

```json
{
  "currency_pair": "EURUSD",
  "exchange_rate": 1.034
}
```

## Admin interface:

The admin panel includes functionality for viewing and managing historical
exchange rates. Filters for **date ranges** and **currency pair** names simplify record navigation.

## Technologies Used

* **Django:** Web framework used to create application.

* **Django REST Framework:** Used to implement the REST API.

* **SQLite:** Local database used in project.

* **Requests:** Python library used to make HTTP requests to the external NBP AP.

* **NBP API:** External API Narodowego Banku Polskiego used to fetch actual and historical rates.

* **Pytest:** Tool used to test application.

* **Django-admin-rangefilter:** A library that adds date range filter to the admin interface

* **Pandas:** Used to handle calendar-based working date calculations.

## Installation and Setup

1. Clone the repository:

```bash
git clone 
```

2. Install dependencies:

```shell
pip install -r requirements.txt
```

3. Apply Database migrations:

```shell
python manage.py migrate
```

4. Load actual currency rates to the database:

```shell
python manage.py load_rates
```

5. Start the development server:

```bash
python manage.py runserver
```

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

### Micheasz Maciąg
