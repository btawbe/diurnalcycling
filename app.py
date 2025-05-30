from flask import Flask, render_template, request, jsonify
from get_data import DiurnalCycling
from config import connection
import pandas as pd

app = Flask(__name__)

# Initialisation de l'instance DiurnalCycling
cycling_data = DiurnalCycling(connection)
ann_location='10.25976/6761-tk42'
less_location='10.25976/t1je-t809'

# Ca nous evite de telecharger chaque fois les donnees sur le map
# On telecharge ces donnees une seule fois
@app.before_first_request
def load_data_once():
    """Charge les données une seule fois avant la première requête."""
    global Annapolis, Lesser, metal_locations, dist_metal_names
    Annapolis = cycling_data.get_metals_lesser_river()
    Lesser = cycling_data.get_metals_annapolis_river()
    metal_locations = cycling_data.get_distinct_locations()
    #dist_metal_names = cycling_data.get_metal_names()

@app.route('/')
def index():
    global Annapolis, Lesser, metal_locations  # Permet d'accéder aux variables globales
    # Initialisez selected_values avec des valeurs par défaut
    selected_values = {
        'dropdown_season': 'AllSeason',
        'dropdown_year': 'AllYears',
        'dropdown_month': 'AllMonths',
        'dropdown_location': None,
        'dropdown_choice': '1'
    }
    selected_ids = []
    if request.method == 'POST':
        # Récupérer les IDs des paramètres cochés
        selected_ids = request.form.getlist('parameters') 
    # Generate dropdown menus and render the main page with no data initially
    dropdown_html = cycling_data.display_all_dropdowns(selected_values)
    # Generate checkboxes for parameters
    generate_parameters = cycling_data.generate_parameters(selected_ids)
    # Generate metals list name by location, by default Lesser Slave river
    distinct_name_metals=cycling_data.get_distinct_characteristics(doi_filter=None)
    #less_location='10.25976/t1je-t809'
    current_url = request.url  # Obtain the actual url
    return render_template('index.html', dropdown_html=dropdown_html, metal_locations=metal_locations, parameters=generate_parameters, current_url=current_url, data=None, season=None, year=None, month=None, Annapolis=Annapolis, Lesser=Lesser, ann_location=ann_location, less_location=less_location)

@app.route('/display', methods=['GET', 'POST'])
def display():
    # Pas besoin de rechargés Annapolis et Lesser, elles sont déjà chargées
    global Annapolis, Lesser, metal_locations  # Permet d'accéder aux variables globales
    # Retrieve user selections from the form submission
    season = request.form.get('dropdown_season')
    year = request.form.get('dropdown_year')
    month = request.form.get('dropdown_month')
    location = request.form.get('dropdown_location')
    daycollect= request.form.get('daycollect')
    characteristics=request.form.get('characteristics')
    choicedisplay=request.form.get('dropdown_choice')
    time_slot=request.form.get('time_slot')
    graphs_separate=request.form.get('graphs_separate')
    selected_ids = []
    if request.method == 'POST':
        # Récupérer les IDs des paramètres cochés
        selected_ids = request.form.getlist('parameters')
    #Annapolis = cycling_data.get_metals_lesser_river()
    #Lesser = cycling_data.get_metals_annapolis_river()
    distinct_name_metals=cycling_data.get_distinct_characteristics(doi_filter=location)
    current_url = request.url  # Obtain the actual url
    # Fetch data based on the selected location
    df = cycling_data.get_data(doi_filter=location, daycollect=daycollect, monthn=month, yearn=year)
    # Drop rows where 'resultvalue' is NaN
    df = df.dropna(subset=['resultvalue'])
    # Render the updated page with the selected data and dropdowns
    if request.method == 'POST':
        # Récupérez les valeurs envoyées via POST
        selected_values = request.form.to_dict()
    if request.method == 'GET':
        # Récupérez les valeurs envoyées via GET
        selected_values = request.args.to_dict()

    result_df, data_metal_n, df_sunrise = cycling_data.preprocessing_data_new(df, characteristics, location, season, month, year, selected_ids)
     
    # Render the updated page with the selected data and dropdowns
    dropdown_html = cycling_data.display_all_dropdowns(selected_values)
    # Generate checkboxes for parameters
    generate_parameters = cycling_data.generate_parameters(selected_ids)
    #result_df_new = result_df.to_json(orient='records')
    result_df_new = result_df.to_html(classes='table table-striped') if not result_df.empty else "No data available for parameters checked."
    #data_metal_new = data_metal_n.to_html(classes='table table-striped') if not data_metal_n.empty else "No data available for metal."
    df_sunrise_dict = df_sunrise.to_dict(orient='records')
    data_metal_new = data_metal_n.to_dict(orient='records')  
    #df_sunrise_dict = df_sunrise.to_html(classes='table table-striped') if not result_df.empty else "No data available for parameters checked."
    return render_template(
       'index.html',
       dropdown_html=dropdown_html,
       parameters=generate_parameters,
       selected_ids=selected_ids,
       season=season,
       choicedisplay=choicedisplay,
       characteristics=characteristics,
       year=year,
       month=month,
       daycollect=daycollect,
       time_slot=time_slot,
       selected_values =selected_values,
       Annapolis=Annapolis,
       Lesser=Lesser,
       location=location,
       current_url=current_url,
       ann_location=ann_location,
       less_location=less_location,
       result_df_new = result_df_new,
       df_sunrise = df_sunrise_dict,
       data_metal_new = data_metal_new,
       metal_locations=metal_locations
    )
@app.route('/map')
def display_map():
    return render_template('map.html')
# Route pour la page "Profile"
@app.route('/profile')
def profile():
    return render_template('profile.html')

# Route pour la page "Help"
@app.route('/help')
def help():
    return render_template('help.html')

# Route pour la page "Add Location"
@app.route('/add-location')
def add_location():
    return render_template('add_location.html')


# Route pour la page "sunrise"
@app.route('/sunrise')
def sunrise():
    return render_template('sunrise.html')

# Route pour la page "Calculated Parameters"
@app.route('/calculated-parameters')
def calculated_parameters():
    return render_template('calculated_parameters.html')


@app.route('/getmetals', methods=['GET', 'POST'])
def get_metals():
    # Retrieve the location sent from the frontend
    selected_location = request.json.get('location')
    # Call the get_distinct_characteristics to retrieve the metal names for the location
    metal_names=cycling_data.get_distinct_characteristics(selected_location)
    return jsonify({'metals': metal_names}) 



@app.route('/metalanalysis')
def metalanalysis():
    # Retrieve the location sent from the frontend
    mtlname = request.args.get('mtlname')
    location = request.args.get('location')
    # Call the get_distinct_characteristics to retrieve the metal names for the location
    #metal_names=cycling_data.get_distinct_characteristics(selected_location)
    data_df=cycling_data.get_data_for_name(location, mtlname)
    data_for_name = data_df.to_dict(orient='records')  # Convertir en liste de dictionnaires
    return render_template('metalanalysis.html', mtlname=mtlname, data_for_name=data_for_name)
if __name__ == '__main__':
    app.run(debug=True)
