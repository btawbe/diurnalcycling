import pandas as pd
import psycopg2
from config import connection
import numpy as np
import matplotlib.pyplot as plt
import base64
import io

class DiurnalCycling:
    def __init__(self, connection):
        # Initialize the DiurnalCycling class with a database connection.
        self.connection = connection
        self.cursor = connection.cursor()
        self.characteristicname_and_fraction = self.get_distinct_characteristics()

    def get_distinct_characteristics(self, doi_filter=None):
        # Fetch distinct characteristic names and fractions from the database.
        # Combines 'characteristicname' and 'resultsamplefraction' fields into one.
        query = """
        SELECT DISTINCT CONCAT(characteristicname, ' ', resultsamplefraction) AS characteristicname_and_fraction
        FROM public.cycling
        WHERE (resultunit LIKE 'mg/L' or resultunit LIKE 'ug/L' or resultunit LIKE 'ppm')
        """
        if doi_filter:
            query += " and doi = '"+doi_filter + "'"
            params = (doi_filter,)
        else:
           query += " and doi = '10259766761-tk42'"
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            #return [row[0] for row in rows]  
            return [row[0].strip() for row in rows]
        except Exception as e:
            print(f"Erreur lors de la récupération des caractéristiques distinctes : {e}")
            return []

    def get_metals_by_location(self, location=None):
        """
        Fetch distinct metal names based on the selected location.
        :param location: The selected location to filter the data.
        :return: List of distinct metal names.
        """
        # Requête SQL pour récupérer les noms distincts des métaux
        query = """
        SELECT DISTINCT CONCAT(characteristicname, ' ', resultsamplefraction) AS characteristicname_and_fraction
        FROM public.cycling
        WHERE (resultunit LIKE 'mg/L' OR resultunit LIKE 'ug/L' or resultunit LIKE 'ppm')
        """
        if location:  # Si une location est fournie, on l'ajoute dans la requête
            query += " AND doi = '"+doi_filter + "'"
            params = (location,)
        else:  # Si aucune location n'est spécifiée, on peut utiliser une valeur par défaut
            query += " AND doi = '10259766761-tk42'"
            params = ('Default Location',)

        try:
            # Exécution de la requête
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Erreur lors de la récupération des noms des métaux : {e}")
            return []

    def get_metals_lesser_river(self):
        # Fetch distinct characteristic names and fractions from the database.
        # Combines 'characteristicname' and 'resultsamplefraction' fields into one.
        query = """
        SELECT DISTINCT CONCAT(characteristicname, ' ', resultsamplefraction) AS characteristicname_and_fraction
        FROM public.cycling
        WHERE (resultunit LIKE 'mg/L' or resultunit LIKE 'ug/L') AND doi IN ('1025976t1je-t809')
        """
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Erreur lors de la récupération des caractéristiques distinctes : {e}")
            return []

    def get_metals_annapolis_river(self):
        # Fetch distinct characteristic names and fractions from the database.
        # Combines 'characteristicname' and 'resultsamplefraction' fields into one.
        query = """
        SELECT DISTINCT CONCAT(characteristicname, ' ', resultsamplefraction) AS characteristicname_and_fraction
        FROM public.cycling
        WHERE (resultunit LIKE 'mg/L' or resultunit LIKE 'ug/L') AND doi IN ('10259766761-tk42')
        """
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Erreur lors de la récupération des caractéristiques distinctes : {e}")
            return []

    def get_distinct_locations(self):
        # Fetch distinct locations from the database.
        # Combines 'characteristicname' and 'resultsamplefraction' fields into one.
        query = """
        SELECT * FROM public.newlocations order by name
        """
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Erreur lors de la récupération des locations : {e}")
            return []

    def get_parameters(self):
        # Fetch distinct locations from the database.
        # Combines 'characteristicname' and 'resultsamplefraction' fields into one.
        query = """
        SELECT * FROM public.parameters where active=1
        """
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Erreur lors de la récupération des locations : {e}")
            return []

    def get_data(self, doi_filter=None, daycollect=None, monthn=None, yearn=None):
        # Retrieve data from the database with optional filtering by DOI.
        # Returns the result as a pandas DataFrame.
        query = """
        SELECT doi, activitystartdate, activitystarttime, resultvalue, resultunit,
               CONCAT(characteristicname, ' ', resultsamplefraction) AS characteristicname_and_fraction
        FROM public.cycling
        """
        
        # Add a DOI filter to the query if specified
        if doi_filter:
           if daycollect:
              query += " WHERE activitystartdate = '"+daycollect + "' and doi = '" + doi_filter + "'"
              params = (daycollect,)
           else:
              if yearn=="AllYears":
                  query += " WHERE doi = '"+doi_filter + "'"  
              else:
                  query += " WHERE activitystartdate like  '%" + yearn + "-%'"

              if monthn in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
                  query += " and activitystartdate like  '%-"+monthn + "-%' and doi = '" + doi_filter + "'" 
              else:
                  query += " and  doi = '"+doi_filter + "'"
                  params = (doi_filter,)
           params = (doi_filter,)
        else:
            # Default query retrieves multiple DOIs
            query += " WHERE doi IN ('10259766761-tk42')"
            params = ()

        try:
            print(query)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            # Convert query results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=['doi', 'activitystartdate', 'activitystarttime', 'resultvalue', 'resultunit',
                                              'characteristicname_and_fraction'])

            self.connection.commit()
            return df
        except (Exception, psycopg2.Error) as error:
            print("Error:", error)
            return None

    def get_data_for_name(self, doi_filter=None, mtlname=None):
        # Retrieve data from the database with optional filtering by DOI.
        # Returns the result as a pandas DataFrame.
        query = """
        SELECT doi, activitystartdate, activitystarttime, resultvalue, resultunit,
               CONCAT(characteristicname, ' ', resultsamplefraction) AS characteristicname_and_fraction
        FROM public.cycling
        """

        # Add a DOI filter to the query if specified
        if doi_filter:
           query += " WHERE doi='" + doi_filter + "' and (CONCAT(characteristicname, ' ', resultsamplefraction) = '" +mtlname + "' or characteristicname='" +mtlname + "')";
           #query += " WHERE characteristicname='" +mtlname + "'";
  
        try:
            print(query)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            # Convert query results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=['doi', 'activitystartdate', 'activitystarttime', 'resultvalue', 'resultunit',
                                              'characteristicname_and_fraction'])
            #Somnetimes we have space at the end of characteristicname_and_fraction when resultsamplefraction=''
            #We delete this space we use
            df['characteristicname_and_fraction'] = df['characteristicname_and_fraction'].str.strip()
            self.connection.commit()
            return df
        except (Exception, psycopg2.Error) as error:
            print("Error:", error)
            return None

    def normalizedata(self, y_values):
        """Normalize values to a 0-1 range for consistent plotting scale."""
        xv=(y_values-y_values.min())/(y_values.max()-y_values.min())
        return xv

    def format_time_ticks(self, x, pos):
        # Convert decimal time (e.g., 12.5) to HH:MM format
        hours = int(x)
        minutes = int((x - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def plot_interpolations(self, df_metal, result_df, time_slot=None, doi_filter=None):
        """
        Generate interpolation plots for distinct metals and parameters, return them as base64 images.
        """
        # Convert time strings to float (e.g., 12:30:00 -> 12.5)
        def convert_to_float(time_str):
            time_obj = pd.to_datetime(time_str, format='%H:%M:%S')
            return time_obj.hour + time_obj.minute / 60.0

        # List to store base64-encoded images for each plot
        image_base64_list = []
        # Unique metals and parameters
        unique_metals = df_metal['characteristicname_and_fraction'].unique()
        if result_df is not None and not result_df.empty:
            unique_parameters = result_df['characteristicname_and_fraction'].unique()
        else:
            unique_parameters = []  # Liste vide si le DataFrame est vide ou None

        if doi_filter == "10.25976/6761-tk42":
            allowed_times = [f"{hour:02}:{minute:02}:00" for hour in range(8, 23) for minute in [0, 15, 30, 45]]
            df_metal = df_metal[df_metal['activitystarttime'].isin(allowed_times)]
            if result_df is not None and not result_df.empty:
                result_df = result_df[result_df['activitystarttime'].isin(allowed_times)]

        time_slot1, time_slot2 = 8, 23.5
        if time_slot:
            time_slot_str = time_slot.split('.')
            time_slot1 = int(time_slot_str[0])
            time_slot2 = int(time_slot_str[1])

        for metal in unique_metals:
            # Create a plot for the current metal
            fig, ax = plt.subplots(figsize=(20, 6))

            # Plot metal data
            metal_data = df_metal[df_metal['characteristicname_and_fraction'] == metal]
            metal_data = metal_data.sort_values(by='activitystarttime').drop_duplicates(subset=['activitystarttime'])
            metal_data['resultvalue'] = self.normalizedata(metal_data['resultvalue'])

            if not metal_data.empty:
                metal_data = metal_data.sort_values('activitystarttime')
                metal_data['activitystarttime_float'] = metal_data['activitystarttime'].apply(convert_to_float)
                metal_data['interpolated_values'] = metal_data['resultvalue'].interpolate(method='linear')
                ax.plot(
                    metal_data['activitystarttime_float'],
                    metal_data['interpolated_values'],
                    label=f'Metal ({metal})',
                    color='orange',
                    marker=None
                )
            # Define a color map using a color palette
            #colors = plt.cm.get_cmap("tab10", len(unique_parameters))  # 'tab10' is a palette with distinct colors
            colors = ['blue', 'red', 'green', 'yellow', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan',
                      'magenta', 'plum', 'black', 'white', 'indigo', 'violet', 'teal', 'peach', 'gold', 'silver',
                      'navy', 'maroon', 'lime', 'beige', 'charcoal', 'turquoise', 'coral', 'crimson', 'mint', 'lavender']
            i=1
            # Plot parameters on the same plot
            for param in unique_parameters:
                param_data = result_df[result_df['characteristicname_and_fraction'] == param]
                param_data = param_data.sort_values(by='activitystarttime').drop_duplicates(subset=['activitystarttime'])
                param_data['resultvalue'] = self.normalizedata(param_data['resultvalue'])

                if not param_data.empty:
                    param_data = param_data.sort_values('activitystarttime')
                    param_data['activitystarttime_float'] = param_data['activitystarttime'].apply(convert_to_float)
                    param_data['interpolated_values'] = param_data['resultvalue'].interpolate(method='linear')
                    ax.plot(
                        param_data['activitystarttime_float'],
                        param_data['interpolated_values'],
                        label=f'Param ({param})',
                        color=colors[i],
                        marker=None
                    )
                    i=i+1
            # Customize axes and titles
            ax.set_title(f"Interpolation of Metal ({metal}) with Parameters Over Time")
            ax.set_xlabel("Activity Start Time (hours)")
            ax.set_ylabel("Result Value")
            ax.legend()
            ax.set_xlim([time_slot1, time_slot2])

            # Save plot to a buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)

            # Convert plot to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()

            # Add image to list
            image_base64_list.append(image_base64)

        # Return base64-encoded images
        return image_base64_list


    @staticmethod
    def convert_to_float(time_str):
        """Convert time string to float representing hours."""
        time_obj = pd.to_datetime(time_str, format='%H:%M:%S')
        return time_obj.hour + time_obj.minute / 60.0

    def plot_separate_interpolations(self, df_metal, result_df, time_slot=None, doi_filter=None):
        """
        Generate interpolation plots for distinct parameters and metals.
        Display pH, Temperature, and Metal concentration in separate subplots for each parameter or metal.
        """
        image_base64_list = []

        if result_df is not None and not result_df.empty:
            unique_parameters = result_df['characteristicname_and_fraction'].unique()
        else:
            unique_parameters = []  # Liste vide si le DataFrame est vide ou None

        if doi_filter == "10259766761-tk42":
            allowed_times = [f"{hour:02}:{minute:02}:00" for hour in range(8, 23) for minute in [0, 15, 30, 45]]
            df_metal = df_metal[df_metal['activitystarttime'].isin(allowed_times)]
            if result_df is not None and not result_df.empty:
                result_df = result_df[result_df['activitystarttime'].isin(allowed_times)]

        time_slot1, time_slot2 = 8, 23.5
        if time_slot:
            time_slot_str = time_slot.split('.')
            time_slot1 = int(time_slot_str[0])
            time_slot2 = int(time_slot_str[1])

        def generate_plot(data, title_prefix, ax):
            if not data.empty:
                data['activitystarttime_float'] = data['activitystarttime'].apply(self.convert_to_float)
                data['interpolated_values'] = data['resultvalue'].interpolate(method='linear')
                ax.plot(
                    data['activitystarttime_float'],
                    data['interpolated_values'],
                    marker='o',
                    label=f'{title_prefix}',
                    color='orange'
                )

                ax.set_title(f'{title_prefix}')
                ax.set_xlabel('Time (hours)')
                ax.set_ylabel('Normalized Value')
                ax.legend()
                ax.set_xlim([time_slot1, time_slot2])
                ax.set_xticks(np.arange(time_slot1, time_slot2 + 1, 1))
        # Plot for parameters from result_df
        for param in unique_parameters:
            fig, ax = plt.subplots(1, 1, figsize=(16, 5))
            fig.suptitle(f"Interpolation of Parameter ({param}) Over Time", fontsize=16)
            param_data = result_df[result_df['characteristicname_and_fraction'] == param]
            param_data = param_data.sort_values(by='activitystarttime').drop_duplicates(subset=['activitystarttime'])
            param_data['resultvalue'] = self.normalizedata(param_data['resultvalue'])
            generate_plot(param_data, f'Parameter ({param})', ax)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            image_base64_list.append(image_base64)
            plt.close()

        # Plot for metals from df_metal
        unique_metals = df_metal['characteristicname_and_fraction'].unique()
        for metal in unique_metals:
            fig, ax = plt.subplots(1, 1, figsize=(16, 5))
            fig.suptitle(f"Interpolation of Metal ({metal}) Over Time", fontsize=16)
            metal_data = df_metal[df_metal['characteristicname_and_fraction'] == metal]
            metal_data = metal_data.sort_values(by='activitystarttime').drop_duplicates(subset=['activitystarttime'])
            metal_data['resultvalue'] = self.normalizedata(metal_data['resultvalue'])
            generate_plot(metal_data, f'Metal ({metal})', ax)

            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            image_base64_list.append(image_base64)
            plt.close()

        return image_base64_list

    def load_and_filter_data(self, selected_season, selected_month, selected_year, df):
        # Load and filter the data based on season, month, and year.
        # Returns a filtered and averaged DataFrame.
        df['activitystartdate'] = df['activitystartdate'].str.strip()
        df['month'] = df['activitystartdate'].astype(str).str[5:7]
        df['year'] = df['activitystartdate'].astype(str).str[0:4]
        
        # Determine the months associated with the chosen season
        season_months = {
            'AllSeason': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
            'Winter': ['12', '01', '02'],
            'Spring': ['03', '04', '05'],
            'Summer': ['06', '07', '08'],
            'Autumn': ['09', '10', '11']
        }
        
        # Filtrer per season (if we select a season)
        if selected_season in season_months:
            selected_months = season_months[selected_season]
        elif selected_month != 'AllMonths':
            selected_months = [str(selected_month).zfill(2)]
        else:
            selected_months = season_months['AllSeason']

        filtered_df = df

        if selected_year != 'AllYears':
            filtered_df = filtered_df[filtered_df['year'] == str(selected_year)]
        if selected_months:
            filtered_df = filtered_df[filtered_df['month'].isin(selected_months)]


        # Drop NAN
        filtered_df = filtered_df.dropna(subset=['activitystarttime', 'characteristicname_and_fraction', 'resultvalue'])
        # Ensure that 'resultvalue' is of type numeric
        filtered_df['resultvalue'] = pd.to_numeric(filtered_df['resultvalue'], errors='coerce')

        # Calculate the average of 'resultvalue' for each combination of 'activitystarttime' and 'characteristicname_and_fraction'
        mean_resultvalues = (
           filtered_df.groupby(['activitystarttime', 'characteristicname_and_fraction'])['resultvalue']
           .mean()
           .reset_index()
        )

        # Sort results
        mean_resultvalues = mean_resultvalues.sort_values(by=['characteristicname_and_fraction', 'activitystarttime'])
        return mean_resultvalues

    def preprocessing_data(self, df, characteristics, location, season, month, year, selected_values):
        """
        Preprocesses the data by filtering and normalizing based on user input.
        """
        # Filter metal data based on user selection
        if characteristics == '1':
            filtered_data_metal = df[(df['resultunit'].isin(['mg/L', 'ug/L', 'ppm']))].dropna(subset=['resultvalue'])
        else:
            filtered_data_metal = df[(df['resultunit'].isin(['mg/L', 'ug/L', 'ppm'])) & 
                                     (df['characteristicname_and_fraction'] == characteristics)].dropna(subset=['resultvalue'])
        

        filtered_data_metal['characteristicname_and_fraction'] = filtered_data_metal['characteristicname_and_fraction'].str.strip()

        # Apply seasonal, monthly, and yearly filters
        filtered_data_metal = self.load_and_filter_data(season, month, year, filtered_data_metal).dropna(subset=['resultvalue'])

        # Normalize result values for each subset
        if not filtered_data_metal.empty:
            filtered_data_metal['resultvalue'] = filtered_data_metal['resultvalue'].astype(float)
        return filtered_data_metal

    def preprocessing_data_new(self, df, characteristics, location, season, month, year, selected_ids):
        """
        Preprocesses the data by filtering and normalizing based on user input.
        """
        # Delete space from begining and end of each cloumn in df
        df = df.apply(lambda col: col.str.strip() if col.dtype == 'object' else col)
        # Stocke les DataFrames filtrés
        filtered_data_list = []
        filtered_sunrise_list = []
        # Filer the data for all parameters selected
        for param in selected_ids:
            filtered_data = df[df['characteristicname_and_fraction'] == param].dropna(subset=['resultvalue'])
            filtered_sunrise_list.append(filtered_data)

        # Concatenates all filtered data into a single DataFrame
        result_df = pd.concat(filtered_data_list, ignore_index=True) if filtered_data_list else pd.DataFrame()
        df_sunrise = pd.concat(filtered_sunrise_list, ignore_index=True) if filtered_sunrise_list else pd.DataFrame()
        filtered_data_metal = df[(df['resultunit'].isin(['mg/L', 'ug/L', 'ppm'])) &
                                 (df['characteristicname_and_fraction'] == characteristics)].dropna(subset=['resultvalue'])
        filtered_data_metal['characteristicname_and_fraction'] = filtered_data_metal['characteristicname_and_fraction'].str.strip()
        filtered_data_metal_new = filtered_data_metal
        #filtered_data_metal_new = self.load_and_filter_data(season, month, year, filtered_data_metal).dropna(subset=['resultvalue'])
        

        return result_df, filtered_data_metal_new, df_sunrise

    def generate_dropdown1(self, selected_value):
        """
        Génère le HTML pour le menu déroulant des saisons en fonction de la valeur sélectionnée.
        """
        # Evaluating conditions before generating HTML
        selected_all_season = 'selected' if selected_value == 'AllSeason' else ''
        selected_winter = 'selected' if selected_value == 'Winter' else ''
        selected_spring = 'selected' if selected_value == 'Spring' else ''
        selected_summer = 'selected' if selected_value == 'Summer' else ''
        selected_autumn = 'selected' if selected_value == 'Autumn' else ''

        # Returns the HTML code with the selected option
        return f"""
        <label for="dropdown1">Select a Season:</label>
        <select id="dropdown1" name="dropdown_season">
            <option value="AllSeason" {selected_all_season}>AllSeason</option>
            <option value="Winter" {selected_winter}>Winter</option>
            <option value="Spring" {selected_spring}>Spring</option>
            <option value="Summer" {selected_summer}>Summer</option>
            <option value="Autumn" {selected_autumn}>Autumn</option>
        </select>
        
        """

    def generate_dropdown2(self, selected_value):
        """
        Génère le HTML pour le menu déroulant des années en fonction de la valeur sélectionnée.
        """
        # Conditions for each year
        selected_all_years = 'selected' if selected_value == 'AllYears' else ''
        selected_2017 = 'selected' if selected_value == '2017' else ''
        selected_2018 = 'selected' if selected_value == '2018' else ''
        selected_2019 = 'selected' if selected_value == '2019' else ''
        selected_2020 = 'selected' if selected_value == '2020' else ''
        selected_2021 = 'selected' if selected_value == '2021' else ''
        selected_2022 = 'selected' if selected_value == '2022' else ''
        selected_2023 = 'selected' if selected_value == '2023' else ''
        selected_2024 = 'selected' if selected_value == '2024' else ''
        selected_2025 = 'selected' if selected_value == '2025' else ''
        selected_2026 = 'selected' if selected_value == '2026' else ''

        # Generation of year options
        return f"""
        <label for="dropdown2">Select a Year:</label>
        <select id="dropdown2" name="dropdown_year">
            <option value="AllYears" {selected_all_years}>AllYears</option>
            <option value="2017" {selected_2017}>2017</option>
            <option value="2018" {selected_2018}>2018</option>
            <option value="2019" {selected_2019}>2019</option>
            <option value="2020" {selected_2020}>2020</option>
            <option value="2021" {selected_2021}>2021</option>
            <option value="2022" {selected_2022}>2022</option>
            <option value="2023" {selected_2023}>2023</option>
            <option value="2024" {selected_2024}>2024</option>
            <option value="2025" {selected_2025}>2025</option>
            <option value="2026" {selected_2026}>2026</option>
        </select>
        
        """

    def generate_dropdown3(self, selected_value):
        """
        Génère le HTML pour le menu déroulant des mois en fonction de la valeur sélectionnée.
        """
        selected_value = str(selected_value) if selected_value else 'AllMonths'  # Sets 'AllMonths' to default if selected_value is empty or None
        
        # Defining the selected options for each month
        selected_all_months = 'selected' if selected_value == 'AllMonths' else ''
        selected_01 = 'selected' if selected_value == '01' else ''
        selected_02 = 'selected' if selected_value == '02' else ''
        selected_03 = 'selected' if selected_value == '03' else ''
        selected_04 = 'selected' if selected_value == '04' else ''
        selected_05 = 'selected' if selected_value == '05' else ''
        selected_06 = 'selected' if selected_value == '06' else ''
        selected_07 = 'selected' if selected_value == '07' else ''
        selected_08 = 'selected' if selected_value == '08' else ''
        selected_09 = 'selected' if selected_value == '09' else ''
        selected_10 = 'selected' if selected_value == '10' else ''
        selected_11 = 'selected' if selected_value == '11' else ''
        selected_12 = 'selected' if selected_value == '12' else ''

        # Returns the HTML code with the selected option
        return f"""
        <label for="dropdown3">Select a Month:</label>
        <select id="dropdown3" name="dropdown_month">
            <option value="AllMonths" {selected_all_months}>AllMonths</option>
            <option value="01" {selected_01}>1</option>
            <option value="02" {selected_02}>2</option>
            <option value="03" {selected_03}>3</option>
            <option value="04" {selected_04}>4</option>
            <option value="05" {selected_05}>5</option>
            <option value="06" {selected_06}>6</option>
            <option value="07" {selected_07}>7</option>
            <option value="08" {selected_08}>8</option>
            <option value="09" {selected_09}>9</option>
            <option value="10" {selected_10}>10</option>
            <option value="11" {selected_11}>11</option>
            <option value="12" {selected_12}>12</option>
        </select>
        
        """

    def generate_dropdown4(self, selected_value):
        """
        Génère le HTML pour le menu déroulant des locations en fonction de la valeur sélectionnée.
        """
        selected_value = str(selected_value) if selected_value else '10259766761-tk42'  # Sets 'AllLocations' to default if selected_value is empty or None
        locations = self.get_distinct_locations()
        # Construire les options du dropdown dynamiquement
        options_html = "<option>Choose a location</option>"
        for location in locations:
            doi = location[1]  # Assurez-vous que 'doi' est dans la 2e colonne
            name = location[2]  # Assurez-vous que 'name' est dans la 3e colonne
            selected_attr = 'selected="selected"' if selected_value == doi else ""
            options_html += f'<option value="{doi}" {selected_attr}>{name}</option>' 
       # Returns the HTML code with the selected option
        # Retourner le menu déroulant HTML
        return f"""
        <label for="dropdown4">Location:</label>
        <select id="dropdown4" name="dropdown_location" style="max-width: 188px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            {options_html}
        </select>        
        """

    def generate_parameters(self, selected_ids):
        """
        Generate the parameters as checkboxes.
        Returns:
            str: HTML code with checkboxes for parameters.
        """
        parameters = self.get_parameters()

        # Build checkboxes dynamically
        checkboxes_html = """<div><input type="checkbox" id="graph_all" name="graph_all" onclick="toggleAllCheckboxes(this)">
            <label for="graph_all">&nbsp;<strong>Graph All Parameters</strong></label>&nbsp;"""
        for parameter in parameters:
            id = str(parameter[1])  # Assuming 'id' is in the first column
            name = parameter[1]  # Assuming 'name' is in the second column
            checked_attr = 'checked="checked"' if selected_ids and id in selected_ids else ""
            checkboxes_html += f"""
                <input type="checkbox" id="param_{id}" name="parameters" value="{name}" {checked_attr}>
                <label for="param_{id}">{name}</label>&nbsp;
            """
        checkboxes_html += "</div>"

        return checkboxes_html

    def generate_dropdown5(self, selected_value):
        """
        Generates the HTML for the display's drop-down menu based on the selected value.
        """
        # Sets selected_value as a default value if empty or None
        selected_value = str(selected_value) if selected_value else '1'  # By default, select 'Display Data and Graphs'
        
        # Setting the selected options for each display value
        selected_display_data_graphs = 'selected' if selected_value == '3' else ''
        selected_display_data_only = 'selected' if selected_value == '2' else ''
        selected_display_graphs_only = 'selected' if selected_value == '1' else ''

        # Returns the HTML code with the selected option
        return f"""
        <label for="dropdown5">Display:</label>
        <select id="dropdown5" name="dropdown_choice">
            <option value="1" {selected_display_graphs_only}>Display Graphs Only</option>
            <option value="2" {selected_display_data_only}>Display Data Only</option>
            <option value="3" {selected_display_data_graphs}>Display Data and Graphs</option>
        </select>
        
        """

    def generate_dropdown6(self, selected_value):
        """
        Génère le HTML pour le menu déroulant de l'affichage en fonction de la valeur sélectionnée.
        """
        # Sets selected_value as a default value if empty or None
        selected_value = str(selected_value) if selected_value else '1'  # By default, select 'Display Data and Graphs'

        # Setting the selected options for each display value
        selected_separate_graphs = 'selected' if selected_value == '1' else ''
        selected_combine_graphs = 'selected' if selected_value == '2' else ''

        # Returns the HTML code with the selected option
        return f"""
        <label for="dropdown6">Display Separate Graphs:</label>
        <select id="dropdown6" name="graphs_separate">
            <option value="1" {selected_separate_graphs}>Yes</option>
            <option value="2" {selected_combine_graphs}>No</option>
        </select>
        
        """


    def generate_time_slot(self, selected_value):
        """
        Génère le HTML pour le menu déroulant des années en fonction de la valeur sélectionnée.
        """
        # Conditions for each year
        selected_8_22 = 'selected' if selected_value == '8.23' else ''
        selected_8_17 = 'selected' if selected_value == '8.18' else ''
        selected_17_22 = 'selected' if selected_value == '17.23' else ''

        # Generation of year options
        return f"""
        <label for="TimeSlot">Select a Time Slot:</label>
        <select id="timneslot" name="time_slot">
            <option value="17.23" {selected_17_22}>5 PM to 10 PM</option>
            <option value="8.23" {selected_8_22}>8 Am to 10 PM</option>
            <option value="8.18" {selected_8_17}>8 Am to 5 PM</option>
        </select>
        <br>
        """

    def generate_categorylocation(self, selected_value):
        """
        Génère le HTML pour le menu déroulant des catégories de localisation avec des options fixes.
        """
        selected_value = str(selected_value) if selected_value else '4'  # Valeur par défaut : '1' = 24-Hour Cycling

        options = [
            ('1', '24-Hour Cycling'),
           ('23', 'Day and Night Cycling'),
            ('2', 'Day Cycling'),
            ('3', 'Night Cycling'),
            ('4', 'All')
        ]

        # Construire les options HTML
        options_html = ""
        for category_id, category_name in options:
            selected_attr = 'selected="selected"' if selected_value == category_id else ""
            options_html += f'<option value="{category_id}" {selected_attr}>{category_name}</option>'

        # Retourner le menu déroulant HTML
        return f"""
        <label for="category_location">Data Category:</label>
        <select id="category_location" name="category_location" style="max-width: 148px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            {options_html}
        </select>
        """

    def generate_display_button(self):
        return """
        <button type="submit" class="btn btn-primary mt-3">Display</button>
        """

    def display_all_dropdowns(self, selected_values):
        
        selected_season = selected_values.get("dropdown_season", "AllSeason")
        selected_year = selected_values.get("dropdown_year", "AllYears")
        selected_month = selected_values.get("dropdown_month", "AllMonths")
        selected_location = selected_values.get("dropdown_location", "1025976t1je-t809")  # For example, default value for "LESSER SLAVE RIVER"
        selected_category = selected_values.get("category_location", "4")
        selected_display = selected_values.get("dropdown_choice", "1")  # Default: "Display Graphs"
        selected_separate = selected_values.get("graphs_separate", "1")  # Default: "Display Separate"
        selected_timeslot = selected_values.get("time_slot", "8.23")
        page = selected_values.get("page", "1")
        daycollect = selected_values.get("daycollect")
        # Retrieve distinct values for the dropdown
        distinct_characteristics = sorted(self.get_distinct_characteristics(selected_location))

        # Retrieve the selected value for "characteristics" from selected_values ​​(default "1" if no value)
        selected_characteristic = selected_values.get("characteristics", "1")
        
        # Generate HTML code for the feature drop-down menu, with the selected value
        dropdown_menu_char = f"""
        <label for="characteristics">Metal Name:</label>
        <select id="characteristics" name="characteristics"  style="width: 160px;">
            {"".join(f"<option value='{char}' {'selected' if selected_characteristic == char else ''}>{char}</option>" for char in distinct_characteristics)}
        </select>
        
        """

        # Combine the three dropdown menus and the button into an HTML form
        return f"""
            {self.generate_dropdown1(selected_season)}<br>
            {self.generate_dropdown2(selected_year)}<br>
            {self.generate_dropdown3(selected_month)}<br>
            <label for="date">Select a Day :</label>
            <input type="date" value="{daycollect}" id="daycollect" name="daycollect"><br>
            {self.generate_categorylocation(selected_category)}<br>
            {self.generate_dropdown4(selected_location)}<br>
            {dropdown_menu_char}<span id="loading-message" style="display:none; color: orange; font-weight: bold;"></span><br>
            {self.generate_dropdown5(selected_display)}<br>
            {self.generate_dropdown6(selected_separate)}<br>
            {self.generate_time_slot(selected_timeslot)}<br>
            <input type="hidden" name="page" value="{page}">  
            {self.generate_display_button()}
        </form>

        <script type="text/javascript">
            document.addEventListener("DOMContentLoaded", function () {{
                const url = window.location.href;
                const form = document.getElementById("data-form");
                if (url.includes("?page=")) {{
                    form.submit();
                }}
            }});
        </script>
        """

