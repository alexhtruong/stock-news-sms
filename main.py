import os
import requests
from twilio.rest import Client
from datetime import date
from datetime import timedelta
from newsapi import NewsApiClient

account_sid = 'AC82dd3d30de616f9259c8ceb228cdf0b9'
auth_token = os.environ.get("AUTH_TOKEN")
news_key = os.environ.get("NEWS_API_KEY")
stock_key = os.environ.get("STOCK_API_KEY")

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

yesterday = str(date.today() - timedelta(days=2))
before_yesterday = str(date.today() - timedelta(days=3))
today = date.today()
close = "4. close"


def send_articles():
    for i in range(3):  # Send messages for the first 3 articles
        title = str(all_articles["articles"][i]["title"])
        description = str(all_articles["articles"][i]["description"])
        if delta_closing > 0:
            change_symbol = "🔺"  # Up symbol
        elif delta_closing < 0:
            change_symbol = "🔻"  # Down symbol
        else:
            change_symbol = "↔️"  # No change symbol

        # Formatting the SMS message
        sms_message = f"{STOCK}: {change_symbol}{abs(delta_closing)}%\n"
        sms_message += f"Headline: {title}\n"
        sms_message += f"Brief: {description}\n"
        # sms_message = f"Source: {source}"
        print(sms_message)

        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=sms_message,
                from_='+18449983839',
                to='+14086104838',
            )
            print(f"Message sent. Status: {message.status}")
        except Exception as e:
            print(f"Error sending SMS: {e}")


try:
    # Make API request
    request = requests.get(
        f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={stock_key}')
    request.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
    data = request.json()
    y_close = float(data["Time Series (Daily)"][yesterday][close])
    y2_close = float(data["Time Series (Daily)"][before_yesterday][close])
    print(y_close)
    print(y2_close)
    delta_closing = (y2_close - y_close) / y2_close * 100

except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
except KeyError as e:
    print(f"Error accessing data: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


newsapi = NewsApiClient(api_key=news_key)
all_articles = newsapi.get_everything(q=COMPANY_NAME,
                                      from_param=before_yesterday,
                                      to=today,
                                      language='en',
                                      sort_by='popularity',
                                      page=1)


if abs(delta_closing) > 5:
    send_articles()
