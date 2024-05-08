import json
import os
import pyproj

# Get current directory
current_dir = os.path.dirname(__file__)


# Read JSON files
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_coordinates_data():
    coordinate_file = os.path.join(current_dir, 'koordinaatit.json')
    return read_json_file(coordinate_file)

def get_population_data():
    population_file = os.path.join(current_dir, 'populaatio.json')
    return read_json_file(population_file)

def get_population_density_data():
    populationDensity_file = os.path.join(current_dir, 'asukastiheys.json')
    return read_json_file(populationDensity_file)

def get_income_data():
    income_file = os.path.join(current_dir, 'tulot.json')
    return read_json_file(income_file)

def get_education_data():
    education_file = os.path.join(current_dir, 'koulutus.json')
    return read_json_file(education_file)

def get_activity_data():
    activity_file = os.path.join(current_dir, 'toiminta.json')
    return read_json_file(activity_file)





def get_coordinates_and_postal_codes(coordinates_data):
    coordinates = coordinates_data['dataset']['value']
    postal_codes = coordinates_data['dataset']['dimension']['Postinumeroalue']['category']['index']
    return coordinates, postal_codes

def get_median_incomes(income_data):
    return income_data['dataset']['value']

def get_population_counts_and_average_ages(population_data):
    population_count = population_data['dataset']['value'][::4]
    average_age = population_data['dataset']['value'][3::4]
    return population_count, average_age

def get_population_counts_and_surface_areas(populationDensity_data):
    surface_areas_m2 = populationDensity_data['dataset']['value'][::2]
    population_counts = populationDensity_data['dataset']['value'][1::2]
    surface_areas_km2 = [area / 1000000 for area in surface_areas_m2]
    population_counts = [int(count) for count in population_counts]
    return population_counts, surface_areas_km2

def get_activity_percentages(activity_data, postal_codes):
    postal_codes = activity_data['dataset']['dimension']['Postinumeroalue']['category']['index']
    population_count = activity_data['dataset']['value'][::7]

    employed_counts = activity_data['dataset']['value'][1::7]
    unemployed_counts = activity_data['dataset']['value'][2::7]
    children_counts = activity_data['dataset']['value'][3::7]
    student_counts = activity_data['dataset']['value'][4::7]
    retired_counts = activity_data['dataset']['value'][5::7]
    other_counts = activity_data['dataset']['value'][6::7]

    activityPercentages_by_area = {}

    for postal_code in postal_codes:
        postal_code_str = str(postal_code)
        area_population_index = postal_codes[postal_code]
        total_population = population_count[area_population_index]

        employed_percentage = employed_counts[area_population_index] / total_population * 100
        unemployed_percentage = unemployed_counts[area_population_index] / total_population * 100
        kids_percentage = children_counts[area_population_index] / total_population * 100
        student_percentage = student_counts[area_population_index] / total_population * 100
        retired_percentage = retired_counts[area_population_index] / total_population * 100
        other_percentage = other_counts[area_population_index] / total_population * 100

        activityPercentages_by_area[postal_code_str] = {
            "Employed": employed_percentage,
            "Unemployed": unemployed_percentage,
            "Kids": kids_percentage,
            "Students": student_percentage,
            "Retired": retired_percentage,
            "Other": other_percentage
        }

    return activityPercentages_by_area

def get_area_names():
    area_names = {
        "33100": "Tampere Keskus",
        "33180": "Lapinniemi-Käpylä",
        "33200": "Tampere Keskus Läntinen",
        "33210": "Itä-Amuri-Tammerkoski",
        "33230": "Länsi-Amuri",
        "33240": "Tahmela",
        "33250": "Pispala",
        "33270": "Epilä",
        "33300": "Rahola",
        "33310": "Tesoma",
        "33330": "Myllypuro-Kalkku",
        "33340": "Haukiluoma-Ikuri",
        "33400": "Luoteis-Tampere",
        "33410": "Lentävänniemi",
        "33420": "Lamminpää",
        "33500": "Osmonmäki-Petsamo",
        "33520": "Keskussairaala-alue-Kauppi",
        "33530": "Kissanmaa",
        "33540": "Kaleva",
        "33560": "Takahuhti",
        "33580": "Atala-Linnainmaa",
        "33610": "Olkahinen-Tasanne",
        "33680": "Aitolahti",
        "33700": "Messukylä",
        "33710": "Kaukajärvi",
        "33720": "Hervanta",
        "33730": "Leinola-Vehmainen",
        "33800": "Nekala",
        "33820": "Koivistonkylä",
        "33840": "Peltolammi",
        "33850": "Multisilta",
        "33870": "Vuores",
        "33900": "Härmälä-Rantaperkiö",
        "34240": "Kämmenteisko",
        "34260": "Terälahti",
        "34270": "Velaatta"
    }
    return area_names


# Define the EUREF-FIN (ETRS-TM35FIN) projection
transformer_etrs_tm35fin_to_wgs84 = pyproj.Transformer.from_crs('EPSG:3067', 'EPSG:4326', always_xy=True)


# Define a function to get longitude and latitude
def convert_to_lat_lon(x_coord, y_coord):
    lon, lat = transformer_etrs_tm35fin_to_wgs84.transform(x_coord, y_coord)
    return lat, lon