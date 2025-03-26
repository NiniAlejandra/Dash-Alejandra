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
    html.H1("Tablero de Hurtos de Luminarias", style={'textAlign': 'center'}),

    # Filtro de año
    html.Div([
        html.Label("Seleccione el año:", style={'fontSize': '20px', 'marginBottom': '10px'}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in df['AÑO'].unique()],
            value=[df['AÑO'].unique()[0]],  # Valor inicial
            multi=True,  # Permite selección múltiple
            clearable=False,
            style={'width': '100%', 'marginBottom': '20px'}
        ),
    ], style={'width': '100%', 'padding': '10px'}),

    # Gráficos
    html.Div([
        dcc.Graph(id='bar-chart'),
        dcc.Graph(id='map', style={'height': '600px'})  # Aumentamos la altura del mapa
    ], style={'width': '100%', 'padding': '10px'})
])

# Callbacks para actualizar los gráficos
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('map', 'figure')],
    [Input('year-dropdown', 'value')]
)
def update_graphs(selected_years):
    # Filtrar el DataFrame por los años seleccionados
    filtered_df = df[df['AÑO'].isin(selected_years)]

    # Gráfico de barras (hurtos por mes)
    bar_fig = px.bar(
        filtered_df,
        x='Mes',
        y='Farola',
        title=f'Hurtos de Luminarias por Mes',
        labels={'Farola': 'Número de Hurtos', 'Mes': 'Mes del Año'},
        color='AÑO',  # Color por año
        barmode='group',  # Agrupa las barras por año
        color_discrete_sequence=px.colors.qualitative.Plotly  # Colores discretos
    )
    # Quitar la leyenda del gráfico de barras
    bar_fig.update_layout(showlegend=True, legend_title_text='Año')

    # Mapa de hurtos usando go.Scattermapbox
    map_fig = go.Figure()

    # Añadir un trace por cada año seleccionado
    for year in selected_years:
        year_df = filtered_df[filtered_df['AÑO'] == year]
        map_fig.add_trace(go.Scattermapbox(
            lat=year_df['Latitud'],
            lon=year_df['Longitud'],
            mode='markers',
            marker=dict(size=10, color=px.colors.qualitative.Plotly[selected_years.index(year)]),
            name=str(year),  # Nombre de la leyenda
            hovertext=year_df['Farola'],  # Texto al pasar el mouse
            hoverinfo='text'
        ))

    # Configuración del mapa
    map_fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=filtered_df['Latitud'].mean(), lon=filtered_df['Longitud'].mean()),
            zoom=12
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        legend_title_text='Año',
        height=600  # Altura del mapa
    )

    return bar_fig, map_fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)