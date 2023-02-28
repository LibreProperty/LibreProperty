# ![Logo](libreproperty/static/favicon.png?raw=true "Logo") LibreProperty: Short-Term Property Management
Note: This README is more of a roadmap since there is no working prototype yet.

LibreProperty is free and open source property management software focused on vacation
and short-term rentals.

## Features
ROADMAP:

* Manage your listings across various platforms Airbnb, Vrbo and Booking.com
* Automatically close off your listings when on other platforms when booked
  to prevent double bookings
* Dynamically adjust pricing based across all platforms based on the rules
  you define
* Integrate with Smart Locks and send a unique code for each booking
* Easily create a professional booking website for your property

## Setting up a local development environment
Create a virtualenv and install dependencies
```sh
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Start minio to be used instead of S3 and redis:
```sh
./scripts/run-dev-services.sh
```

Start the local development server:
```
export AWS_ACCESS_KEY_ID=LIBREPROPERTY
export AWS_SECRET_ACCESS_KEY=LIBREPROPERTY
export SECRET_KEY=changemetosomethingsecret
python server.py
```

You should now have a development environment running on
[http://localhost:8888](http://localhost:8888).

Start Huey for background tasks execution:
```sh
export AWS_ACCESS_KEY_ID=LIBREPROPERTY
export AWS_SECRET_ACCESS_KEY=LIBREPROPERTY
huey_consumer.py libreproperty.tasks.tasks.huey -w 2 -v
```

## License
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

