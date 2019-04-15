import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.cluster import AgglomerativeClustering, DBSCAN, Birch
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, MDS
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler


def colour_mapping(de, fr, ja, ko):
    """
    Function to map each language to a particular colour.
    """
    if de == 1:
        return 'yellow'
    elif fr == 1:
        return 'blue'
    elif ja == 1:
        return 'red'
    elif ko == 1:
        return 'green'


scaler = StandardScaler()

data = pd.read_csv('tweets/data.csv')
ids = data.loc[:, :'id'].to_dict()['id']
colours = data.loc[:, 'de':'ko'].apply((lambda x: colour_mapping(x[0], x[1], x[2], x[3])), axis=1)

data = data.drop(labels='id', axis=1)
scaled_columns = scaler.fit_transform(data.loc[:, 'hashtags':])
# data = np.concatenate([data.loc[:, 'de':'sentiment'], scaled_columns], axis=1)
data = np.concatenate([data.loc[:, 'sentiment':'sentiment'], scaled_columns], axis=1)

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='German', markerfacecolor='yellow', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='French', markerfacecolor='blue', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Japanese', markerfacecolor='red', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Korean', markerfacecolor='green', markersize=10),
]


def plot(Z, title, knn=15, dbscan_args=None, agg_n=4, birch_args=None):
    """
    Plot the scatterplot for the data, along with 3 different clusterings thereof.
    :param Z: output from dimensionality reduction
    :param title: title of this plot
    :param knn: number of neighbours to look for in the k-nearest-neighbour graph
    :param dbscan_args: arguments for DBSCAN clustering
    :param agg_n: number of clusters to look for in agglomerative clustering
    :param birch_args: arguments for Birch clustering
    """

    if birch_args is None:
        birch_args = {'n_clusters': None, 'threshold': 0.5, 'branching_factor': 20}
    if dbscan_args is None:
        dbscan_args = {'eps': 2, 'min_samples': 5}

    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row', num=title)
    f.suptitle(title)
    ax1.scatter(Z[:, 0], Z[:, 1], alpha=0.5, c=colours)
    # ax1.legend(handles=legend_elements)
    ax1.set_title('Language Colouring')
    # for i in ids.keys():
    #     ax1.text(Z[int(i), 0], Z[i, 1], str(ids[i] % 10000).zfill(4), fontsize=9)

    knn_graph = kneighbors_graph(data, knn, include_self=False)
    agg_clustering = AgglomerativeClustering(n_clusters=agg_n, connectivity=knn_graph)
    ax2.scatter(Z[:, 0], Z[:, 1], alpha=0.5, c=agg_clustering.fit_predict(data), cmap=plt.get_cmap('Dark2'))
    ax2.set_title(f'Agglomerative (knn$_{{{knn}}}$, ward)')

    dbscan = DBSCAN(eps=dbscan_args['eps'], min_samples=dbscan_args['min_samples'])
    ax3.scatter(Z[:, 0], Z[:, 1], alpha=0.5, c=dbscan.fit_predict(data), cmap=plt.get_cmap('Dark2'))
    ax3.set_title('DBSCAN')

    birch = Birch(n_clusters=birch_args['n_clusters'], threshold=birch_args['threshold'], branching_factor=birch_args['branching_factor'])
    ax4.scatter(Z[:, 0], Z[:, 1], alpha=0.5, c=birch.fit_predict(data), cmap=plt.get_cmap('Dark2'))
    ax4.set_title('Birch')

    for ax in [ax1, ax2, ax3, ax4]:
        ax.set(xlabel='$z_1$', ylabel='$z_2$')
    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in [ax1, ax2, ax3, ax4]:
        ax.label_outer()

    plt.savefig(f'figs/{title}.png')


def solo_plot(Z, title):
    """
    Plot just the standalone scatterplot of the data.
    :param Z: output of the dimensionality reduction
    :param title: name of this plot
    """
    plt.figure(title)
    plt.suptitle(title)
    plt.scatter(Z[:, 0], Z[:, 1], alpha=0.5, c=colours)
    plt.legend(handles=legend_elements)
    # for i in ids.keys():
    #     plt.text(Z[int(i), 0], Z[i, 1], str(ids[i] % 10000).zfill(4), fontsize=9)

    plt.savefig(f'figs/{title.lower()}.png')


tsne = TSNE()
z = tsne.fit_transform(data)
plot(z, 't-SNE')
solo_plot(z, 't-SNE')

mds = MDS()
z = mds.fit_transform(data)
plot(z, 'MDS')
solo_plot(z, 'MDS')

pca = PCA(n_components=2)
z = pca.fit_transform(data)
plot(z, 'PCA')
solo_plot(z, 'PCA')

pca_no_onehot = PCA(n_components=2)
z = pca_no_onehot.fit_transform(data)
plot(z, 'PCA (no one-hot)')
solo_plot(z, 'PCA (no one-hot)')

plt.show()
