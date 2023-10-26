
import datetime
import json
import re
import time

import requests
import schedule


TELEGRAM_TOKEN = ""
TELEGRAM_CHANNEL_ID = ""
PARTNERS_WATCHLIST = ["AMZ", "ALB", "CHR", "JBW", "BOK", "CSB", "CAS", "CEA", "BUD", "DAF", "DCH", "CDR", "EUD", "CEX",
                      "FST", "FLA", "ALP", "HRG", "CSW", "ITG", "LEG", "MZL", "VMZ", "CNB", "NTS", "BOT", "OVC", "PLS",
                      "RNN", "SPR", "FIL", "ZTN"]

URL_PARTNERS_DATA = "https://www.livelo.com.br/ccstore/v1/files/thirdparty/config_partners_compre_e_pontue.json"
URL_PARTNERS_INFO = "https://apis.pontoslivelo.com.br/partners-campaign/v1/campaigns/active?partnersCodes="


def search_partner_key(partners, name):
    pattern = re.compile(r"{}".format(name), re.IGNORECASE)

    output = []
    for x in partners:
        if pattern.search(x["name"]):
            output.append([x["id"], x["name"]])

    return output


def get_partner_data_by_key(partners, key):
    for x in partners:
        if key == x["id"]:
            return x

    return None


def get_partner_info_by_key(partners_info, key):
    for x in partners_info:
        if key == x["partnerCode"]:
            return x
    return None


def load_partners_data():
    return json.loads(requests.get(URL_PARTNERS_DATA).text)["partners"]


def load_partners_info():
    return json.loads(requests.get(URL_PARTNERS_INFO + ",".join(PARTNERS_WATCHLIST)).text)


def telegram_send_message(message):
    apiURL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        response = json.loads(
            requests.post(
                apiURL,
                json={"chat_id": TELEGRAM_CHANNEL_ID, "text": message}).text)

        if response["ok"]:
            print("OK ", datetime.datetime.now())
    except Exception as e:
        print(e)


def main():
    partners = load_partners_data()
    partners_info = load_partners_info()

    output = []
    for partner in PARTNERS_WATCHLIST:
        data = get_partner_data_by_key(partners, partner)
        info = get_partner_info_by_key(partners_info, partner)
        name = data.get("name", "N/A")
        currency = info.get("currency", "N/A")
        value = info.get("value", "N/A")
        separator = info.get("separator", "=") or "="
        parity = info.get("parity", "N/A")
        details = data.get("partnerDetailsPage", "N/A")
        output.append("{}:  {} {} {} {} {}".format(
            name, currency, value, separator, parity, details))
        # info["parityClub"]

    telegram_send_message("\n".join(output))


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":

    # schedule to check promotions every day at 6am
    schedule.every().day.at("06:00").do(main)

    run_scheduler()
