from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import calendar
import os


# Load environment variables in .env file (for local development only, has no effect on Heroku)
from dotenv import load_dotenv
load_dotenv()
LOGIN = os.getenv('SWISSBAD_LOGIN')
PASSWORD = os.getenv('SWISSBAD_PASSWORD')

FRENCH_MONTHS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin", 7: "juillet", 8: "août", 9: "septembre",
    10: "octobre", 11: "novembre", 12: "décembre"
}


def add_member(member_data):
    driver = login()

    # Add member
    form_url = "https://sb.tournamentsoftware.com/organization/member_create.aspx?id=A819E89F-58F3-49B9-9C1F-C865A135F19A&gid=1F8ED2D9-D1C7-4378-A881-C104C63FEF1B"
    driver.get(form_url)

    # Fill out fields

    # First name
    first_name_name = "cphPage_cphPage_divRightColumn_cphPage_VF1_fs0_firstname"
    fill_out_field(driver, first_name_name, member_data["prenom"])

    # Last name
    last_name_name = "cphPage_cphPage_divRightColumn_cphPage_VF1_fs0_lastname"
    fill_out_field(driver, last_name_name, member_data["nom"])

    # Parse birthday
    dob = member_data["date_naissance"].split("-")
    year, month, day = dob[0], FRENCH_MONTHS[int(dob[1])], str(int(dob[2]))

    # Birthday day
    birthday_day_name = "cphPage_cphPage_divRightColumn_cphPage_VF1_fs0_birthdate_d"
    dropdown_menu(driver, birthday_day_name, day)

    # Birthday month
    birthday_month_name = "cphPage_cphPage_divRightColumn_cphPage_VF1_fs0_birthdate_m"
    dropdown_menu(driver, birthday_month_name, month)

    # Birthday year
    birthday_year_name = "cphPage_cphPage_divRightColumn_cphPage_VF1_fs0_birthdate_y"
    fill_out_field(driver, birthday_year_name, year)

    # Gender
    gender_name = "cphPage_cphPage_divRightColumn_cphPage_VF1_fs0_gender"
    dropdown_menu(driver, gender_name, member_data["genre"])

    # Nationality
    nationality_name = "cphPage_cphPage_divRightColumn_cphPage_VF1_fs0_nationality"
    dropdown_menu(driver, nationality_name, member_data["nationalite"])

    # Language
    langue = member_data["langue"]
    if langue == "Anglais":
        langue_full = "Anglais (GBR)"
    elif langue == "Francais":
        langue_full = "Français (SUI)"
    elif langue == "Allemand":
        langue_full = "Allemand (SUI)"

    language_name = "cphPage_cphPage_divRightColumn_cphPage_VF1_fs0_language"
    dropdown_menu(driver, language_name, langue_full)

    # Click next button
    next_button_name = "ctl00$ctl00$ctl00$cphPage$cphPage$divRightColumn$cphPage$btnNext_0"
    next_button = driver.find_element(By.NAME, next_button_name)
    next_button.click()

    # Address
    address_name = "cphPage_cphPage_divRightColumn_cphPage_VF2_fs0_address"
    fill_out_field(driver, address_name, member_data["adresse"])

    # Postcode
    postcode_name = "cphPage_cphPage_divRightColumn_cphPage_VF2_fs0_postalcode"
    fill_out_field(driver, postcode_name, member_data["code_postal"])

    # City
    city_name = "cphPage_cphPage_divRightColumn_cphPage_VF2_fs0_city"
    fill_out_field(driver, city_name, member_data["ville"])

    # Telephone
    phone_name = "cphPage_cphPage_divRightColumn_cphPage_VF2_fs0_phone"
    fill_out_field(driver, phone_name, member_data["telephone"])

    # Mail
    mail_name = "cphPage_cphPage_divRightColumn_cphPage_VF2_fs0_email"
    fill_out_field(driver, mail_name, member_data["email"])

    # News
    news_name = "cphPage_cphPage_divRightColumn_cphPage_VF2_fs0_communicationsallowed_news"
    click_checkbox(driver, news_name)

    # Marketing
    marketing_name = "cphPage_cphPage_divRightColumn_cphPage_VF2_fs0_communicationsallowed_marketing"
    click_checkbox(driver, marketing_name)

    # Click next button
    next1_button_name = "ctl00$ctl00$ctl00$cphPage$cphPage$divRightColumn$cphPage$btnNext_1"
    next1_button = driver.find_element(By.NAME, next1_button_name)
    next1_button.click()

    # Affiliation
    affiliation = member_data["statut_swissbad"]  # Actif, passif ou licence
    if affiliation == "LicenceAdulte":
        affiliation = "Licence"
    elif affiliation == "LicenceU19":
        affiliation = "Affiliation Junior (U17-U19)"
    elif affiliation == "LicenceU15":
        affiliation = "Affiliation Junior (jusqu’à U15)"
    elif affiliation != "Actif" and affiliation != "Passif":
        raise ValueError(f"Affiliation Swissbad inconnue: {affiliation}")

    affiliation_name = "cphPage_cphPage_divRightColumn_cphPage_VF4_fs0_typeselect"
    dropdown_menu(driver, affiliation_name, affiliation)

    submit_button_name = "ctl00$ctl00$ctl00$cphPage$cphPage$divRightColumn$cphPage$btnSubmit_2"
    submit_button = driver.find_element(By.NAME, submit_button_name)
    # submit_button.click()


def fill_out_field(driver, name, value):
    field = driver.find_element(By.NAME, name)
    field.send_keys(value)


def dropdown_menu(driver, name, value):
    field = driver.find_element(By.NAME, name)
    dropdown = Select(field)
    try:
        dropdown.select_by_visible_text(value)
    except:  # If value does not exist in the menu, send_keys will find the closest match
        field.send_keys(value)

def click_checkbox(driver, name):
    checkbox = driver.find_element(By.NAME, name)
    checkbox.click()

def login():
    # # Initialize the WebDriver (Firefox in this case) (local development)
    # options = Options()
    # options.set_preference("intl.accept_languages", "en-US")
    # driver = webdriver.Firefox(options=options)

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=en")

    driver = webdriver.Chrome(options=chrome_options)

    # URL for the login endpoint
    login_url = "https://sb.tournamentsoftware.com/user"

    # Login
    driver.get(login_url)

    # Accept cookies
    find_cookies_button = (By.CSS_SELECTOR, ".btn.btn--success.js-accept-basic")
    cookies_button = driver.find_element(*find_cookies_button)
    cookies_button.click()

    # Log in
    fill_out_field(driver, "Login", LOGIN)
    fill_out_field(driver, "Password", PASSWORD)

    # Submit the login form
    find_login_button = (By.CSS_SELECTOR, ".btn.btn--primary.margin-top--small")
    login_button = driver.find_element(*find_login_button)
    login_button.click()

    # Change language
    language_url = "https://sb.tournamentsoftware.com/Language/SetLanguage/4108"
    driver.get(language_url)

    return driver

if __name__ == '__main__':
    member_data = {"nom": "Dupont", "prenom": "Jean", "date_naissance": "2000-01-01", "genre": "Masculin",
                   "nationalite": "Switzerland", "langue": "Francais", "adresse": "1 rue du LUC", "ville": "Lausanne",
                   "code_postal": "1007", "telephone": "0123456789", "email": "test@gmail.com",
                   "statut_swissbad": "Passif"}
    add_member(member_data)


