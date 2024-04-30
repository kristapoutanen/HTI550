import dash
from dash import html, dcc, Input, Output
import folium
from folium.plugins import HeatMap
import json
import os
import plotly.graph_objs as go
import pyproj

# Get the current directory
current_dir = os.path.dirname(__file__)

# Paths to the JSON files
coordinate_file = os.path.join(current_dir, 'koordinaatit.json')
population_file = os.path.join(current_dir, 'populaatio.json')
populationDensity_file = os.path.join(current_dir, 'asukastiheys.json')
income_file = os.path.join(current_dir, 'tulot.json')
education_file = os.path.join(current_dir, 'koulutus.json')
activity_file = os.path.join(current_dir, 'toiminta.json')

# Read the JSON data for coordinate data
with open(coordinate_file, 'r', encoding='utf-8') as file:
    coordinates_data = json.load(file)

# Read the JSON data for population data
with open(population_file, 'r', encoding='utf-8') as file:
    population_data = json.load(file)

# Read the JSON data for population density data
with open(populationDensity_file, 'r', encoding='utf-8') as file:
    populationDensity_data = json.load(file)

# Read the JSON data for income data
with open(income_file, 'r', encoding='utf-8') as file:
    income_data = json.load(file)

# Read the JSON data for education data
with open(education_file, 'r', encoding='utf-8') as file:
    education_data = json.load(file)

# Read the JSON data for activity data
with open(activity_file, 'r', encoding='utf-8') as file:
    activity_data = json.load(file)

# Get coordinates and postal codes from the JSON data
coordinates = coordinates_data['dataset']['value']
postal_codes = coordinates_data['dataset']['dimension']['Postinumeroalue']['category']['index']

# Get median incomes from the JSON data
median_incomes = income_data['dataset']['value']

# Get population counts and average ages from the JSON data
population_count = population_data['dataset']['value'][::4]
average_age = population_data['dataset']['value'][3::4]

# Get population counts and surface areas from the JSON data
surface_areas_m2 = populationDensity_data['dataset']['value'][::2]
population_counts = populationDensity_data['dataset']['value'][1::2]

# Convert surface areas from square meters to square kilometers
surface_areas_km2 = [area / 1000000 for area in surface_areas_m2]

# Convert population counts from decimals to integers
population_counts = [int(count) for count in population_counts]

# Get population counts for different activity groups from the JSON data
postal_codes = activity_data['dataset']['dimension']['Postinumeroalue']['category']['index']
population_count = activity_data['dataset']['value'][::7]

employed_counts = activity_data['dataset']['value'][1::7]
unemployed_counts = activity_data['dataset']['value'][2::7]
children_counts = activity_data['dataset']['value'][3::7]
student_counts = activity_data['dataset']['value'][4::7]
retired_counts = activity_data['dataset']['value'][5::7]
other_counts = activity_data['dataset']['value'][6::7]

# Create a dict for activity percentages for each postal code area
activityPercentages_by_area = {}

# Calculate percentages for different activity groups for each postal code area
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

# Create a dict for postal area names and postal area codes
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

# Define the EUREF-FIN (ETRS-TM35FIN) projection
transformer_etrs_tm35fin_to_wgs84 = pyproj.Transformer.from_crs('EPSG:3067', 'EPSG:4326', always_xy=True)

# Define a function to convert x and y coordinates to latitude and longitude
def convert_to_lat_lon(x_coord, y_coord):
    lon, lat = transformer_etrs_tm35fin_to_wgs84.transform(x_coord, y_coord)
    return lat, lon

# Create a folium Map centered around Tampere
m = folium.Map(location=(61.4978, 23.7610), zoom_start=12)

# Add general for postal code areas
for postal_code in postal_codes:
    postal_code_str = str(postal_code)
    area_name = area_names.get(postal_code_str)
    if area_name:
        coordinates_index = postal_codes[postal_code]
        x_coordinate = coordinates[coordinates_index * 2]
        y_coordinate = coordinates[coordinates_index * 2 + 1]
        
        # Get latitude and longitude from coordinates
        latitude, longitude = convert_to_lat_lon(x_coordinate, y_coordinate)

        # Set marker size based on population count
        marker_size = population_count[coordinates_index] / 500
        
        # Set marker color
        marker_color = 'orange'
        
        # Add a marker with information popup
        popup_text = f"<b>{area_name}</b><div style='display:flex; flex-direction: row;'><div style='margin-right:10px;'>Population:</div><div>{population_count[coordinates_index]}</div></div><div style='display:flex; flex-direction: row;'><div style='margin-right:10px;'>Average age:</div><div>{average_age[coordinates_index]}</div></div>"
        
        folium.CircleMarker(
            [latitude, longitude],
            radius=marker_size, 
            color=marker_color, 
            fill=True, 
            fill_opacity=0.4, 
            popup=popup_text,
            max_width=300
        ).add_to(m)

# Serialize the Folium map to HTML
m_html = m._repr_html_()

# Create Dash app
app = dash.Dash(__name__)

# Define the layout of the Dash app
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1('Tampere Data Dashboard', style={'font-family': 'Roboto', 'color': '#444342', 'font-size': '24px', 'margin-bottom': '5px'}),
    ], style={'background-color': '#DDDDDD', 'padding': '5px', 'text-align': 'left'}),
    
    # Dropdown for map layers
    dcc.Dropdown(
        id='layer-dropdown',
        options=[
            {'label': 'General Information', 'value': 'general'},
            {'label': 'Population Density', 'value': 'heatmap'}
        ],
        value='general',
        clearable=False
    ),

    # Main content section
    html.Div([
        # Folium Map section
        html.Div([
            html.Iframe(id='folium-map', srcDoc=m_html, width='100%', height='500px')
        ], style={'width': '100%', 'display': 'inline-block'}),
    ]),
    
    # Charts section
    html.Div([
        # Pie chart section
        html.Div([
            # Education pie chart
            html.Div([
                dcc.Graph(
                    id='education-pie-chart',
                    figure={
                        'data': [],
                        'layout': go.Layout(
                            title='Education Level Distribution',
                            plot_bgcolor='#f2f2f2',
                            paper_bgcolor='#f2f2f2',
                            font=dict(family='Roboto', size=18, color='#444342'),
                        )
                    }
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            # Activity pie chart
            html.Div([
                dcc.Graph(
                    id='activity-pie-chart',
                    figure={
                        'data': [],
                        'layout': go.Layout(
                            title='Activity Distribution',
                            plot_bgcolor='#f2f2f2',
                            paper_bgcolor='#f2f2f2',
                            font=dict(family='Roboto', size=18, color='#444342'),
                        )
                    }
                )
            ], style={'width': '48%', 'display': 'inline-block'})
        ]),
        
        # Bar chart section
        html.Div([
            html.Div([
                dcc.Graph(
                    id='income-bar-chart',
                    figure={
                        'data': [
                            go.Bar(
                                x=list(area_names.values()),
                                y=median_incomes,
                                marker_color='orange',
                            )
                        ],
                        'layout': go.Layout(
                            title='Median Incomes by Postal Code Areas',
                            xaxis={'title': ''},
                            yaxis={'title': 'Median Income'},
                            plot_bgcolor='#f2f2f2',
                            paper_bgcolor='#f2f2f2',
                            font=dict(family='Roboto', size=12, color='#444342')
                        )
                    }
                )
            ], style={'width': '100%', 'display': 'inline-block'})
        ])
    ])
])

# Define callback to update education pie chart based on the data point selected on the bar chart
@app.callback(
    Output('education-pie-chart', 'figure'),
    [Input('income-bar-chart', 'clickData')]
)
def update_education_pie_chart(click_data):
    if click_data is None:
        # Set default postal area for the education pie chart as 33100 Tampere Keskus
        selected_area = "33100"
    
    else:
        # Extract selected postal area from click data
        selected_area_name = click_data['points'][0]['x']
        
        # Get the postal area code from the postal code area name
        selected_area = next((code for code, name in area_names.items() if name == selected_area_name), None)
    
    # Get education level data for the selected area
    education_levels = education_data.get(selected_area, {})
    
    # Create pie chart trace for education level distribution
    trace_pie = go.Pie(
        labels=list(education_levels.keys()),
        values=list(education_levels.values()),
        hole=0.3,
        marker_colors=['#FFD700', '#32CD32', '#FFA500', '#45b3e0', '#FF69B4'],
        textinfo='percent',
        hoverinfo='label+percent'
    )
    
    # Define layout for pie chart
    layout_pie = go.Layout(
        title=f'Education Level Distribution in {area_names.get(selected_area, "Tampere Keskus")}',
        plot_bgcolor='#f2f2f2',
        paper_bgcolor='#f2f2f2',
        font=dict(family='Roboto', size=12, color='#444342')
    )
    
    # Return the updated pie chart
    return {'data': [trace_pie], 'layout': layout_pie}


# Define callback to update activity pie chart based on the data point selected on the bar chart
@app.callback(
    Output('activity-pie-chart', 'figure'),
    [Input('income-bar-chart', 'clickData')]
)
def update_activity_pie_chart(click_data):
    if click_data is None:
        # Set default postal area for the activity pie chart as 33100 Tampere Keskus
        selected_area = "33100"
    else:
        # Get selected postal area from click data
        selected_area_name = click_data['points'][0]['x']
        
        # Get the area code from the area name
        selected_area = next((code for code, name in area_names.items() if name == selected_area_name), None)
    
    # Get data for the selected area
    percentages_data = activityPercentages_by_area.get(selected_area, {})
    
    # Create pie chart trace for activity distribution
    trace_pie = go.Pie(
        labels=list(percentages_data.keys()),
        values=list(percentages_data.values()),
        hole=0.3,
        marker_colors=['#FFD700', '#32CD32', '#FFA500', '#45b3e0'],
        textinfo='percent',
        hoverinfo='label+percent'
    )
    
    # Define layout for pie chart
    layout_pie = go.Layout(
        title=f'Activity Distribution in {area_names.get(selected_area, "Tampere Keskus")}',
        plot_bgcolor='#f2f2f2',
        paper_bgcolor='#f2f2f2',
        font=dict(family='Roboto', size=12, color='#444342')
    )
    
    # Return the updated pie chart
    return {'data': [trace_pie], 'layout': layout_pie}


# Define callback to update Folium map based on layer selection
@app.callback(
    Output('folium-map', 'srcDoc'),
    [Input('layer-dropdown', 'value')]
)
def update_folium_map(layer):
    # Create a folium Map centered around Tampere
    m = folium.Map(location=(61.4978, 23.7610), zoom_start=12)

    if layer == 'general':
        # Add general information layer
        for postal_code in postal_codes:
            postal_code_str = str(postal_code)
            area_name = area_names.get(postal_code_str)
            if area_name:
                coordinates_index = postal_codes[postal_code]
                x_coordinate = coordinates[coordinates_index * 2]
                y_coordinate = coordinates[coordinates_index * 2 + 1]
                
                # Get latitude and longitude from coordinates
                latitude, longitude = convert_to_lat_lon(x_coordinate, y_coordinate)

                # Calculate marker size based on population count
                marker_size = population_count[coordinates_index] / 500
                
                # Set marker color to to orange
                marker_color = 'orange'
                
                # Add a marker with information popup
                popup_text = f"<b>{area_name}</b><div style='display:flex; flex-direction: row;'><div style='margin-right:10px;'>Population:</div><div>{population_count[coordinates_index]}</div></div><div style='display:flex; flex-direction: row;'><div style='margin-right:10px;'>Average age:</div><div>{average_age[coordinates_index]}</div></div>"
                
                folium.CircleMarker(
                    [latitude, longitude],
                    radius=marker_size, 
                    color=marker_color, 
                    fill=True, 
                    fill_opacity=0.4, 
                    popup=popup_text,
                    max_width=300
                ).add_to(m)
    
    elif layer == 'heatmap':
        # Add heatmap layer
        populationDensity_heatmapData = [[convert_to_lat_lon(coordinates[i*2], coordinates[i*2+1])[0], 
                      convert_to_lat_lon(coordinates[i*2], coordinates[i*2+1])[1],
                      population_counts[i] / surface_areas_km2[i]] for i in range(len(postal_codes))]
        HeatMap(populationDensity_heatmapData, min_opacity=0.2, max_opacity=0.8, gradient={0.1: 'blue', 0.5: 'yellow', 0.9: 'red'}).add_to(m)

    # Serialize the Folium map to HTML
    m_html = m._repr_html_()
    
    return m_html

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
