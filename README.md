# LUC Badminton Members Database App

A **Flask** web application that manages the membership database of the [LUC Badminton](https://lucbadminton.ch/) club (~200 members). This app handles record-keeping, automates newsletter subscription, and integrates with external services.

## Table of Contents
1. [Overview](#overview)  
2. [Key Features](#key-features)  
3. [Tech Stack](#tech-stack)  
4. [Project Structure](#project-structure)  
5. [Setup & Installation](#setup--installation)  
6. [Usage](#usage)  
7. [Future Improvements](#future-improvements)  
8. [License](#license)

---

## Overview
- **Objective**: Provide an easy-to-use GUI for adding, modifying, and removing members in the club’s database.  
- **Automation**: Automates interactions with Infomaniak’s newsletter service and the Swiss Badminton database to keep member information in sync.

---

## Key Features
1. **Member Management**  
   - Add, edit, or remove member profiles via a simple web interface.  
   - Data stored in an SQL database for reliable and consistent record-keeping.

2. **Newsletter Integration**  
   - Synchronizes email lists with [Infomaniak Newsletter](https://newsletter.infomaniak.com/) via API calls.  
   - Ensures new or updated member emails are accurately reflected in the mailing list.

3. **External Database Integration**  
   - Uses [Selenium](https://www.selenium.dev/) to automatically add new members to the Swiss Badminton database.  
   - Reduces manual data entry by automating the process.

---

## Tech Stack
- **Frontend**:  
  - HTML, CSS, JavaScript

- **Backend**:  
  - [Flask](https://flask.palletsprojects.com/en/stable/) (Python)  
  - SQL (for the main database)  
  - [Requests](https://docs.python-requests.org/en/latest/) (API calls)  
  - [Pandas](https://pandas.pydata.org/) (data manipulation)  
  - [Selenium](https://www.selenium.dev/) (browser automation)

- **Hosting**:  
  - [Heroku](https://www.heroku.com/) (for deployment)

---

## Project Structure

- **`app.py`**  
  Entrypoint for the Flask application. Defines routes, app configuration, and ties everything together.

- **`database_params.py`**  
  Contains definitions for the database fields and any relevant configuration parameters.

- **`infomaniak.py`**  
  Contains code for interacting with Infomaniak’s API.

- **`swissbad.py`**  
  Implements Selenium-based automation to add new members to the Swiss Badminton database.

- **`templates/`**  
  Holds HTML templates for rendering dynamic pages.

- **`requirements.txt`**  
  Lists all Python dependencies needed to run the project.

- **`Procfile`**  
  Used by Heroku to specify the commands needed to run the application.

---
