import smtplib
import ssl
import requests
import logging
import traceback
import yaml

from email.mime.text import MIMEText
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from random import randint
from random import choice
from os import path

if path.exists("settings.local.yaml"):
    file = open("settings.local.yaml")
else:
    file = open("settings.yaml")
settings = yaml.safe_load(file)
file.close()

PORT = settings["email"]["port"]
SMTP_SERVER = settings["email"]["smtp_server"]
SENDER_EMAIL = settings["email"]["sender_email"]
SENDER_PASSWORD = settings["email"]["sender_password"]
RECEIVERS = settings["email"]["receivers"]
IS_USERNAME = settings["is_muni"]["username"]
IS_PASSWORD = settings["is_muni"]["password"]

SESSION_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en,q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
}
IS_LOGIN_URL = "https://is.muni.cz/auth/"
IS_LOGIN_DATA = {
    "akce": "login",
    "credential_0": IS_USERNAME,
    "credential_1": IS_PASSWORD,
    "uloz": "uloz"
}
IS_THESIS_URL = "https://is.muni.cz/auth/rozpis/"
SWEARS = ["pliagarská škebra", "mahagárska bzdocha", "zmoknutá opica", "harfatý bakalár", "osemkilová buzna",
          "neandertálska fľandra", "pahliacka indiánka", "zdochliacka herbra", "ožratý primitív", "bosorácka marha",
          "materin ogrgeľ"]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(asctime)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("debug.log")]
)


def send_mail(message, subject="Lackove bakalárky"):
    logging.info(f"Sending email from {SENDER_EMAIL} to {RECEIVERS}")
    msg = MIMEText(message, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVERS)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVERS, msg.as_string())
    logging.info("Email successfully sent")


def update_headers(session):
    # Add "Cookie" value to headers
    headers = SESSION_HEADERS
    cookies = session.cookies.get_dict()
    h_cookies = []
    for key in cookies.keys():
        h_cookies.append(key + "=" + cookies[key])
    if h_cookies:
        headers["Cookie"] = "; ".join(h_cookies)
    session.headers.clear()
    session.headers.update(headers)


def login(session):
    logging.info(f"Accessing {IS_LOGIN_URL}")
    res = session.get(IS_LOGIN_URL)
    update_headers(session)
    sleep(randint(800, 1500) / 1000)
    url = res.url
    logging.info(f"Trying to login to {url} as {IS_USERNAME}")
    session.post(url, data=IS_LOGIN_DATA)
    update_headers(session)
    sleep(randint(800, 1500) / 1000)


def get_bachelor_thesis_url(session):
    logging.info(f"Accessing {IS_THESIS_URL}")
    res = session.get(IS_THESIS_URL)
    update_headers(session)
    sleep(randint(800, 1500) / 1000)
    soup = BeautifulSoup(res.text, "html.parser")
    link = soup.find("a", string="Bakalářské práce")
    url = urljoin(IS_THESIS_URL, link.get("href"))
    logging.info(f"Successfully parsed bachelor thesis url: {url}")
    return url


def get_thesis(session, url, sorted_by_update=True):
    if sorted_by_update:
        url += ";sorter=poslmod"
    logging.info(f"Trying to get thesis from {url}")
    res = session.get(url)
    update_headers(session)
    sleep(randint(800, 1500) / 1000)

    soup = BeautifulSoup(res.text, 'html.parser')
    tags = soup.find_all("h5")
    thesis_links = []
    for elem in tags:
        link = elem.find("a")
        if not elem.has_attr("class") and link:
            new_link = soup.new_tag("a", href=urljoin(res.url, link.get("href")))
            new_link.string = link.text
            thesis_links.append(str(new_link))
    logging.info(f"Successfully parsed these thesis: {thesis_links}")
    return thesis_links


req_session = requests.session()
update_headers(req_session)
login(req_session)
thesis_url = get_bachelor_thesis_url(req_session)
thesis = get_thesis(req_session, thesis_url)

message_text = f"Práve sa spúšťam ty {choice(SWEARS)}!<br><br>"
message_text += f"Tu máš aktuálne témy zoradené podla poslednej modifikácie ty {choice(SWEARS)}:<br>"
message_text += "<br>".join(thesis)
message_text += f"<br><br>Ak sa niečo zmení, tak ti dám vedieť ty {choice(SWEARS)}."
send_mail(message_text)

while True:
    time_to_sleep = randint(60, 120)
    logging.info(f"Sleeping for {time_to_sleep} seconds")
    sleep(time_to_sleep)
    subject = "Lackove bakalárky"
    try:
        new_thesis = get_thesis(req_session, thesis_url)
    except Exception:
        logging.error(f"Something went wrong!\n{traceback.format_exc()}")
        subject = "(Pokazené) " + subject
        message_text = f"Dačo sa pokazilo ty {choice(SWEARS)}!<br>"
        message_text += traceback.format_exc()
        send_mail(message_text)
        break
    message_text = f"Zmenil sa zoznam tém ty {choice(SWEARS)}!<br>"
    added = list(set(new_thesis) - set(thesis))
    if added:
        logging.info(f"These thesis were added: {added}")
        subject = "(Pridané) " + subject
        message_text += f"<br>Tieto témy boli pridané ty {choice(SWEARS)}:<br>"
        message_text += "<br>".join(added)
    removed = list(set(thesis) - set(new_thesis))
    if removed:
        logging.info(f"These thesis were removed: {removed}")
        if added:
            subject = "(Pridané/Odstránené) " + subject
        else:
            subject = "(Odstránené) " + subject
        message_text += f"<br>Tieto témy boli odstránené ty {choice(SWEARS)}:<br>"
        message_text += "<br>".join(removed)
        message_text += "<br>"
    if removed or added:
        send_mail(message_text)
    thesis = new_thesis
