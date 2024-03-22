import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import random
from dateutil.relativedelta import relativedelta

# Create the random time series data
df = pd.DataFrame({
    'Date': pd.date_range(start='1960-01-01', end='2024-01-01', freq='M'),
    'Value': [(np.sin(i * 0.2) * 5) + random.randint(-8,8) for i in range(len(pd.date_range(start='1960-01-01', end='2024-01-01', freq='M')))]
})

# Read in provided data
forecast_df = pd.read_excel('forecast_data.xlsx')
forecast_df = forecast_df.rename(columns={'date': 'Date'})

# Change the last value in random data to match the provided data
df.loc[df.index[-1], 'Value'] = forecast_df.loc[forecast_df.index[0],'UB_50']

# Initialize the dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Hayden Church Code Assessment", style={'textAlign':'center'}),
    dcc.Graph(id='time-series-plot', 
        style={'width': '1200px', 
        'height': '800px',
        'margin':'auto',
        'textAlign': 'center'})
])

@app.callback(
    Output('time-series-plot', 'figure'),
    [Input('time-series-plot', 'selectedData')]
)
def update_plot(selectedData):
    # Create the figure
    fig = px.line(df, x='Date', y='Value', title='US Inflation', color_discrete_sequence=['black'], markers=True)


    # Makes sure the fill does not go all the way to the x- axis
    # Rather the fill stays between our UB and LB
    error_50 = dict(
        type="scatter",
        x=forecast_df['Date'].tolist() + list(reversed(forecast_df['Date'])),
        y=list(forecast_df["UB_50"]) + list(reversed(forecast_df["LB_50"])),
        fill="tozeroy",
        fillcolor="rgba(226, 87, 78, 1)",
        line=dict(color="rgba(255,255,255,0)"), 
        name="50% CI",
    )

    error_75 = dict(
        type="scatter",
        x=forecast_df['Date'].tolist() + list(reversed(forecast_df['Date'])),
        y=list(forecast_df["UB_75"]) + list(reversed(forecast_df["LB_75"])),
        fill="tozeroy",
        fillcolor="rgba(0, 0, 255, 1)",
        line=dict(color="rgba(255,255,255,0)"),
        name="75% CI",
    )

    error_95 = dict(
        type="scatter",
        x=forecast_df['Date'].tolist() + list(reversed(forecast_df['Date'])),
        y=list(forecast_df["UB_95"]) + list(reversed(forecast_df["LB_95"])),
        fill="tozeroy",
        fillcolor="rgba(0, 100, 78, 1)",
        line=dict(color="rgba(255,255,255,0)"),
        name="95% CI",
    )


    # Center the title
    fig.update_layout(title=dict(text="US Inflation", x=0.5))

    # Add error plots to the figure
    fig.add_traces([error_95])
    fig.add_traces([error_75])
    fig.add_traces([error_50])




    data_start = df['Date'].iloc[0]
    data_end = df['Date'].iloc[-1] + relativedelta(months=18)
    delta_t = data_end - data_start

    # Buttons and slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                dict(count=delta_t.days, label="All", step="day",stepmode="backward")
            ])
        ),
        rangeslider = dict(
            visible=True,
            autorange = False,
            range = [data_start, data_end]
        )

    )

    # Calculate the start and end dates for the range slider
    range_start = df['Date'].iloc[-16]
    range_end = df['Date'].iloc[-1] + relativedelta(months=18)
    # Set the range of the range slider
    fig.update_layout(
        xaxis=dict(
            range=[range_start, range_end]
        )
    )
    
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)

