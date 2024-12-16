import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from currencyData.models import Currency


# # USE pytest.mark.django_db to inform pytest-django that have to work with database
# @pytest.mark.django_db
# def test_get_currency_endpoint():
#     """Test fetching all currencies from the endpoint."""
#     # create an API environment to send request without starting server
#     client = APIClient()
#
#     Currency.objects.create(code='USD', rate_currency=4.0)
#     Currency.objects.create(code='EUR', rate_currency=4.30)
#
#     response = client.get(reverse('getCurrency'))
#     assert response.status_code == 200
#     assert len(response.data) == 2
#     codes = [currency['code'] for currency in response.data]
#     assert set(codes) == {'USD', 'EUR'}
#
#
# @pytest.mark.django_db
# def test_get_currency_filter_by_code():
#     """Test filtering currencies by code or partial match."""
#     client = APIClient()
#
#     Currency.objects.create(code='USD', rate_currency=4.0)
#     Currency.objects.create(code='EUR', rate_currency=4.30)
#     Currency.objects.create(code='AUD', rate_currency=2.20)
#     Currency.objects.create(code='HUF', rate_currency=0.0010)
#     expected_currency = ['USD', 'AUD', 'EUR', 'HUF']
#
#     response = client.get(reverse('getCurrency') + '?code=USD')
#
#
#     assert response.status_code == 200
#     assert len(response.data) == 1
#     assert response.data[0]['code'] == 'USD'
#
#     response_one_letter = client.get(reverse('getCurrency') + '?code=u')
#
#     actual_currency = [item['code'] for item in response_one_letter.data]
#     assert sorted(actual_currency) == sorted(expected_currency)
#
# @pytest.mark.django_db
# def test_get_currency_filter_by_min_rate():
#     """Test filtering currencies by minimum rate."""
#     client = APIClient()
#     Currency.objects.create(code='USD', rate_currency=4.0)
#     Currency.objects.create(code='EUR', rate_currency=4.30)
#     Currency.objects.create(code='JPY', rate_currency=0.035)
#
#     response = client.get(reverse('getCurrency') + '?min_rate=0.04')
#
#     assert response.status_code == 200
#     codes = [currency['code'] for currency in response.data]
#     assert len(codes) == 2
#     assert set(codes) == {'USD', 'EUR'}
#
#
# @pytest.mark.django_db
# def test_get_currency_filter_by_min_and_max_rate():
#     """Test filtering currencies by minimum and maximum rate."""
#     client = APIClient()
#     Currency.objects.create(code='USD', rate_currency=4.0)
#     Currency.objects.create(code='EUR', rate_currency=4.30)
#     Currency.objects.create(code='JPY', rate_currency=0.035)
#
#     response = client.get(reverse('getCurrency') + '?min_rate=0.04&max_rate=4.10')
#
#     assert response.status_code == 200
#     codes = [currency['code'] for currency in response.data]
#     assert len(codes) == 1
#     assert codes[0] == 'USD'
#
#
# @pytest.mark.django_db
# def test_get_currency_filter_no_results():
#     """Test filtering currencies with no matches."""
#     client = APIClient()
#     Currency.objects.create(code='USD', rate_currency=4.0)
#     Currency.objects.create(code='EUR', rate_currency=4.30)
#     Currency.objects.create(code='JPY', rate_currency=0.035)
#
#     response = client.get(reverse('getCurrency') + '?min_rate=4.50&max_rate=5.0')
#
#     assert response.status_code == 200
#     assert len(response.data) == 0
#
#
# @pytest.mark.django_db
# def test_get_currency_filter_min_rate_greater_than_max_rate():
#     """Test error for min_rate greater than max_rate."""
#     client = APIClient()
#     response = client.get(reverse('getCurrency') + '?min_rate=5&max_rate=3')
#
#     assert response.status_code == 400
#     assert 'error' in response.data
#
#
#
# @pytest.mark.django_db
# def test_get_currency_invalid_filter():
#     """Test error for invalid filter input."""
#     Currency.objects.create(code='USD', rate_currency=4.0)
#
#     client = APIClient()
#     response = client.get(reverse('getCurrency') + '?min_rate=abc')
#
#     assert response.status_code == 400
#     assert 'error' in response.data
#
#
@pytest.mark.django_db
def test_get_currency_rate():
    """Test exchange rate calculation between two currencies."""
    Currency.objects.create(code='USD', rate_currency=4.0)
    Currency.objects.create(code='EUR', rate_currency=4.30)

    client = APIClient()
    response = client.get(reverse('getCurrencyRate', args=['USD', 'EUR']))

    assert response.status_code == 200
    assert response.data['currency_pair'] == 'USDEUR'
    assert response.data['exchange_rate'] == 0.9302325581395349


@pytest.mark.django_db
def test_get_currency_rate_invalid_currency():
    """Test error for exchange rate with invalid currency."""
    Currency.objects.create(code='USD', rate_currency=4.0)

    client = APIClient()
    response = client.get(reverse('getCurrencyRate', args=['USD', 'JPY']))

    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_get_currency_rate_transaction_saved():
    """Test saving transaction after successful exchange rate fetch."""
    Currency.objects.create(code='USD', rate_currency=4.0)
    Currency.objects.create(code='EUR', rate_currency=4.30)

    client = APIClient()
    response = client.get(reverse('getCurrencyRate', args=['USD', 'EUR']))

    assert response.status_code == 200



@pytest.mark.django_db
def test_get_currency_rate_zero_devision():
    """Test error for division by zero in exchange rate calculation."""
    Currency.objects.create(code='USD', rate_currency=4.0)
    Currency.objects.create(code='JPY', rate_currency=0.0)

    client = APIClient()
    response = client.get(reverse('getCurrencyRate', args=['USD', 'JPY']))

    assert response.status_code == 400
    assert 'error' in response.data
