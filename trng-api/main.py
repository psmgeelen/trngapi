import os
from fastapi import FastAPI, Form
from fastapi.openapi.utils import get_openapi
from fastapi_health import health
import logging
import trng

# Setup Logger
logging.basicConfig(
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s", level=logging.WARNING
)
logger = logging.getLogger("my-logger")
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

# Init Handler
# handler = trng.Handler()

# Init API
app = FastAPI()


def my_schema():
    DOCS_TITLE = "TRNG"
    DOCS_VERSION = "0.1"
    openapi_schema = get_openapi(
        title=DOCS_TITLE,
        version=DOCS_VERSION,
        routes=app.routes,
    )
    openapi_schema["info"] = {
        "title": DOCS_TITLE,
        "version": DOCS_VERSION,
        "description": "A service that delivers free to use, truly random numbers",
        "contact": {
            "name": "A project of geelen.io",
            "url": "https://github.com/psmgeelen/etaai",
        },
        "license": {"name": "UNLICENSE", "url": "https://unlicense.org/"},
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = my_schema

##### Endpoints #####
@app.get(
    "/ping",
    summary="Check whether there is a connection at all",
    description="You ping, API should Pong",
    response_description="A string saying Pong",
)
def ping():
    return "pong"


@app.get(
    "/list_devices",
    summary="Get a list of all the available devices",
    description=(
        "This request returns a list of devices. If no hardware is found, it will"
        "return the definition of the DeviceEmulator class"
    ),
    response_description="A dictionary with a list of devices",
    response_model=str,
)
def list_devices():
    return trng.Handler().list_devices()


@app.post(
    "/get_random_nrs",
    summary="Get a list truly random numbers",
    description=(
        'This request returns a list of random-numbers, formatted with numpy. The supported formats are: "byte", '
        '"ubyte", "short", "ushort", "intc", "uintc", "int_", "uint", "longlong", "ulonglong", "half", "float16", '
        '"single", "double", for more information, please check out: '
        'https://numpy.org/doc/stable/user/basics.types.html'
    ),
    response_description="A dictionary with Random Numbers and some meta-data",
    response_model=trng.randomPayload,
)
def get_random_nrs(dtype: str = Form(...), n_numbers: int = Form(...)) -> trng.randomPayload:
    if n_numbers <= 1000:
        results = trng.Handler().get_numbers(dtype = dtype, n_numbers = n_numbers)
    else:
        results = trng.randomPayload(
            length=0,
            actual_length = 0,
            dtype = dtype,
            data = ["Limited to 1000 items at a time"],
            device = "error"
        )
    return results
@app.post(
    "/get_random_hex",
    summary="Get a random hex of desired length",
    description=(
        "This request returns a truly random hex to a specified length"
    ),
    response_description="A dictionary with Random Hex and some meta-data",
    response_model=trng.randomPayload,
)
def get_random_hex(length: int = Form(...)) -> trng.randomPayload:
    if length <= 10000:
        results = trng.Handler().get_hex(length = length)
    else:
        results = trng.randomPayload(
            length=0,
            actual_length = 0,
            dtype = "bytes",
            data = ["Limited to length of 10000 at a time"],
            device = "error"
        )
    return results

##### Healthchecks #####
def _healthcheck_ping():
    hostname = "google.com"  # example
    response = os.system("ping -c 1 " + hostname)
    print(response)

    # and then check the response...
    if response == 0:
        return str(response)
    else:
        return False
def _healthcheck_get_random_nrs():
    response = False
    try:
        get_random_nrs(dtype = 'int8', n_numbers = 10)
        response = True
    except Exception as e:
        logger.error("Healthcheck failed at getting nrs")
    finally:
        return response

def _healthcheck_get_hex():
    response = False
    try:
        get_random_hex(length = 10)
        response = True
    except Exception as e:
        logger.error("Healthcheck failed at getting hex")
    finally:
        return response
def _healthcheck_list_devices():
    response = False
    try:
        list_devices()
        response = True
    except Exception as e:
        logger.error("Healthcheck failed listing devices")
    finally:
        return response

app.add_api_route(
    "/health",
    health([_healthcheck_ping, _healthcheck_get_random_nrs, _healthcheck_get_hex, _healthcheck_list_devices]),
    summary="Check the health of the service",
    description=(
        "The healthcheck checks more then whether the service is up. It will check"
        " for internet connectivity, whether the hardware is callable and does an"
        " end-to-end test. The healthcheck therefore can become blocking by nature. Use"
        " with caution!"
    ),
    response_description=(
        "The response is only focused around the status. 200 is OK, anything else and"
        " there is trouble."
    ),
)
