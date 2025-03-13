import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns
import numpy as np


if __name__ == '__main__':
    try:
        CASES_FILE = sys.argv[1]  # case id
    except:
        print("Filename not given")
        exit()
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42
    matplotlib.rcParams.update({'font.size': 36})
    matplotlib.rcParams['lines.linewidth'] = 3
    matplotlib.rcParams['lines.markersize'] = 10
    matplotlib.rcParams['figure.figsize'] = [20, 10]

    ylabel = {'makespan':'makespan', 'totalCost':'cost','aggMC':'aggMC','totalReward':'reward'}
    metrics = ylabel.keys()
    aggregation = {metric:'mean' for metric in metrics}
    labels = {'QL':'base-RL', 'QLDBEA':'ReLIEF-I-DBEA', 'QLNSGAIII':'ReLIEF-NSGA-III'}

    df = pd.read_csv(CASES_FILE)
    df['makespan'] = df['makespan'].apply(lambda x: x / 3600)
    df['aggMC'] = np.hypot((df['makespan']), df['totalCost'])
    df['algorithm'] = df['autoscalerArgs'].apply(lambda x: x.split(":")[1])
    df['epsilon'] = df['autoscalerArgs'].apply(lambda x: x.split(":")[5])
    df = df[['workflow','epsilon','algorithm','aggMC','makespan','totalCost','totalReward','episode']]
    dfGrouped = df\
                .groupby(['workflow', 'algorithm', 'epsilon', 'episode'], as_index=False)\
                .agg(aggregation)

    for (workflow, epsilon), group in dfGrouped.groupby(['workflow', 'epsilon']):
        for metric in metrics:
            fig, ax = plt.subplots()
            for algorithm, episodeSeries in group.groupby('algorithm'):
                ax.plot(episodeSeries['episode'],episodeSeries[metric], label=labels[algorithm])
            ax.set_xlabel("Episodes")
            ax.set_ylabel(ylabel[metric])
            plt.legend()
            plt.title(f"{workflow} {epsilon}")
            plt.savefig(f"results/{metric}_{workflow}_{epsilon}_learning_curve.pdf")
            plt.close()