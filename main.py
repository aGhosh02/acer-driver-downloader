import json
from itertools import chain

# from module.remote.thriftbackend.ThriftClient import ThriftClient, WrongLogin
import requests


def group_by_keys(data, keys):
    """
    Recursively group an array of objects by multiple keys.

    Parameters:
    - data (list): The array of objects to be grouped.
    - keys (list): The list of keys to group the objects by.

    Returns:
    - dict: A nested dictionary representing the grouped data.
    """
    if not keys:
        # If there are no more keys to group by, return the original data
        return data

    current_key = keys[0]
    grouped_data = {}

    for item in data:
        key_value = item.get(current_key)

        # Create a new key if it doesn't exist
        if key_value not in grouped_data:
            grouped_data[key_value] = []

        # Append the item to the list under the current key
        grouped_data[key_value].append(item)

    # Recursively call the function for each group
    for key, group in grouped_data.items():
        grouped_data[key] = group_by_keys(group, keys[1:])

    return grouped_data


def search_drivers_for(model_code):
    api_url = 'https://www.acer.com/in-en/DynamicContent/GetDriversAndManuals'
    headers = {
        'content-type': 'application/json',
        'referer': 'arghyaghosh.cloud'
    }
    data = {
        'ModelName': model_code,
        'Local': 'en-in'
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        return json.loads(response.json()['hits'][0]["_source"]["global_download_details"])
    except requests.exceptions.RequestException as e:
        print(f"Error making API call: {e}")
        return None


def drivers_to_download(driver_list):
    files = []
    grouped_drivers = group_by_keys(driver_list, ['category', 'vendor', 'description'])

    for key, value in grouped_drivers.items():
        for vendor, drivers in value.items():
            choice = 1
            if len(drivers.items()) > 1:
                print(", ".join(drivers))
                choice = int(input("Which " + vendor + " driver do you want to download. (input number / 0 for all): "))
                print("\n")

            if choice == 0:
                files.extend(list(chain(*drivers.values())))
            else:
                files.append(
                    sorted(tuple(drivers.items())[choice - 1][1], key=lambda x: x.get('date'), reverse=True)[0])
    return files


def bios_to_download(driver_list):
    files = []
    grouped_drivers = group_by_keys(driver_list, ['category'])

    for key, value in grouped_drivers.items():
        files.append(
            sorted(value, key=lambda x: x.get('date'), reverse=True)[0])
    return files

# def download_files(files,packagename):
#
#
#     try:
#         client = ThriftClient(host="127.0.0.1", port=7227, user="User", password="yourpw")
#     except:
#         print
#         "Login was wrong"
#         exit()


if __name__ == '__main__':
    model = 'PHN16-71'
    files_to_download = []

    response = search_drivers_for(model)

    files_to_download.extend(drivers_to_download(response["driver"]["files"]))
    files_to_download.extend(bios_to_download(response["bios"]["files"]))
    files_to_download.extend(drivers_to_download(response["application"]["files"]))

    print(json.dumps(list(map(lambda a : "https://global-download.acer.com/"+a['link'], files_to_download))))
