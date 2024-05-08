import dash
from dash import html, dcc, Input, Output
import folium
from folium.plugins import HeatMap
import plotly.graph_objs as go
from data_handler import get_coordinates_data, get_population_data, get_population_density_data, get_income_data, get_education_data, get_activity_data, get_population_counts_and_average_ages, get_population_counts_and_surface_areas, get_coordinates_and_postal_codes, get_median_incomes, get_area_names, get_activity_percentages, convert_to_lat_lon

# Read JSON data using the data_handler module
coordinates_data = get_coordinates_data()
population_data = get_population_data()
populationDensity_data = get_population_density_data()
income_data = get_income_data()
education_data = get_education_data()
activity_data = get_activity_data()


# Get data using the data_handler module
coordinates, postal_codes = get_coordinates_and_postal_codes(coordinates_data)
median_incomes = get_median_incomes(income_data)
population_count, average_age = get_population_counts_and_average_ages(population_data)
population_counts, surface_areas_km2 = get_population_counts_and_surface_areas(populationDensity_data)
activityPercentages_by_area = get_activity_percentages(activity_data, postal_codes)
area_names = get_area_names()


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
        
        # Get latitude and longitude from coordinates using the function from data_handler.py
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
    
    # Define layout for education level distribution pie chart
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
    
    # Define layout for activity distribution pie chart
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
    
    # Add general information layer
    if layer == 'general':
        for postal_code in postal_codes:
            postal_code_str = str(postal_code)
            area_name = area_names.get(postal_code_str)
            if area_name:
                coordinates_index = postal_codes[postal_code]
                x_coordinate = coordinates[coordinates_index * 2]
                y_coordinate = coordinates[coordinates_index * 2 + 1]
                
                # Get latitude and longitude
                latitude, longitude = convert_to_lat_lon(x_coordinate, y_coordinate)

                # Calculate marker size based on population count
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
                
    # Add heatmap layer
    elif layer == 'heatmap':
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