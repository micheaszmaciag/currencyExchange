from celery import shared_task

@shared_task
def update_pair_history():
    '''
    Celery task to fetch and update historical exchange rates for all currency pairs.
    '''

    from .services import fetch_historical_rate
    fetch_historical_rate()

