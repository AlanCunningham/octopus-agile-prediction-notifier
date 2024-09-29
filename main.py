import settings
import apprise
import requests
from datetime import datetime


def send(title, message):
    """
    Sends a message using Apprise
    :param title: The string for the title of the notification
    :param message: The string of the message to send
    """
    if settings.apprise_services:
        # Create an Apprise instance
        app = apprise.Apprise()
        for service in settings.apprise_services:
            app.add(service)

        app.notify(
            body=message,
            title=title,
        )


def main():
    request_url = f"https://agilepredict.com/api/{settings.region_code}"
    predictions = requests.get(request_url).json()
    prices = predictions[0]["prices"]

    for price in prices:
        if (
            price["agile_pred"] < settings.price_low_threshold
            or price["agile_low"] < settings.price_low_threshold
        ):
            # Cheap period found - send a notification and break out
            formatted_date = datetime.strftime(
                datetime.fromisoformat(price["date_time"]), "%A %d %B at %H:%M"
            )
            send(
                title="🐙 Octopus Agile: Cheap rate coming up",
                message=f"{formatted_date}.\nBetween {price['agile_pred']}p and {price['agile_low']}p.",
            )
            break


if __name__ == "__main__":
    main()
