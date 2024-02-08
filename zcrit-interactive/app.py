from dash import Dash, dcc, html, Input, Output, callback, no_update
import plotly.express as px
import plotly.graph_objects as plygo
import json
import pandas as pd
import sys
import os
import glob
import io
from base64 import b64encode

import numpy as np 

def find_closest(value, array):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def extract_parameters(hoverData, tau_array, alpha_array, Z_array):
    if hoverData and 'points' in hoverData:
        point = hoverData['points'][0]

        if point.get('curveNumber') in [1, 2]:  # cuverNumber is the order of each plot is plotted. Zcrit is 0, Collapse case is 1, No-Collapse case is 2.
            log_tau = point.get('x')
            log_alpha = point.get('y')
            Z = point.get('z')

            # Convert and find the closest predefined values (10^(log(-1.5)) doesn't give exact 0.03.)
            tau = find_closest(10 ** float(log_tau), tau_array) if log_tau is not None else None
            alpha = find_closest(10 ** float(log_alpha), alpha_array) if log_alpha is not None else None
            Z = find_closest(Z, Z_array) if Z is not None else None

            return tau, alpha, Z
    return None, None, None




def extract_tsg(filename):
    tsg = filename.split('-sg')[1].split('.')[0]
    return float(tsg)

#def get_data_for_run(tau,alpha,Z):
#    return data_files.get((tau,alpha,Z))

#def get_filename(tau,alpha,Z,tsg):
#    file_label = alpha_mapping.get(alpha,"default_value")
#    return f"tau{tau}-Z{Z}-{file_label}-sg{tsg}.csv"

def get_yaxis_label(plot_type):
    if plot_type == 'dmax':
        return 'ρ<sub>p,max</sub> / ρ<sub>g0</sub>'
    elif plot_type == 'hp':
        return 'H<sub>p</sub>/H'
    elif plot_type == 'eps':
        return '<ϵ>'


def get_yaxis_range(plot_type):
    if plot_type == 'dmax':
        return [1.0,1.e+5]
    elif plot_type == 'hp':
        return [8.e-3,0.2]
    elif plot_type == 'eps':
        return [0.2,100.0]

def get_yaxis_tick(plot_type):
    if plot_type == 'dmax':
        tickvals = [1.0,10.0,1.e+2,1.e+3,1.e+4,1.e+5]
        ticktext = [f'10<sup>{0}</sup>',f'10<sup>{1}</sup>',f'10<sup>{2}</sup>',f'10<sup>{3}</sup>',f'10<sup>{4}</sup>',f'10<sup>{5}</sup>']
    elif plot_type == 'hp':
        tickvals = [0.01, 0.015, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15,0.2]
        ticktext = ['0.01', '0.015','0.02', '0.03','0.05', '0.07', '0.1', '0.15','0.2']
    elif plot_type == 'eps':
        tickvals = [0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
        ticktext = tickvals
        #ticktext = [0.2, 0.5, f'10<sup>{1}</sup>', 20.0, 50.0, f'10<sup>{2}</sup>']
    return tickvals, ticktext


# My naming convension is tau$tau-Z$Z-1 for alpha=1.e-4, and ...-2 for alpha=1.e-3.5, and so on.

alpha_mapping = {
    10**(-4): "1",
    0.000316: "2",
    10**(-3): "3"
}

#Step 0. Read collapse_data that has tau,Z,alpha combination of each run

ds = pd.read_csv('./collapse_data.txt', delimiter="\t")

alphas, taus, Zs = np.asarray(ds['alpha']), np.asarray(ds['tau']), np.asarray(ds['Z'])

alpha_Y, tau_Y, Z_Y = alphas[(ds['collapse']=='Y')&(alphas>1e-20)], taus[(ds['collapse']=='Y')&(alphas>1e-20)], Zs[(ds['collapse']=='Y')&(alphas>1e-20)]
alpha_N, tau_N, Z_N = alphas[(ds['collapse']=='N')&(alphas>1e-20)], taus[(ds['collapse']=='N')&(alphas>1e-20)], Zs[(ds['collapse']=='N')&(alphas>1e-20)]

#Step 1. Combine Arrays into Tuples and pre-load data

parameters = list(zip(taus,alphas,Zs))

#Preload data
file_names = {}
data_files = {}


for tau,alpha, Z in parameters:
    file_label = alpha_mapping.get(alpha, "default_label")
    pattern = f"tau{tau}-Z{Z}-{file_label}-*sg*.csv"
    file_names[(tau,alpha,Z)] = glob.glob(pattern)[0]
    data_files[(tau,alpha,Z)] = pd.read_csv(f'./{glob.glob(pattern)[0]}',delimiter=' ')

#Step 2. Now, plotting.

#First, plot the Z_Crit

alpha_axis = np.logspace(-4, -3, 128)[::-1]; tau_axis = np.logspace(-2, np.log10(0.3), 128)
Z_crit = 10**( 0.15 * np.log10(alpha_axis[:, None])**2 - 0.24 * np.log10(tau_axis) * np.log10(alpha_axis[:, None])
              - 1.48 * np.log10(tau_axis) + 1.18 * np.log10(alpha_axis[:, None]) )

layout = plygo.Layout(width=1200, height=800, autosize=False, showlegend=False, font = {'size': 18},
                     scene=dict(aspectmode='cube', xaxis=dict(title='log(τ<sub>s</sub>)', titlefont=dict(size=24)),
                                yaxis=dict(title='log(α<sub>D</sub>)', titlefont=dict(size=24)), zaxis=dict(title='Z', titlefont=dict(size=28)),
                                camera=dict(up=dict(x=0,y=0,z=1), center=dict(x=0,y=0,z=-0.15), eye=dict(x=0.8, y=-1.6, z=0.8)))
                     )

vis_data = [plygo.Surface(y = np.log10(alpha_axis), x = np.log10(tau_axis), z = Z_crit, colorscale='viridis', opacity=0.65,
                          name='Z<sub>crit</sub>(τ<sub>s</sub>, α)', showscale=False, showlegend=False,
                          hovertemplate='<b>Z<sub>crit</sub>(τ<sub>s</sub>, α)</b>'+'<br><b>log(τ<sub>s</sub>)</b>: %{x:.3e}'+'<br><b>log(α<sub>D</sub>)</b>: %{y:.3e}'+'<br><b>Z<sub>crit</sub></b>: %{z:.3e}'+'<extra></extra>'),
            plygo.Scatter3d(x=np.log10(tau_Y), y=np.log10(alpha_Y), z=Z_Y, mode='markers', marker = dict(size = 10),
                            name='Collapse', showlegend=True,
                            hovertemplate='<b>Collapse</b>'+'<br><b>log(τ<sub>s</sub>)</b>: %{x:.2e}'+'<br><b>log(α<sub>D</sub>)</b>: %{y:.2e}'+'<br><b>Z</b>: %{z:.2e}'+'<extra></extra>'),
            plygo.Scatter3d(x=np.log10(tau_N), y=np.log10(alpha_N), z=Z_N, mode='markers', marker = dict(size = 10), marker_symbol=['diamond-open',]*Z_N.size,
                            name='No Collapse', showlegend=True,
                            hovertemplate='<b>No Collapse</b>'+'<br><b>log(τ<sub>s</sub>)</b>: %{x:.2e}'+'<br><b>log(α<sub>D</sub>)</b>: %{y:.2e}'+'<br><b>Z</b>: %{z:.2e}'+'<extra></extra>'), ]

surface_fig = plygo.Figure(layout = layout, data = vis_data)
surface_fig.update_layout(margin = dict(l = 0, r = 0, b = 0, t = 0), hoverlabel=dict(font_size=17,), showlegend=True, legend=dict(y=0.5))



#Second, initialize the Dash app

app = Dash(__name__)

buffer = io.StringIO()

surface_fig.write_html(buffer)

html_bytes = buffer.getvalue().encode()
encoded = b64encode(html_bytes).decode()

#Third, Define the layout (one of the two parts that consist of Dash apps. It describes what the app looks like)
#More info: https://dash.plotly.com/layout

app.layout = html.Div([
        html.H1('Conditions for Planetesimal Formation',
                style = {'textAlign':'center'}),

        html.Div("(Hover on points/squares to display related info)",
           style ={
               'textAlign': 'center',
               'fontSize': '20px'
                }
               ),

	    
    html.Div(
    html.A("Link to the paper", href='https://arxiv.org/abs/2312.12508', target="_blank")
    ),
    
    html.Div(
    html.A("Link to Jeonghoon's personal webpage", href='https://jhlim.weebly.com/',target='_blank')
    ),

    dcc.Graph(id='surface-plot',
             figure=surface_fig), #Placeholder for Z_crit(tau,alpha)

    #include Dropdown in Layout
    html.Div([
    dcc.Dropdown(
    id='plot-type-dropdown',
    options=[
        {'label': 'dmax (max.density of particle) vs time', 'value': 'dmax'},
        {'label': 'hp   (scale height of particle) vs time', 'value': 'hp'},
        {'label': 'eps (mid-plane density ratio)  vs time', 'value': 'eps'},
        {'label': 'Final Snapshot', 'value': 'final_snapshot'}
    ],
    value='dmax' #Default value
    )
    ]),

    html.Div([
        dcc.Graph(id='time-series-plot') #Placeholder for time evolution plots
        #html.Img(id='final_snapshot',style={'display': 'none'})
    ]),

    html.Div([
    html.A(
        html.Button("Download as HTML **the surface plot only **"),
        id="download",
        href="data:text/html;base64," + encoded,
        download="tau-Z-alpha.html"
    )
    ])

])


#Fourth, Define the callback functions that are automatically called by Dash whenever an input component's property change
#More info: https://dash.plotly.com/basic-callbacks

def get_file_for_run(tau,alpha,Z):
    file = data_files.get((tau,alpha,Z),[])
    return file[0] if file else None

@callback(
    Output('time-series-plot','figure'),
    Input(component_id='surface-plot',component_property='hoverData'),
    Input(component_id='plot-type-dropdown',component_property='value')
)
def update_graph(hoverData,plot_type):

    tau, alpha, Z = extract_parameters(hoverData,taus,alphas,Zs)

    if tau is not None and Z is not None and alpha is not None:
        fname = file_names[(tau,alpha,Z)]

        #read csv file
        df = data_files.get((tau,alpha,Z))

        #Plotting
        sz=18 #font size

        #automatically choose for dmax, hp, or eps

        if plot_type != 'final_snapshot':
            y_label = get_yaxis_label(plot_type)
            y_range = get_yaxis_range(plot_type)
            y_tickvals, y_ticktext = get_yaxis_tick(plot_type)

            fig = px.line(df, x='time', y=plot_type)

        # customize texts in hover box
            fig.update_traces(hovertemplate='(t-t<sub>par</sub>)Ω: %{x:.3e}'+f'<br>{y_label}: %{{y:.3e}}<extra></extra>')
            fig.update_layout(hoverlabel=dict(font_size=sz-2))

            fig.update_layout(yaxis = dict(
                                   tickmode = 'array',
                                   tickvals = y_tickvals,
                                   ticktext = y_ticktext))

            if plot_type == 'dmax':
                hill=180.0

                fig.add_hline(y=hill, line_width=2, line_dash="dot", line_color="black") #Hill density

                fig.add_annotation(
                x=0.15, y=np.log10(hill),
                xref="paper",yref="y",
                text="Hill density",
                showarrow=True, arrowhead=2,
                font=dict(size=sz,color="black")
                )

            fig.update_layout(font=dict(size=sz-2, color="black"))
            fig.update_layout(xaxis_title="(t-t<sub>par</sub>)Ω")
            fig.update_layout(yaxis_type='log', yaxis_range=np.log10(y_range),yaxis_title=y_label,yaxis = dict(showexponent='all', exponentformat='power'))

            if fname.split('-')[3].split('.')[0] != 'nosg':
                tsg = extract_tsg(fname)      #Extract tsg from the filename

            #Create a time series plot based on the selected plot type

                fig.add_vline(x=tsg, line_width=2, line_dash="dash", line_color="red")

            #annotate for the vertical line (tsg).
                fig.add_annotation(
                x=tsg,
                y=0.95,  # Adjust this according to your y-axis scale
                text="t<sub>sg</sub>",  # The label for the vertical line
                showarrow=True, arrowhead=2,
                yref="paper",  # Using 'paper' refers to the entire height of the plot
                xanchor="left",  # Position the text to the left of the line
                font=dict(size=sz,color='red')
                )
                fig.update_layout(title=f"{plot_type} vs time for τ<sub>s</sub>={tau}, Z={Z}, α<sub>D</sub>={alpha:.2e}")
            else:
                fig.update_layout(title=f"{plot_type} vs time for τ<sub>s</sub>={tau}, Z={Z}, α<sub>D</sub>={alpha:.2e} (NoSG)")

            return fig

        elif plot_type == 'final_snapshot':
            temp=fname.split('-')

            img_name = temp[0]+'-'+temp[1]+'-'+temp[2]+'-'+temp[3].split('.')[0]

            img_path = app.get_asset_url(f"{img_name}.png")

            #print(img_path)

            return {
            'data': [],
            'layout': {
            'images': [{'source': img_path,
                            'xref': "paper", 'yref': "paper",
                            'x': 0.5, 'y': 0.5,
                            'sizex': 1.0, 'sizey': 1.0,
                            'xanchor': "center", 'yanchor': "middle"
                            }],
            'xaxis': {'visible': False},
            'yaxis': {'visible': False}
            }
            }

    else:
        return no_update #not updating when hovering over the surface (not points)

#def update_snapshot(plot_type,hoverData):
#    if plot_type == 'final snapshot': #triggered by the Dropdown
#        tau, alpha, Z = extract_parameters(hoverData,taus,alphas,Zs)
#        if tau is not None and Z is not None and alpha is not None:
#            image_name = filename([tau,alpha,Z])
#            return html.Img(src=app.get_asset_url(f"{image_name}.png"))

# Run the app
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=8080)
