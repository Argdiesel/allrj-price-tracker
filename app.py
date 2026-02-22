import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PriceTrackerError(Exception):
    """Base class for other exceptions"""
    pass

class PriceNotFoundError(PriceTrackerError):
    """Raised when the price is not found"""
    def __init__(self, message):
        self.message = message
        logging.error(message)

class PriceTracker:
    def __init__(self, api_url):
        self.api_url = api_url

    def fetch_price(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()  # Raises HTTPError for bad responses
            price_data = response.json()
            if 'price' not in price_data:
                raise PriceNotFoundError('Price not found in response data.')
            return price_data['price']
        except requests.exceptions.RequestException as e:
            logging.error(f'HTTP Request failed: {e}')
            raise PriceTrackerError('Failed to fetch price data.')
        except PriceNotFoundError:
            raise
        except Exception as e:
            logging.error(f'An unexpected error occurred: {e}')
            raise PriceTrackerError('An unexpected error occurred.')

if __name__ == '__main__':
    tracker = PriceTracker('https://api.example.com/price')
    try:
        current_price = tracker.fetch_price()
        logging.info(f'Current price: {current_price}')
    except PriceTrackerError as e:
        logging.error(f'Price tracking error: {e.message}')
