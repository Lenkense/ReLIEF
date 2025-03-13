import matplotlib
import matplotlib.pyplot as plt
from numpy import nanmax,nanmin,nanmean,nansum
from scipy.stats import mannwhitneyu
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

    ylabel = {'makespan':'makespan', 'totalCost':'cost',
                'aggMC':'aggMC','totalReward':'reward'}
    metrics = ylabel.keys()
    aggregation = {metric:'mean' for metric in metrics}
    aggregationSignificance = {f"{metric}Significance":'max' for metric in metrics}
    aggregation = aggregation | aggregationSignificance
    labels = {'QL':'base-RL', 'QLDBEA':'ReLIEF-I-DBEA', 'QLNSGAIII':'ReLIEF-NSGA-III'}
    baseline = 'QL'
    window = 10
    alpha = 0.01

    df = pd.read_csv(CASES_FILE)
    df['makespan'] = df['makespan'].apply(lambda x: x / 3600)
    df['aggMC'] = np.hypot((df['makespan']), df['totalCost'])
    df['algorithm'] = df['autoscalerArgs'].apply(lambda x: x.split(":")[1])
    df['epsilon'] = df['autoscalerArgs'].apply(lambda x: x.split(":")[5])
    df['bin'] = df['episode'].apply(lambda x: ((x - 1) // window) * window + window / 2.0)
    df = df[['workflow','epsilon','algorithm','aggMC','makespan','totalCost','totalReward','bin']]

    dfGrouped = df.groupby(['workflow', 'epsilon','bin'], as_index=False)
    for metric in metrics:
        df[f"{metric}Significance"] = False
    for (workflow, epsilon, bin), group in dfGrouped:
        dfBaseline = group.loc[group['algorithm'] == baseline]
        for metric in metrics:
            baselineMetric = dfBaseline[metric].values
            for algorithm, sample in group.groupby('algorithm'):
                if baseline == algorithm:
                    continue
                _, pvalue = mannwhitneyu(baselineMetric, sample[metric].values)
                df.loc[sample.index, f"{metric}Significance"] = pvalue < alpha
    dfProcessed = df.groupby(['workflow', 'epsilon','bin','algorithm'], as_index=False)\
                    .agg(aggregation)
    
    for metric in metrics:
        dfProcessed[f"Differences_{metric}"] = 0.0
        dfProcessed[f"Baseline_significative_{metric}"] = np.nan
    dfGrouped = dfProcessed.groupby(['workflow', 'epsilon'])
    for (workflow, epsilon), group in dfGrouped:
        dfBaseline = group.loc[group['algorithm'] == baseline]
        for metric in metrics:
            baselineMetric = dfBaseline[metric].values
            for algorithm, binnedValues in group.groupby('algorithm'):
                if algorithm == baseline:
                    continue
                graphData = binnedValues[metric].values - baselineMetric
                if metric != 'totalReward':
                    graphData *= -1
                significance = binnedValues[f"{metric}Significance"].values
                positiveValues = significance & (graphData > 0.0)
                negativeValues = significance & (graphData < 0.0)
                middleEp = binnedValues['bin']

                indeces = binnedValues.index
                dfProcessed.loc[indeces,f"Differences_{metric}"] =\
                        np.where(significance,graphData,np.nan)
                dfProcessed.loc[indeces,f"Baseline_significative_{metric}"] =\
                        np.where(significance,baselineMetric,np.nan)

                #absolute values
                fig, ax = plt.subplots()
                ax.plot(middleEp, graphData, 'k-',label='mean in the window')
                ax.plot(middleEp, np.zeros_like(middleEp), 'k-',label='')
                ax.scatter(middleEp[positiveValues], graphData[positiveValues],
                           s=320, color='green', label='significance')
                ax.scatter(middleEp[negativeValues], graphData[negativeValues],
                           s=320, color='red', label='significance')
                plt.xlabel('Episodes')
                plt.ylabel('Difference in means\n values of ' + ylabel[metric])
                plt.title(f"{workflow} {labels[algorithm]} $\mathrm{{\epsilon}}$={epsilon}")
                plt.savefig(f"results/{metric}_{workflow}_{epsilon}_{algorithm}.pdf")
                plt.close()
    
                #relatives values
                k = 1 if metric != 'totalReward' else -1
                fig, ax = plt.subplots()
                ax.plot(middleEp, graphData / baselineMetric * k,
                        'k-',label='mean in the window')
                ax.plot(middleEp, np.zeros_like(middleEp), 'k-',label='0')
                ax.scatter(middleEp[positiveValues],
                           graphData[positiveValues] / baselineMetric[positiveValues] * k,
                           s=320, color='green', label='significance')
                ax.scatter(middleEp[negativeValues],
                           graphData[negativeValues] / baselineMetric[negativeValues] * k,
                           s=320, color='red', label='significance')
                plt.xlabel('Episodes')
                plt.ylabel('Relative difference in means\n values of ' + ylabel[metric])
                plt.title(f"{workflow} {labels[algorithm]} $\mathrm{{\epsilon}}$={epsilon}")
                plt.savefig(f"results/{metric}_{workflow}_{epsilon}_relative_{algorithm}.pdf")
                plt.close()
    
    aggregation1 = {f"Differences_{metric}":[nanmin, nanmax, nanmean, nansum]\
                    for metric in metrics}
    aggregation2 = {f"Baseline_significative_{metric}":nansum for metric in metrics}
    aggregation = aggregation1 | aggregation2
    dfFinal = dfProcessed.groupby(
        ['workflow','epsilon','algorithm']).agg(
            aggregation)
    medians = df.groupby(
        ['workflow','epsilon','algorithm']).agg(
            {metric:'median' for metric in metrics})
    for metric in metrics:
        medians[f"{metric}"] = medians.groupby(
            ['workflow','epsilon'])[f"{metric}"].transform('first')

    for metric in metrics:
        dfFinal[f"Differences_{metric}",'nansum'] = \
            dfFinal[f"Differences_{metric}",'nansum'].apply(lambda x: window * x)
        dfFinal[f"Differences_{metric}",'reference_sum'] = \
            dfFinal[f"Baseline_significative_{metric}",'nansum'].apply(lambda x: window * x)
        dfFinal[f"Differences_{metric}",'saved_percentage'] = \
            dfFinal[f"Differences_{metric}",'nansum'] / dfFinal[f"Differences_{metric}",'reference_sum'] * 100
        dfFinal[f"Differences_{metric}",'equivalent_episode'] = \
            dfFinal[f"Differences_{metric}",'nansum'] / medians[f"{metric}"]
        dfFinal[f"Differences_{metric}",'reference_median'] = medians[f"{metric}"]
    dfFinal = dfFinal.rename_axis(
            columns=['metrics', 'statistics']
        ).sort_index(axis=1).drop(
            columns=[f"Baseline_significative_{metric}" for metric in metrics]
        ).rename(
            columns={f"nan{statistic}":statistic for statistic in [
                'min', 'max', 'mean', 'sum'
            ]}
        ).rename(
            {f"Differences_{metric}":metric for metric in metrics}, axis=1
        ).stack(level=0)[['min', 'max', 'mean', 'sum', 'saved_percentage',
            'equivalent_episode','reference_median','reference_sum']]
    dfFinal.to_csv('results/summary.csv')
    Table3 = dfFinal.drop(
        index='totalReward', level=3).drop(index=baseline,level=2)[[
            'sum', 'equivalent_episode']].stack(level=0).unstack(
                level=[0,2,1,4]).sort_index(
                    axis=1, level=[0,1,2,3], ascending= [True, True, True, False]
            ).groupby(axis=1, level=0)
    pd.DataFrame().to_csv('results/Table3.csv', mode='w')
    for workflow, group in Table3:
        group.to_csv('results/Table3.csv', mode='a')
    # remember to drop totalReward
    Table4 = dfFinal.drop(
        index=baseline, level=2)[['min', 'max', 'mean', 'sum', 'saved_percentage']]
    indeces = Table4.xs('aggMC', level=3).groupby('workflow')['sum'].idxmax()
    indeces = pd.MultiIndex.from_tuples(indeces)
    indeces = indeces.to_frame(index=False)
    indeces = indeces.merge(
        pd.Index(sorted(metrics)).to_frame(index=False), how='cross'
    )
    indeces = pd.MultiIndex.from_frame(indeces)
    Table4.loc[indeces].drop('totalReward', level=3).to_csv('results/Table4.csv')

