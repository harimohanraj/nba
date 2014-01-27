# gross script to visualize PCA and k-means clustering for basketball data.
# @full_data: pandas DataFrame of any statistics
# @n_pca: number of components to crush data down into
# @n_means: number of cluster groups for k-means algorithm
# 
#
#
# note: this is pretty raw and any bad data will break it. 

from sklearn import decomposition
from sklearn import cluster
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

def reduction(full_data,n_pca,n_means):
	# assumes full_data is indexed by player name
	names = full_data.index.values

	# PCA 
	pca = decomposition.PCA(n_components=n_pca)
	pca.fit(full_data)
	compressed = pca.transform(full_data)

	# K-Means 
	k_means = cluster.KMeans(n_means)
	k_means.fit(compressed)

	# Graph reduced/projected data, label with player names,
	# and color based on labels from K-Means
	plt.scatter(compressed[:,0],compressed[:,1],c=k_means.labels_)
	for i in range(0,len(full_data)-1):
		plt.text(compressed[i,0],compressed[i,1],names[i],fontsize=7)


