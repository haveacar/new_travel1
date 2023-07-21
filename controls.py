import datetime
import os
import requests as requests
from flask import json
from keys_api import *
from models import Review
# path
CURRENT_PATH = os.path.dirname(__file__)
CURRENT_PATCH_JASON = os.path.join(CURRENT_PATH, "static")
# days period
DAYS = 20

def get_dates() -> tuple:
    """
    func to generate departing date and return with Israel preferences
    :return: tuple of strings
    """
    current_date = datetime.date.today()

    # time delta
    timedelta = datetime.timedelta(days=DAYS)

    future_date = current_date + timedelta

    # Loop until we find a Thursday day
    while future_date.weekday() != 3:
        future_date += datetime.timedelta(days=1)

    # create departure string
    data_departure = f"{future_date}_{future_date + datetime.timedelta(days=1)}"

    # create return string
    sunday_return = future_date + datetime.timedelta(days=4)
    data_return = f"{sunday_return}_{sunday_return + datetime.timedelta(days=3)}"

    return data_departure, data_return


def receive_data():
    """
        Receive_data func check
    :return:  dict(collected_rates) or False
    """
    try:
        # receive data
        response_data = requests.get(REQUEST_URL, headers={"UserAgent": "XY", "apikey": API_KEY_CUR}, timeout=5)
        print(response_data)
        collected_rates = json.loads(response_data.text)

        if collected_rates.get("success") == True: return collected_rates

    except requests.exceptions.Timeout:
        print("Connection timed out")
        return False

    except:
        return False


class Carbon:
    """This class is responsible for talking to the Flight Search API."""

    def get_iata_code(self, city: str) -> str | None:
        """
        Func request to kivi for get Iata code
        :param city: city str
        :return: str|None
        """

        params = {
            "term": city.lower()
        }
        try:
            response = requests.get(url=KIWI_ENDPOINT, headers=HEADER, params=params, timeout=5)

        except requests.exceptions.Timeout:
            print("Connection timed out")
            return None
        except:
            print("Data collect error")
            return None

        else:

            response.raise_for_status()
            return response.json()['locations'][0]['code']


    def carbon_request(self, departure_city: str, destination_city: str, return_t=False, passenger: int = 1):
        """
        Func request to carbon for calculate co2
        :param departure_city: str
        :param destination_city: str
        :param passenger: int
        :return: dict
        """

        self.departure = self.get_iata_code(departure_city)
        self.destination = self.get_iata_code(destination_city)
        self.passenger = passenger

        headers = {
            "Authorization": f"Bearer {API_KEY_CARBON}",
            "Content-Type": "application/json"
        }
        if return_t:
            data = {
                "type": "flight",
                "passengers": self.passenger,
                "legs": [
                    {"departure_airport": f"{self.departure}", "destination_airport": f"{self.destination}"},
                    {"departure_airport": f"{self.destination}", "destination_airport": f"{self.departure}"}
                ]
            }

        else:
            data = {
                "type": "flight",
                "passengers": self.passenger,
                "legs": [
                    {"departure_airport": f"{self.departure}", "destination_airport": f"{self.destination}"},

                ]
            }
        try:
            response = requests.post(CARBON_URL, headers=headers, data=json.dumps(data), timeout=5)

        except requests.exceptions.Timeout:
            print("Connection timed out")
            return None
        except:
            print("Get carbon Api error")
            return None

        else:
            res = response.json()
            return res

def psw_validation(psw:str)->bool:
    """
    Func check password validation
    :param psw: str
    :return: Bool
    """
    #  length case
    if len(psw) < 8 or len(psw)>10: return False
    # digital case
    if not any(char.isdigit() for char in psw): return False
    # char case
    if not any(char.isalpha() for char in psw): return False
    # lower case
    if not any(char.islower() for char in psw): return False
    # upper case
    if not any(char.isupper() for char in psw): return False

    return True

def get_reviews():
    """Fetch and return the reviews."""
    reviews = Review.query.order_by(Review.id.desc()).limit(10).all()

    reviews = [{'title': review.title, 'stars': review.stars, 'name':review.name, 'text': review.text} for review in reviews]
    return reviews
