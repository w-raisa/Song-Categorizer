import matplotlib.pyplot as plt
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer


class ClusteringModel():


    def __init__(self, num_clusters, init_param, random_state, n_init, features):
        self.num_clusters = num_clusters
        self.init_param = init_param
        self.random_state = random_state
        self.n_init = n_init
        self.features = features
        self.kmeans_labels = None
        self.pipeline = None # will initialize a ppln containing data preprocessing steps and the clustering model itself


    def build_pipeline(self, df):
        '''
        Build a pipeline that first pre-processes the features to be input into the 
        clustering  model. The pipeline will also contains the clustering model as the 
        second step. Clustering model will cluster the top tracks provided by df.
        Returns the predicted labels of each of the top tracks.
        '''
        features = ["danceability", "energy"] # columns/features we want our model to look at at
        standard_scaler = StandardScaler(copy=True,with_mean=True,with_std=True) # need to standardize these continuous features
        stdzing_transformer = Pipeline(steps=[("standard_scaler", standard_scaler)]) # Putting standard_scaler in a Pipeline so we can put it in a ColumnTransformer
        preprocessor = ColumnTransformer(
            transformers=[
                    ("stdzing_transformer", stdzing_transformer, features), # apply stdzing_transformer onto the features/columns specified by the list features
                ]
            )

        kmeans = KMeans(n_clusters = self.num_clusters, init = self.init_param, random_state = self.random_state, n_init=self.n_init) # KMeans model
        self.pipeline = Pipeline( # Creating a Pipeline where the the first step is to preprocess the data (stdize) and then fit std'd data to model
            steps = [
                    ("preprocessor", preprocessor),
                    ("kmeans_model", kmeans)
                ]
            )
        y_kmeans = self.pipeline.fit_predict(df) # passing df data into the pipeline to fit model to the data and predict labels of the tracks.


        # Plotting the clusters

        scaler = StandardScaler() # need to standardize the two features and have an instance of it to be able to plot the clusters
        X = scaler.fit_transform(pd.DataFrame(df.iloc[:, [4, 5]]))

        colour_dict = {0: "red", 1: "green", 2: "blue"} # colours for each cluster
        for i in range(self.num_clusters):
            plt.scatter(X[y_kmeans==i, 0], X[y_kmeans==i, 1], s=30, c=colour_dict[i], label ='Cluster ' + str(i))

        # Plot centroids onto the graph with the clusters
        # self.pipeline.steps[-1][-1] contains an instance of the fitted KMeans model
        plt.scatter(self.pipeline.steps[-1][-1].cluster_centers_[:, 0], self.pipeline.steps[-1][-1].cluster_centers_[:, 1], s=150, c='magenta', label = 'Centroids')
        plt.title('Clusters of Top Tracks')
        plt.legend(loc="upper right")
        plt.show()

        self.analysis(df) # Analyzing which K is optimal

        self.kmeans_labels = self.pipeline.steps[-1][-1].labels_ # self.pipeline.steps[-1][-1] contains an instance of the fitted KMeans model
        return self.kmeans_labels # returning each top track's predicted label to answer Q5


    def analysis(self, df):
        """
        Analyzing what value of K (number of clusters) would be optimal for
        our clustering model by calculating Silhouette Score and graphing 
        Elbow and Silhouette Score graphs.

        Question 4 Answer: To answer question 4, I used a Scikit-Learn KMeans++ model to cluster the dataset.

        My recommendation for the optimal number of clusters would be 3. The reason for this is due to the fact that 
        in the Elbow graph which I plot and output in the code using Matplotlib, the point at which the within-cluster 
        sum of squares (WCSS) starts to decrease more slowly occurs is at x = 3. We can see the WCSS starts to decrease 
        more slowly at x = 4 too. To confirm whether 3 clusters would be better or 4 clusters would be better to have in 
        our KMeans++ model, we can view Silhouette Scores as well.

        Looking at the Silhouette Scores, we can see that for 3 clusters, we obtain a score of 0.3642. For 4 clusters, we
        obtain a much lower Silhouette Score, at 0.3580. So this would confirm that indeed 3 clusters is the optimal number
        of clusters for our model which is why I would recommend it. 
        
        We can also see from the Silhouette Scores that 6 clusters would be a great choice. But in tandem with the Elbow graph,
        it’s clear that 6 clusters isn’t the best option here as it goes far past the elbow at x = 3. By viewing the Silhouette
        Scores, alongside the Elbow graph, we can confirm that 3 clusters is a great choice for my KMeans++ model to cluster
        the dataset. My final recommendation for the optimal number of clusters would be 3.
        """
        # Standardize features
        scaler = StandardScaler()
        X = scaler.fit_transform(pd.DataFrame(df.iloc[:, [4, 5]]))

        num_clusters = []
        wcss = []
        silhouette_scores = []
        for k in range(2, 11):
            kmeans = KMeans(n_clusters = k, init = self.init_param, random_state = 42, n_init=10) # KMeans model with k clusters.
            kmeans.fit(X) # fit data to KMeans model

            num_clusters.append(k) # num_clusters will be x-axis in our graphs
            
            sil_score = silhouette_score(X, kmeans.labels_) # calculating Silhouette Score using Sklearn method
            silhouette_scores.append(sil_score) # append Silhouette Score to be able to graph it, will be y-axis in first graph

            # kmeans.inertia_ returns the WCSS value
            wcss.append(kmeans.inertia_) # append inertia to be able to plot Elbow graph, will be y-axis in second graph


        # Plot Silhouette Score
        plt.title('Silhouette Scores Graph')
        plt.xlabel('Number of Clusters')
        plt.ylabel('Silhouette Score')
        plt.plot(num_clusters, silhouette_scores)
        plt.show()

        # Plot Elbow graph
        plt.title('Elbow Graph')
        plt.xlabel('Number of Clusters')
        plt.ylabel('WCSS')
        plt.plot(num_clusters, wcss)
        plt.show() 


    def q5(self, df, labels):
        '''
        Find for each artist in df how many different clusters contain at least one of their top tracks
        using labels. Result is printed.
        Return df containing an extra column containing the labels for each top track for each artist.
        '''
        # Create a DataFrame mapping each artist's top tracks to their predicted labels
        labels_dict = {"labels": list(labels), "track_id": list(df["track_id"])}
        labels_df = pd.DataFrame.from_dict(labels_dict) # convert labels_dict to DataFrame

        # merge DataFrame containing labels (labels_df) with DataFrame containing the rest of the track and artist information (df)
        df = pd.merge(labels_df, df, how="outer", on=["track_id"]) # df now contains one extra column, the column with the predicted labels

        artists_to_clusters = {} # dictionary mapping artists to the clusters their top tracks have appeared in
        for i in df.itertuples(): # iterate over each row of df
            artist_name = i.artist_name # extracts artist name from row i
            if artist_name not in artists_to_clusters:
                artists_to_clusters[artist_name] = set()
            artists_to_clusters[artist_name].add(i.labels)
        
        # print out how many clusters each artist has at least one top track in.
        print("Question 5 Answer:")
        for artist in artists_to_clusters:
            if len(artists_to_clusters[artist]) == 3:
                print(artist + " has at least one top track in all three clusters.")
            elif len(artists_to_clusters[artist]) == 2:
                print(artist + " has at least one top track in the following two clusters: " + str(artists_to_clusters[artist]))
            elif len(artists_to_clusters[artist]) == 1:
                print(artist + " has at least one top track in one clusters. The cluster is " + str(artists_to_clusters[artist]))

        return df