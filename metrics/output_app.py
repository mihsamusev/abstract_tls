import argparse
import json

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


def total_agg(x: pd.DataFrame, metric: str, *args):
    return x[metric][x[metric] > 0].sum()

def max_agg(x: pd.DataFrame, metric: str, *args):
    return x[metric].max()

def weighted_mean_agg(x: pd.DataFrame, metric: str, weight_col: str):
    result = np.nan
    if x["count"].sum() != 0:
        result = np.average(x[metric], weights=x[weight_col])
    return result


class DataModel():
    NON_METRICS = ["run_name", "begin", "end", "lane", "lane_group", "count"]
    aggregation_strategy = {
        "max": max_agg,
        "total": total_agg,
        "mean": weighted_mean_agg
    }

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def get_timeseries(self, run, metric, lane_group):
        df = self.data.loc[
            (self.data["run_name"] == run) &
            (self.data["lane_group"] == lane_group)
            ]
        
        # extract column name prefix
        metric_prefix = metric.split("_")[0]
        agg_fun = DataModel.aggregation_strategy[metric_prefix]

        # apply time wise aggregation depending on the prefix
        df_agg = df[["begin","count", metric]].groupby("begin").apply(
            agg_fun, *(metric, "count"))

        # for debug
        # print(df[["begin", "count", metric]], df_agg)

        t, x = np.array([[0, 0]]).T
        if not df_agg.empty:
            t = df_agg.index.to_numpy()
            x = df_agg.to_numpy()
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
        non_metric = DataModel.NON_METRICS
        return [c for c in self.data.columns if c not in non_metric]

    def get_lane_groups(self):
        """
        Return list of lane_groups found in the runs
        """
        return self.data["lane_group"].unique()

class DashView():
    COLOR_PALETTE = px.colors.qualitative.Plotly
    MAX_COLORS = len(COLOR_PALETTE)
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

    def update_labels(self, figure, row_names, column_names):
        """
        Updates labels depending on the row metrics    
        """
        p = 0
        for metric in row_names:
            for _ in column_names:
                xaxis_name = "xaxis" if p==0 else f"xaxis{p + 1}"
                yaxis_name = "yaxis" if p==0 else f"yaxis{p + 1}"
                p += 1
                figure.update_layout(
                    {yaxis_name: {"title": "{} {}".format(metric, "[units]")}})
                figure.update_layout(
                    {xaxis_name: {"title": "time [s]"}})
    

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
            color = DashView.COLOR_PALETTE[k % DashView.MAX_COLORS]
            for i, metric in enumerate(metrics):
                for j, group in enumerate(groups):    
                    
                    # x = self.datamodel.get_data(run, metric, user)
                    t, x = self.datamodel.get_timeseries(run, metric, group)

                    fig.append_trace(go.Scatter(**{
                        "x": t,
                        "y": x,
                        "name": run,
                        "marker": {"color": color, "size": 12},
                        "showlegend": i == 0 and j == 0,
                        }), i + 1, j + 1)

        # update labels and legend
        self.update_labels(
            fig, row_names=metrics, column_names=groups)
        fig.update_layout(
            barmode="overlay",
            legend_title_text='Run names:')
        return fig


def main(args):
    DET_METRICS = {
        "meanTimeLoss": "mean_time_loss",
        "meanSpeed": "mean_speed",
        "maxVehicleNumber": "count",
        "maxHaltingDuration": "max_waiting_time",
        "maxJamLengthInVehicles": "max_queue_veh",
    } # where does it go to satisfy open/closed principle

    EMIT_METRICS = {
        "CO2_abs": "total_co2",
        "fuel_abs": "total_fuel"
    }
    df = oh.output_folder_to_pandas(
        args.folder, 
        DET_METRICS,
        EMIT_METRICS)


    group_map = {}
    if args.groups:
        with open(args.groups, "r") as fin:
            group_map = json.load(fin)
    df = oh.add_lane_group_column(df, group_map)

    dm = DataModel(df)
    view = DashView(dm)
    view.start()

if __name__ == '__main__':
    ag = argparse.ArgumentParser()
    ag.add_argument("-f", "--folder", type=str, required=True, help=
        "Path to the folder with detector and lane emissions output")
    ag.add_argument("-g", "--groups", type=str, default=None, help=
        "path to JSON for grouping lanes by leg and creating lane_groups column in Pandas")
    args = ag.parse_args()
    main(args)
