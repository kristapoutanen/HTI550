import json
import dash
from dash import html
import folium

# Read the JSON file
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Access the data section
data_rows = data['data']


# Define the coordinates for Tampere, Finland
tampere_location = (61.4978, 23.7610)

# Create a folium Map centered around Tampere
m = folium.Map(location=tampere_location, zoom_start=12)


# Serialize the Folium map to HTML
m_html = m._repr_html_()

# Create Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    # Left section for header, description, and statistics
    html.Div([
        html.H1('Otsikko', style={'margin-bottom': '50px'}),
        html.P('Kuvaus', style={'margin-bottom': '100px'}),
        html.Div([
            html.Div('36 postinumeroaluetta', style={'border-radius': '50%', 'background-color': '#fcba03', 'color': 'white', 'width': '180px', 'height': '180px', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-right': '50px'}),
            html.Div('247564 asukasta', style={'background-color': '#5f9647', 'color': 'white', 'width': '180px', 'height': '180px', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
        ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'})
    ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
    # Map section
    html.Div([
        html.Iframe(id='folium-map', srcDoc=m_html, width='100%', height='600')
    ], style={'width': '70%', 'display': 'inline-block'}),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
