# Octopus Agile Trigger

A small script that uses the predictions from [Agile Predict](https://agilepredict.com/)
and sends a notification to your favourite service using
[Apprise](https://github.com/caronc/apprise) when the predicted price goes below
a set threshold.

This is intended to be run on a cronjob.

## Installation

Clone the project and install the dependencies into a python virtual environment:
```
# Clone the repository
$ git clone git@github.com:AlanCunningham/octopus-agile-prediction-notifier.git

# Create a python virtual environment
$ python3 -m venv venv

# Activate the virtual environment
$ source venv/bin/activate

# Install the python dependencies using the requirements.txt file provided
(venv) $ pip install -r requirements.txt
```

Open the settings.py and enter:
- Your [Distribution Network Operator Code](https://en.wikipedia.org/wiki/Distribution_network_operator)
- Your preferred price threshold in pence
- The Apprise services you want to notify - see the [Apprise README](https://github.com/caronc/apprise?tab=readme-ov-file#supported-notifications)
for the format of the service you want to add.

Then run the application
```
(venv) $ python main.py
```
