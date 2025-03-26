import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Cargar el archivo CSV
df = pd.read_csv('hurtos_V1.csv')

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Layout del tablero
app.layout = html.Div([
    html.Div([
        html.H1("Tablero de Hurtos de Luminarias 2022-2025", style={'textAlign': 'center'}),
        
        # Filtro de año
        html.Div([
            html.Label("Seleccione el año:", style={'fontSize': '20px', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in df['AÑO'].unique()],
                value=[df['AÑO'].unique()[0]],
                multi=True,
                clearable=False,
                style={'width': '100%', 'marginBottom': '20px'}
            ),
        ], style={'width': '100%', 'padding': '10px'}),

        # Gráficos
        html.Div([
            dcc.Graph(id='bar-chart'),
            dcc.Graph(id='map', style={'height': '600px'})
        ], style={'width': '100%', 'padding': '10px'}),
    ], style={'paddingBottom': '50px'}),

    # Footer
    html.Div(
        "© 2025 - ESIP SAS ESP - Todos los derechos Reservados- Desarrollado por Alejandra Valderrama",
        style={
            'position': 'fixed',
            'bottom': '10px',
            'right': '20px',
            'color': '#555',
            'fontSize': '14px',
            'backgroundColor': 'rgba(255, 255, 255, 0.7)',
            'padding': '5px 10px',
            'borderRadius': '5px'
        }
    )
])

# Callback modificado para el mapa
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('map', 'figure')],
    [Input('year-dropdown', 'value')]
)
def update_graphs(selected_years):
    filtered_df = df[df['AÑO'].isin(selected_years)]
    
    # Gráfico de barras (sin cambios)
    bar_fig = px.bar(
        filtered_df,
        x='Mes',
        y='Farola',
        title='Hurtos de Luminarias por Mes',
        color='AÑO',
        barmode='group'
    )
    
    # Mapa - Correcciones importantes:
    map_fig = go.Figure()
    
    # Verifica que las columnas de coordenadas existan
    if 'Latitud' in filtered_df.columns and 'Longitud' in filtered_df.columns:
        for year in selected_years:
            year_df = filtered_df[filtered_df['AÑO'] == year]
            
            # Filtra valores NaN en coordenadas
            valid_coords = year_df.dropna(subset=['Latitud', 'Longitud'])
            
            map_fig.add_trace(go.Scattermapbox(
                lat=valid_coords['Latitud'],
                lon=valid_coords['Longitud'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=px.colors.qualitative.Plotly[selected_years.index(year) % len(px.colors.qualitative.Plotly)]
                ),
                name=str(year),
                hovertext=valid_coords['Farola']
            ))
    
    # Configuración mejorada del mapa
    map_fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(
                lat=filtered_df['Latitud'].mean() if not filtered_df['Latitud'].isnull().all() else 4.6097,
                lon=filtered_df['Longitud'].mean() if not filtered_df['Longitud'].isnull().all() else -74.0817
            ),
            zoom=10
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=600
    )
    
    return bar_fig, map_fig

server = app.server

if __name__ == '__main__':
    app.run_server(debug=False)