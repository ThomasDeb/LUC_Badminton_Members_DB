from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, Response
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from io import StringIO
from datetime import date
import pandas as pd
import mysql.connector
import os
from urllib.parse import urlparse

import database_params as db
import infomaniak
import swissbad


# Load environment variables in .env file (for local development only, has no effect on Heroku)
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
secret_key = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = secret_key

# Login credentials for admins
USERS = {
    os.getenv('ADMIN_LOGIN'): {'password': os.getenv('ADMIN_PASSWORD')}
}

# Database parameters

# Get the JawsDB URL from environment variables
url = urlparse(os.getenv('JAWSDB_URL'))

MYSQL_PARAMS = {
    'host': url.hostname,
    'user': url.username,
    'password': url.password,
    'database': url.path[1:],  # Remove leading '/'
    'port': url.port
}

# MYSQL_PARAMS = {"host": "localhost",  # For local development
#                 "user": "root",
#                 "password": "",
#                 "database": "LUC_badminton",
#                 "table": "membres"
#                 }

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized access


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username  # Flask-Login requires the user to have an id property


@login_manager.user_loader
def load_user(username):
    if username in USERS:
        return User(username)
    return None


# Define a custom filter to format datetime objects
@app.template_filter('format_date')
def format_date(value):
    if isinstance(value, date):
        return value.strftime('%d.%m.%Y')  # Desired date format
    return value  # If it's not a date, return it unchanged


# Database connection function
def connect_db():
    return mysql.connector.connect(
        host=MYSQL_PARAMS["host"],
        user=MYSQL_PARAMS["user"],
        password=MYSQL_PARAMS["password"],
        database=MYSQL_PARAMS["database"]
    )


# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password are correct
        user = USERS.get(username)
        if user and user['password'] == password:
            login_user(User(username))
            flash('Logged in successfully.', 'success')
            return redirect(url_for('manage_members'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


# Route to logout the user
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/get_members', methods=['GET'])
@login_required
def get_members():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    # Query the database for members
    cursor.execute("SELECT * FROM membres ORDER BY nom ASC, prenom ASC")
    membres = cursor.fetchall()

    # Apply mapping to each member in the list
    for membre in membres:
        membre['statut_swissbad'] = db.STATUT_SWISSBAD_MAPPING.get(membre['statut_swissbad'], membre['statut_swissbad'])
        membre['pourcentage_cotisation'] = f"{membre['pourcentage_cotisation']} %"

    # Separate current and previous members
    current_members = [m for m in membres if m['membre_actuel'] == 'Oui']
    previous_members = [m for m in membres if m['membre_actuel'] == 'Non']

    cursor.close()
    conn.close()

    # Return a combined response with both lists
    return jsonify({
        'current_members': current_members,
        'previous_members': previous_members
    })

# Main route to manage membres (requires login)
@app.route('/', methods=['GET', 'POST'])
@login_required  # Require login to access the page
def manage_members():

    # Handle adding, editing, or deleting membres
    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        if 'add_member' in request.form:
            new_member_data = {field: request.form.get(field) for field in db.FIELDS}

            # Dynamically construct the SQL query for insertion
            columns = ", ".join(db.FIELDS)  # e.g., "nom, prenom, email, telephone, ..."
            placeholders = ", ".join(["%s"] * len(db.FIELDS))  # e.g., "%s, %s, %s, ..."
            query = f"INSERT INTO membres ({columns}) VALUES ({placeholders})"

            # Extract the values in the correct order
            values = [new_member_data[field] for field in db.FIELDS]

            # Execute the query to insert a new member
            cursor.execute(query, tuple(values))
            conn.commit()
            flash('Membre ajouté avec succès', 'success')

            # Add email to Infomaniak
            success_infomaniak = infomaniak.add_member(new_member_data["email"], is_licence(new_member_data["statut_swissbad"]))
            if success_infomaniak:
                flash('Email ajouté sur Infomaniak avec succès', 'success')
            else:
                flash('Erreur ajout Infomaniak', 'danger')

            # Add to Swissbad (only if not Absent or LicencePlus)
            if request.form.get("add_swissbad") == "on" and (new_member_data["statut_swissbad"] != "Absent" or
                                                             "LicencePlus" not in new_member_data["statut_swissbad"]):
                try:
                    swissbad.add_member(new_member_data)
                    flash('Membre ajouté sur Swissbad avec succès', 'success')
                except Exception as error:
                    flash(f'Erreur ajout Swissbad: {str(error)}', 'danger')

        elif 'edit_member' in request.form:

            # Retrieve the old values from the database
            membre_id = request.form['id']
            cursor.execute("SELECT * FROM membres WHERE id = %s", (membre_id,))
            old_values = cursor.fetchone()
            del old_values["id"]

            # Extract form data dynamically
            new_values = {field: request.form.get(field) for field in db.FIELDS}

            # Compare the old values (old_values) with the new ones
            modified_fields = {}
            for field, new_value in new_values.items():
                if old_values[field] != new_value:
                    modified_fields[field] = {
                        "old": old_values[field],
                        "new": new_value
                    }
            if modified_fields:
                # Dynamically build the SQL query
                set_clause = ", ".join([f"{field} = %s" for field in modified_fields.keys()])
                query = f"UPDATE membres SET {set_clause} WHERE id = %s"

                # Get the values to be updated
                values = [new_values[field] for field in modified_fields.keys()]
                values.append(membre_id)  # Add the member ID for the WHERE clause

                # Execute the query
                cursor.execute(query, tuple(values))
                conn.commit()
                flash('Membre édité avec succès', 'success')
            else:
                flash('Pas de modifications', 'success')

            # Modify Infomaniak if email or licence status changed
            old_email, new_email = old_values["email"], new_values["email"]
            old_is_licence, new_is_licence = is_licence(old_values["statut_swissbad"]), is_licence(new_values["statut_swissbad"])
            if (old_email != new_email) or (old_is_licence != new_is_licence):
                success_modification_infomaniak = infomaniak.edit_member(old_email, new_email, new_is_licence)
                if success_modification_infomaniak:
                    flash('Membre modifié sur Infomaniak avec succès', 'success')
                else:
                    flash('Erreur modification membre Infomaniak', 'danger')

        elif 'delete_member' in request.form:

            membre_id = request.form['id']

            # Retrieve the email from the database (for Infomaniak)
            cursor.execute("SELECT email FROM membres WHERE id = %s", (membre_id,))
            result_query = cursor.fetchone()
            cursor.execute("UPDATE membres SET membre_actuel = 'Non' WHERE id=%s", (membre_id,))
            conn.commit()
            flash('Membre supprimé avec succès', 'success')

            # Delete email from Infomaniak
            if result_query:
                email = result_query['email']
                success_infomaniak = infomaniak.delete_member(email)
                if success_infomaniak:
                    flash('Email supprimé sur Infomaniak avec succès', 'success')
                else:
                    flash('Erreur suppression Infomaniak', 'danger')

        elif 'reregister_member' in request.form:

            membre_id = request.form['id']

            # Retrieve the email and licence status from the database (for Infomaniak)
            cursor.execute("SELECT email, statut_swissbad FROM membres WHERE id = %s", (membre_id,))
            result_query = cursor.fetchone()
            cursor.execute("UPDATE membres SET membre_actuel = 'Oui' WHERE id=%s", (membre_id,))
            conn.commit()
            flash('Membre ajouté avec succès', 'success')

            # Delete email from Infomaniak
            if result_query:
                email, licence = result_query['email'], is_licence(result_query['statut_swissbad'])
                success_infomaniak = infomaniak.add_member(email, licence)
                if success_infomaniak:
                    flash('Email ajouté sur Infomaniak avec succès', 'success')
                else:
                    flash('Erreur ajout Infomaniak', 'danger')

        elif 'permanently_delete_member' in request.form:

            membre_id = request.form['id']
            cursor.execute("DELETE FROM membres WHERE id=%s", (membre_id,))
            conn.commit()
            flash('Membre supprimé définitivement avec succès', 'success')

        cursor.close()
        conn.close()

    return render_template('manage_members.html', fields=db.FIELDS, countries=db.COUNTRIES)


# Route to download database as csv file
@app.route('/download_csv')
@login_required
def download_csv():
    # Connect to the database
    conn = connect_db()

    # Query the database to get all the members
    query = "SELECT * FROM membres"
    df = pd.read_sql(query, conn)

    # Create a CSV buffer
    csv_buffer = StringIO()

    # Convert the DataFrame to CSV
    df.to_csv(csv_buffer, index=False)

    # Create a Flask Response and specify CSV as the content type
    response = Response(csv_buffer.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=membres.csv'

    return response


# Route to download list of membership fees
@app.route('/download_fees')
@login_required
def download_fees():
    # Connect to the database
    conn = connect_db()

    # Query the database to get all the members
    query = "SELECT nom, prenom, statut, pourcentage_cotisation, statut_swissbad, frais_IC FROM membres"
    df = pd.read_sql(query, conn)

    # Process dataframe to compute various fees
    df['Cotisation LUC'] = df.apply(lambda x: LUC_fees(x['statut'], x['pourcentage_cotisation']), axis=1)
    df['Frais interclubs'] = df.apply(lambda x: interclub_fees(x['frais_IC']), axis=1)
    df['Cotisation Swissbad'] = df.apply(lambda x: swissbad_fees(x['statut_swissbad']), axis=1)
    df['Total'] = df.apply(lambda x: x['Cotisation LUC'] + x['Frais interclubs'] + x['Cotisation Swissbad'], axis=1)

    # Rename columns
    df.rename(columns={"nom": "Nom", "prenom": "Prénom"}, inplace=True)
    # Remove useless columns
    df.drop(columns=['statut', 'pourcentage_cotisation', 'statut_swissbad', 'frais_IC'], inplace=True)

    # Create a CSV buffer
    csv_buffer = StringIO()

    # Convert the DataFrame to CSV
    df.to_csv(csv_buffer, index=False)

    # Create a Flask Response and specify CSV as the content type
    response = Response(csv_buffer.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=cotisations.csv'

    return response


# Compute LUC fees based on `statut` and `pourcentage_cotisation`
def LUC_fees(statut, pourcentage_cotisation):
    if statut == 'Etudiant':
        cotisation = 70
    elif statut == 'Collaborateur':
        cotisation = 190
    elif statut == 'Autre':
        cotisation = 240
    elif statut == 'Senior':
        cotisation = 100
    elif statut == 'Passif':
        cotisation = 50
    return int(cotisation * pourcentage_cotisation / 100)


# Compute Swissbad fees
def swissbad_fees(statut_swissbad):
    if statut_swissbad == 'LicenceAdulte':
        cotisation = 120
    elif statut_swissbad == 'LicencePlusAdulte':
        cotisation = 50
    elif statut_swissbad == 'LicencePlusJunior':
        cotisation = 20
    elif statut_swissbad == 'LicenceU19':
        cotisation = 40
    elif statut_swissbad == 'LicenceU15':
        cotisation = 20
    elif statut_swissbad == 'Actif':
        cotisation = 30
    else:  # `Passif` or `Absent`
        cotisation = 0
    return cotisation


# Compute interclub fees
def interclub_fees(frais_IC):
    if frais_IC == 'Oui':
        frais = 50
    else:
        frais = 0
    return frais


# Determine whether member is licencee based on statut_swissbad (for Infomaniak)
def is_licence(statut_swissbad):
    if ("Licence" in statut_swissbad) and not ("LicencePlus" in statut_swissbad):
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(debug=True)
