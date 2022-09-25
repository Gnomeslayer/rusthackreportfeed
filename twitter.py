#!/usr/bin/python
# coding=utf-8

import requests
import json
import asyncio, aiohttp

configfile = {}
with open('./config/config.json', 'r') as f:
    configfile = json.load(f)
bearer_token = f"{configfile['twitter_bearer_token']}"

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "from:rusthackreport"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            print("<<<Tweet Detected>>>")
            json_response = json.loads(response_line)
            url = create_url(json_response['data']['id'])
            tweettext = json_response['data']['text']
            tweetid = json_response['data']['id']
            tweetdeets = connect_to_endpoint(url)
            steamurl = tweetdeets['data'][0]['entities']['urls'][0]['expanded_url']
            if not configfile['color']:
                color = '0x992d22'
            else:
                color = configfile['color']
            tweeturl = f"https://twitter.com/rusthackreport/status/{tweetid}"
            if configfile['sendembed']:
                embed = {
                    "username": f"Rust Hack Reports",
                    "embeds": [
                        {
                        "title": "Gameban report",
                        "color": f"{int(color, base=16)}",
                        "fields": [
                        {
                            "name": "Tweet",
                            "value": f"{tweettext}",
                            "inline": False
                        },
                        {
                            "name": "Links",
                            "value": f"[Steam]({steamurl}) | [Tweet]({tweeturl})",
                            "inline": False
                        },
                        ],
                        "footer": {
                        "text": f"Tweet brought to you by Gnomeslayer#5551"
                        }
                        }
                    ]
                    }
                channel = f"{configfile['channel']}"
                loop = asyncio.get_event_loop()
                loop.run_until_complete(send_embed(embed, channel))
            if not configfile['sendembed']:
                channel = f"{configfile['channel']}"
                loop = asyncio.get_event_loop()
                loop.run_until_complete(send_tweet(channel, tweettext))
                
async def send_embed(embed, channel):
    async with aiohttp.ClientSession() as session:
        async with session.post(channel, json=embed):
            print(">>>Posted embed<<<")
async def send_tweet(channel, tweettext):
    async with aiohttp.ClientSession() as session:
        message = {
                    "username": f"Rust Hack Reports",
                    "content": tweettext
                    }
        async with session.post(channel, json=message):
            print(">>>Posted sent normal tweet<<<")
def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()
def create_url(tweetid):
    tweet_fields = "tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities"
    media_fields = "media.fields=url"
    ids = f"ids={tweetid}"
    url = "https://api.twitter.com/2/tweets?{}&{}&{}".format(ids, tweet_fields, media_fields)
    return url

def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set)


if __name__ == "__main__":
    main()
