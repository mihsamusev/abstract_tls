import argparse
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd

import output_helper as oh

color_palette = px.colors.qualitative.Plotly
max_colors = len(color_palette)

class DataModel():
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def get_timeseries(self, run, metric, lane_group):
        df = self.data.loc[
            (self.data["run_name"] == run) &
            (self.data["lane_group"] == lane_group)
            ]
        
        t, x = np.array([[0, 0]]).T
        if not df.empty:
            t, x = df[["begin", metric]].to_numpy().T
            print(df)
        return t, x

    def get_data(self, run, metric, lane_group):
        m = 2 * np.random.random()
        s = 2 * np.random.random()
        d = np.random.normal(m, s, (500, ))
        return d

    def get_run_names(self):
        """
        Return list of run names found in the folder
        """
        return self.data["run_name"].unique()

    def get_metrics(self):
        """
        Return list of metrics found in the runs
        """
        non_metric = ["run_name", "begin", "end", "lane", "lane_group"]
        return [c for c in self.data.columns if c not in non_metric]

    def get_lane_groups(self):
        """
        Return list of lane_groups found in the runs
        """
        return self.data["lane_group"].unique()

class DashView():
    def __init__(self, datamodel):
        self.app = dash.Dash(__name__)
        self.datamodel = datamodel
        self.generate_layout()
        self.generate_callbacks()


    def start(self):
        self.app.run_server(debug=True)

    def generate_layout(self):
        """
        Builds main componens of the frontend
        """
        self.app.layout = html.Div([
            html.Label('Select runs to compare'),
            dcc.Dropdown(
                id="input_runs",
                options=[{"label": r, "value": r} for r in self.datamodel.get_run_names()],
                value=self.datamodel.get_run_names(),
                multi=True
            ),
            html.Label('Select comparison metrics'),
            dcc.Dropdown(
                id="input_metrics",
                options=[{"label": r, "value": r} for r in self.datamodel.get_metrics()],
                value=self.datamodel.get_metrics()[:1],
                multi=True
            ),
            html.Label('Select lane groups'),
            dcc.Dropdown(
                id="input_groups",
                options=[{"label": r, "value": r} for r in self.datamodel.get_lane_groups()],
                value=self.datamodel.get_lane_groups()[:1],
                multi=True
            ),
            dcc.Graph(
                id="graph",
                figure=make_subplots(rows=1, cols=2),
                style={'height': '80vh'})

        ], style={'columnCount': 1})


    def generate_callbacks(self):
        self.app.callback(
            dd.Output('graph', 'figure'),
            [dd.Input('input_runs', 'value'),
            dd.Input('input_metrics', 'value'),
            dd.Input('input_groups', 'value')],
        )(self.update_subplot)

    def update_xlabels(self, figure, row_names, column_names):
        """
        Updates x labels depending on the row metrics    
        """
        p = 0
        for metric in row_names:
            for _ in column_names:
                axis_name = "xaxis" if p==0 else f"xaxis{p + 1}"
                p += 1
                figure.update_layout(
                    {axis_name: {"title": "{} {}".format(metric, "*units")}})
    

    def update_subplot(self, runs, metrics, groups):
        """
        Updates the amount adn the contetns of the plots depending on the dropbox
        entries 
        """

        n_metrics = len(metrics)
        n_groups = len(groups)
        n_runs = len(runs)

        if n_metrics * n_groups * n_runs == 0:
            return make_subplots(rows=1, cols=1)
            
        fig = make_subplots(
            rows=n_metrics,
            cols=n_groups,
            subplot_titles=groups)
        
        # generate plots
        for k, run in enumerate(runs):
            color = color_palette[k % max_colors]
            for i, metric in enumerate(metrics):
                for j, group in enumerate(groups):    
                    
                    # x = self.datamodel.get_data(run, metric, user)
                    t, x = self.datamodel.get_timeseries(run, metric, group)

                    fig.append_trace(go.Scatter(**{
                        "x": t,
                        "y": x,
                        "mode": "lines",
                        "name": run,
                        "marker": {"color": color},
                        "showlegend": i == 0 and j == 0,
                        }), i + 1, j + 1)

                    """
                    fig.append_trace(go.Histogram(**{
                        "x": x,
                        "histnorm": 'probability',
                        "opacity": 0.75,
                        "nbinsx": 20,
                        "name": run,
                        "marker": {"color": color},
                        "showlegend": i == 0 and j == 0,
                        }), i + 1, j + 1)
                    """

        # update labels and legend
        self.update_xlabels(
            fig, row_names=metrics, column_names=groups)
        fig.update_layout(
            barmode="overlay",
            legend_title_text='Run names:')
        return fig


def main(args):
    df = oh.output_folder_to_pandas(args.folder)
    group_map = {
        "EW_cars": ["EC_2", "EC_3", "EC_4", "WC_2", "WC_3", "WC_4"],
        "NS_cars": ["NC_2", "NC_3", "NC_4", "SC_2", "SC_3", "SC_4"],
        "EW_cyclist": ["EC_1", "WC_1"],
        "NS_cyclist": ["NC_1", "SC_1"]
    }
    df = oh.add_lane_group_column(df, group_map)

    dm = DataModel(df)
    view = DashView(dm)
    view.start()

if __name__ == '__main__':
    ag = argparse.ArgumentParser()
    ag.add_argument("-f", "--folder", type=str, required=True, help=
        "Path to the folder with detector and lane emissions output")
    args = ag.parse_args()
    main(args)
