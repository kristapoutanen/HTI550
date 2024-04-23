import json
import dash
from dash import html, dcc, Input, Output
import folium
import pyproj
import os
import plotly.graph_objs as go

# Get the current directory
current_dir = os.path.dirname(__file__)

# Paths to the JSON files
coordinate_file = os.path.join(current_dir, 'koordinaatit.json')
population_file = os.path.join(current_dir, 'asukasmaara.json')
income_file = os.path.join(current_dir, 'tulot.json')
education_file = os.path.join(current_dir, 'koulutus.json')

# Read the JSON data for coordinates
with open(coordinate_file, 'r', encoding='utf-8') as file:
    coordinates_data = json.load(file)

# Read the JSON data for population counts
with open(population_file, 'r', encoding='utf-8') as file:
    population_data = json.load(file)

# Read the JSON data for median incomes
with open(income_file, 'r', encoding='utf-8') as file:
    incomes_data = json.load(file)

# Read the JSON data for education levels
with open(education_file, 'r', encoding='utf-8') as file:
    education_data = json.load(file)

# Get coordinates from the JSON data
coordinates = coordinates_data['dataset']['value']

# Get median incomes from the JSON data
median_incomes = incomes_data['dataset']['value']

# Get population counts from the JSON data
population = population_data['dataset']['value']

# A dict for the area names based on x-coordinates
area_names = {
    "328970": "Tampere Keskus",
    "328335": "Lapinniemi-Käpylä",
    "327187": "Tampere Keskus Läntinen",
    "327246": "Itä-Amuri-Tammerkoski",
    "326093": "Länsi-Amuri",
    "324822": "Tahmela",
    "325414": "Pispala",
    "323105": "Epilä",
    "320377": "Rahola",
    "320380": "Tesoma",
    "317735": "Myllypuro-Kalkku",
    "319181": "Haukiluoma-Ikuri",
    "322822": "Luoteis-Tampere",
    "326022": "Lentävänniemi",
    "321047": "Lamminpää",
    "329709": "Osmonmäki-Petsamo",
    "330614": "Keskussairaala-alue-Kauppi",
    "331115": "Kissanmaa",
    "329790": "Kaleva",
    "332998": "Takahuhti",
    "335921": "Atala-Linnainmaa",
    "337060": "Olkahinen-Tasanne",
    "338795": "Aitolahti",
    "331601": "Messukylä",
    "334637": "Kaukajärvi",
    "332532": "Hervanta",
    "335522": "Leinola-Vehmainen",
    "329553": "Nekala",
    "330035": "Koivistonkylä",
    "327741": "Peltolammi",
    "325991": "Multisilta",
    "330830": "Vuores",
    "326746": "Härmälä-Rantaperkiö",
    "333797": "Kämmenteisko",
    "335702": "Terälahti",
    "342092": "Velaatta"
}

# Define the EUREF-FIN (ETRS-TM35FIN) projection
transformer_etrs_tm35fin_to_wgs84 = pyproj.Transformer.from_crs('EPSG:3067', 'EPSG:4326', always_xy=True)

# Define a function to convert x and y coordinates to latitude and longitude
def convert_to_lat_lon(x_coord, y_coord):
    lon, lat = transformer_etrs_tm35fin_to_wgs84.transform(x_coord, y_coord)
    return lat, lon

# Create a folium Map centered around Tampere
m = folium.Map(location=(61.4978, 23.7610), zoom_start=12)

# Get latitude and longitude from coordinates
for i in range(0, len(coordinates), 2):
    x_coord = coordinates[i]
    y_coord = coordinates[i+1]
    latitude, longitude = convert_to_lat_lon(x_coord, y_coord)
    
    # Get population for the current area
    pop = population[i // 2]
    
    # Define marker size based on population
    marker_radius = pop / 500
    
    # Get area name based on x-coordinate
    area_name = area_names.get(str(x_coord))
    
    # Add a marker with information popup
    folium.CircleMarker([latitude, longitude], radius=marker_radius, color='orange', fill=True, fill_opacity=0.4, popup=f"<b>{area_name}</b><br>Population: {pop}").add_to(m)

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
    
    # Main content section
    html.Div([
        
        # Folium Map section
        html.Div([
            html.Iframe(id='folium-map', srcDoc=m_html, width='100%', height='500px')
        ], style={'width': '100%', 'display': 'inline-block'}),
    ]),
    
    # Charts section
    html.Div([
        # Bar chart section
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
                        xaxis={'title': 'Postal Code Area'},
                        yaxis={'title': 'Median Income'},
                        plot_bgcolor='#f2f2f2',
                        paper_bgcolor='#f2f2f2',
                        font=dict(family='Roboto', size=12, color='#444342')
                    )
                }
            )
        ], style={'width': '70%', 'margin-top': '15px', 'display': 'inline-block'}),
        
        # Pie chart section
        html.Div([
            dcc.Graph(
                id='education-pie-chart',
                figure={
                    'data': [],
                    'layout': go.Layout(
                        title='Education Level Distribution',
                        plot_bgcolor='#f2f2f2',
                        paper_bgcolor='#f2f2f2',
                        font=dict(family='Roboto', size=26, color='#444342'),
                    )
                }
            )
        ], style={'width': '30%', 'margin-top': '15px', 'display': 'inline-block'})
    ])
])


# Define callback to update education pie chart based on the data point selected on the bar chart
@app.callback(
    Output('education-pie-chart', 'figure'),
    [Input('income-bar-chart', 'clickData')]
)
def update_pie_chart(click_data):
    
    if click_data is None:
        # Set default postal area for the education pie chart as Tampere Keskus
        selected_area = "328970"
    
    else:
        # Extract selected postal area from click data
        selected_area_name = click_data['points'][0]['x']
        
        # Get the area code from the area name
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



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)