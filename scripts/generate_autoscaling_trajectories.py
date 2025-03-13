"""
Script for plotting autoscaling trajectories.

Usage:
    generate_autoscaling_trajectories.py data_path
Args:
    data_path: path to file 1.training_results_experiments.csv

Author: David A. Monge <damonge27@gmail.com, dmonge@uncu.edu.ar>
Date: 2023-09-01
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams.update({'font.size': 14})
matplotlib.rcParams['lines.linewidth'] = 2
matplotlib.rcParams['lines.markersize'] = 10

# params
smooth_time_win = 30  # a number of time steps to smooth or None to disable
scale = 'log'
scale = 'linear'
cases = {
    'CyberShake-100': [
        {'QL': 0.1, 'QLDBEA': 0.1, 'QLNSGAIII': 0.1},
        {'QL': 0.0, 'QLDBEA': 0.0, 'QLNSGAIII': 0.0}
    ],
    'Montage-100': [
        {'QL': 0.1, 'QLDBEA': 0.1, 'QLNSGAIII': 0.1},
        {'QL': 0.0, 'QLDBEA': 0.0, 'QLNSGAIII': 0.0}
    ],
    'SIPHT-97': [
        {'QL': 0.1, 'QLDBEA': 0.1, 'QLNSGAIII': 0.1},
        {'QL': 0.0, 'QLDBEA': 0.0, 'QLNSGAIII': 0.0}
    ],
    'LIGO-100': [
        {'QL': 0.1, 'QLDBEA': 0.1, 'QLNSGAIII': 0.1},
        {'QL': 0.0, 'QLDBEA': 0.0, 'QLNSGAIII': 0.0}
    ]
}

# data
data_path = sys.argv[1]
plots_dir = 'results/'
data = pd.read_csv(data_path)


def _prepare(data):
    data['method'] = data.case.apply(lambda s: s.split(':')[1])
    data['epsilonType'] = data.case.apply(lambda s: 'exponential' if ':exp:' in s else 'fixed')
    data['run'] = data.case.apply(lambda s: int(s.split(')')[0].split(':')[-1]))
    data['initialEpsilon'] = data.case.apply(lambda s: float(s.split(':')[5]))
    data['makespan'] = data['makespan'] / 3600
    data = data[['method', 'workflow', 'epsilonType', 'initialEpsilon',
                 'epsilon', 'episode', 'policy', 'makespan', 'totalCost']]
    return data


data = _prepare(data)
data = data.groupby(by=['method', 'workflow', 'epsilonType', 'initialEpsilon',
                        'episode']).mean().reset_index()

# plots
for workflow, config_wf in cases.items():
    print(f'wf: {workflow}')
    for epsilon_type in ['exponential']:
        for config in config_wf:
            print(f'eps: {epsilon_type}')
            _data_case = []
            for method, epsilon in config.items():
                _data = data.loc[data.workflow == workflow]
                _data = _data.loc[data.method == method]
                _data = _data.loc[data.epsilonType == epsilon_type]
                _data = _data.loc[data.initialEpsilon == epsilon]
                _data = _data[['method', 'makespan', 'totalCost', 'episode']]
                _data[['method_param']] = f'{method}:{epsilon_type[:3]}:{epsilon}'
                _data_case.append(_data)
            _data_case = pd.concat(_data_case, ignore_index=True)
            if smooth_time_win is not None and isinstance(smooth_time_win, int):
                _data_case = (
                    _data_case
                    .sort_values('episode')
                    .groupby(by='method_param')
                    .rolling(smooth_time_win, min_periods=1, center=True)
                    .mean()
                    .reset_index()
                )

            plt.figure(figsize=(5, 5))
            x = 'totalCost'
            y = 'makespan'
            sns.lineplot(data=_data_case, x=x, y=y, hue='method_param', sort=False, estimator=None, alpha=0.7)
            first_episode = _data_case.episode.min()
            last_episode = _data_case.episode.max()
            sns.scatterplot(data=_data_case.loc[_data_case.episode == first_episode], x=x, y=y, hue='method_param',
                            marker='o', legend=False)
            ax = sns.scatterplot(data=_data_case.loc[_data_case.episode == last_episode], x=x, y=y, hue='method_param',
                                marker='X', legend=False)
            plt.xscale(scale)
            plt.yscale(scale)
            plt.ylabel('Makespan [hours]')
            plt.xlabel('Cost [USD]')
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles=handles, labels=['base-RL', 'ReLIEF-I-DBEA', 'ReLIEF-NSGAIII'])
            ax.set(title=workflow)

            plt.tight_layout()
            plt.savefig(f'{plots_dir}/trajectories_{workflow}_{epsilon_type}_{epsilon}_{scale}_avg.pdf')
            plt.close()
