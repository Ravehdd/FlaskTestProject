from flsite import client
import pytest
from flsite import my_list
import requests

base_url = "http://127.0.0.1:8000"

def test_check_number_one():
    my_list = [1, 3, 2]
    assert 1 in my_list

def test_get():
    response = requests.get(base_url+"/")
    assert response.status_code == 200
    # assert response.json is not None


def test_post():
    data = {
        "name": "max",
        "age": 20
    }
    response = requests.post(base_url+"/post", json=data)
    assert response.status_code == 200
    # assert response.text == "ok"
