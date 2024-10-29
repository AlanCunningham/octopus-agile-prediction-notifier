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
    cheap_prices = []
    cheap_period_started = False
    cheapest_price = 0

    # Sometimes the highest prediction can be vastle different to the
    # default and lowest prediction. We'll accept high predictions as long as
    # they're not this many pence above the price_low_threshold.
    high_prediction_acceptance_excess = settings.price_low_threshold + 5

    for price in prices:
        if cheap_period_started == False:
            if (
                price["agile_pred"] <= settings.price_low_threshold
                and price["agile_low"] <= settings.price_low_threshold
                and price["agile_high"] <= high_prediction_acceptance_excess
            ):
                print(
                    f"Cheap start: {price['date_time']}: Predicted: {price['agile_pred']}p / Low: {price['agile_low']}p / High: {price['agile_high']}p"
                )
                cheap_period_started = True
                cheapest_price = price["agile_low"]

                try:
                    formatted_start_date = datetime.strftime(
                        datetime.fromisoformat(price["date_time"]), "%A %-d %B"
                    )
                    formatted_start_time = datetime.strftime(
                        datetime.fromisoformat(price["date_time"]), "%H:%M"
                    )
                except ValueError:
                    # print("Correcting datetime format")
                    corrected_datetime_format = datetime.strptime(
                        price["date_time"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    formatted_start_date = datetime.strftime(
                        corrected_datetime_format, "%A %-d %B"
                    )
                    formatted_start_time = datetime.strftime(
                        corrected_datetime_format, "%H:%M"
                    )

        elif cheap_period_started == True:
            # Update the cheapest price of this current cheap period
            if price["agile_low"] < cheapest_price:
                cheapest_price = price["agile_low"]

            if (
                price["agile_pred"] >= settings.price_low_threshold
                and price["agile_low"] >= settings.price_low_threshold
                and price["agile_high"] >= high_prediction_acceptance_excess
            ):
                # Cheap period has finished
                print(
                    f"Cheap end: {price['date_time']}: Price: {price['agile_pred']}p / {price['agile_low']}p / High: {price['agile_high']}p\n"
                )
                cheap_period_started = False

                # For some reason, not all times include the timezone
                try:
                    formatted_end_date = datetime.strftime(
                        datetime.fromisoformat(price["date_time"]), "%A %-d %B"
                    )
                    formatted_end_time = datetime.strftime(
                        datetime.fromisoformat(price["date_time"]), "%H:%M"
                    )
                except ValueError:
                    # print("Correcting datetime format")
                    corrected_datetime_format = datetime.strptime(
                        price["date_time"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    formatted_end_date = datetime.strftime(
                        corrected_datetime_format, "%A %-d %B"
                    )
                    formatted_end_time = datetime.strftime(
                        corrected_datetime_format, "%H:%M"
                    )

                # We've got a start and period for the cheap rate - add to the
                # cheap prices list
                if cheapest_price < 0:
                    cheapest_price = f"{cheapest_price}p/kWh ⭐"
                else:
                    cheapest_price = f"{cheapest_price}p/kWh"

                # A rather hacky way of adding the suffix to the date (now that we have it)
                split_date = formatted_start_date.split()
                if 4 <= int(split_date[1]) <= 20 or 24 <= int(split_date[1]) <= 30:
                    suffix = "th"
                else:
                    suffix = ["st", "nd", "rd"][int(split_date[1]) % 10 - 1]

                start_date_with_suffix = (
                    f"{split_date[0]} {split_date[1]}{suffix} {split_date[2]}"
                )

                cheap_prices.append(
                    {
                        "start_date": start_date_with_suffix,
                        "start_time": formatted_start_time,
                        "end_date": formatted_end_date,
                        "end_time": formatted_end_time,
                        "price": cheapest_price,
                    }
                )

    if cheap_prices:
        notification_message = ""
        for cheap_price in cheap_prices:
            # formatted_message += f"Start: {cheap_price['start']}\nEnd:{cheap_price['end']}\nCheapest price: {cheap_price['price']}\n\n"
            notification_message += (
                f"*{cheap_price['start_date']}*\n"
                f"{cheap_price['start_time']} to {cheap_price['end_time']}\n"
                f"Lowest price: {cheap_price['price']}\n\n"
            )
        print(notification_message)

        send(
            title="🐙 Octopus Agile: Upcoming cheap rates",
            message=notification_message,
        )


if __name__ == "__main__":
    main()
