from http.client import responses

import requests
import os


# Global variables

# API keys
CLIENT_API = os.getenv('INFOMANIAK_CLIENT_API')
CLIENT_SECRET = os.getenv('INFOMANIAK_CLIENT_SECRET')

# Identifiers
DOMAIN = os.getenv('INFOMANIAK_DOMAIN')
ID_CLUB = os.getenv('INFOMANIAK_ID_CLUB')
ID_LICENCIES = os.getenv('INFOMANIAK_ID_LICENCIES')


def add_member(email, is_licence):

    url = f"https://api.infomaniak.com/1/newsletters/{DOMAIN}/subscribers"

    # Subscribed groups
    groups = [ID_CLUB]
    if is_licence:
        groups.append(ID_LICENCIES)

    # Request data
    data = {
        "email": email,
        "groups": groups
    }

    # Request headers
    headers = {
        'Authorization': f'Bearer {CLIENT_API}',
        'Content-Type': 'application/json'
    }

    # Post request
    response = requests.post(url, json=data, headers=headers)

    return is_successful(response.status_code)


def delete_member(email):
    # Get member ID
    member_ID, response_member_ID = get_member_ID(email)

    url = f"https://api.infomaniak.com/1/newsletters/{DOMAIN}/subscribers/{member_ID}/forget"

    # Request headers
    headers = {
        'Authorization': f'Bearer {CLIENT_API}',
        'Content-Type': 'application/json'
    }

    # Delete request
    response = requests.delete(url, headers=headers)

    return is_successful(response_member_ID.status_code), is_successful(response.status_code)


def edit_member(old_email, new_email, is_licence):

    if old_email != new_email:
        delete_get_member_ID_response, delete_response = delete_member(old_email)

    add_response = add_member(new_email, is_licence)

    return add_response


def get_member_ID(email):
    url = f"https://api.infomaniak.com//1/newsletters/{DOMAIN}/subscribers"
    # Request headers
    headers = {
        'Authorization': f'Bearer {CLIENT_API}',
        'Content-Type': 'application/json'
    }
    data = {
        "filter": {"search": email}
    }
    response_get_ID = requests.get(url, json=data, headers=headers)
    member_ID = response_get_ID.json()["data"][0]["id"]

    return member_ID, response_get_ID


# Check if http request is successful (i.e., if response code is in the 200s)
def is_successful(response_code):
    return (response_code // 100) == 2
