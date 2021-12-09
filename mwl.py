import os
import requests
from dotenv import load_dotenv

api_uri = "https://mywaifulist.moe/api/v1/"

load_dotenv('.env')
API_KEY = os.environ['API_KEY']

def make_request(type, url, data = {}):
    session = requests.Session()
    session.headers.update({'apiKey': str(API_KEY)})

    response = ""
    
    if type == "get":
        response = session.get(api_uri + url)
    elif type == "post":
        response = session.post(api_uri + url, data)

    print("Response: " + str(response.status_code))

    if response.status_code == 404:
        return "notfound"
    elif response.status_code == 200:
        return response.json()
    else:
        return "error"


def search_character(gender, name):
    object = {
        "term":str(name)
    }

    if gender == "female":
        return make_request("post", "search/beta", object)
    if gender == "male":
        return make_request("post", "search/husbando", object)


def get_character(gender, id):
    if gender == "female":
        return make_request("get", "waifu/" + str(id))
    if gender == "male":
        return make_request("get", "husbando/" + str(id))