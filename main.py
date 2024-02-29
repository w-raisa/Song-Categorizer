
import config

from SpotifyAPICaller import SpotifyAPICaller 
from DataFormatter import DataFormatter
from ClusteringModel import ClusteringModel


# Constants 
MAIN_ARTIST_NAME = config.MAIN_ARTIST_NAME # Name of main artist to analyze
MAIN_ARTIST_ID = config.MAIN_ARTIST_ID # Spotify ID of the artist to analyzed

# Spotify API key credentials 
CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET

# Constants (parameters) for clustering model 
K = config.NUM_CLUSTERS # number of clusters to use for the clustering algorithm
INIT_PARAM = config.INIT_PARAM 
RANDOM_STATE = config.RANDOM_STATE
N_INIT = config.N_INIT

# Features that will be used by clustering model
FEATURES = config.FEATURES


if __name__ == "__main__":
    Spotify_API_caller = SpotifyAPICaller(CLIENT_ID, CLIENT_SECRET)
    Spotify_API_caller.request_spotify_access_token() # create API token

    # Q1
    response_top_tracks = Spotify_API_caller.get_tracks(MAIN_ARTIST_ID) # gets the top tracks outputted by Spotify API for this artist
    top_tracks_id_list = [track["id"] for track in response_top_tracks["tracks"]] # list of track ids
    response_audio_features = Spotify_API_caller.get_audio_features(top_tracks_id_list) # get the audio features of the tracks in track_ids_list
    
    # formats Led Zeppelin artist and top tracks information into a DataFrame (partly answers Q3)
    data_formatter = DataFormatter()
    audio_features_dict, artist_tracks_dict, d = data_formatter.format_dicts(response_audio_features, response_top_tracks, MAIN_ARTIST_NAME, MAIN_ARTIST_ID)
    data_formatter.format_df(audio_features_dict, artist_tracks_dict, d)
    df = data_formatter.df
    
    # Q2
    response_related_artists = Spotify_API_caller.get_related_artists(MAIN_ARTIST_ID)
    for related_artist in response_related_artists["artists"]: # iterate over the list of related artists
        related_artist_id = related_artist["id"]
        related_artist_name = related_artist["name"]
        
        # Get the top tracks of the related artist, and get the audio features of those top tracks
        response_ra_top_tracks = Spotify_API_caller.get_tracks(related_artist_id) # related artist top tracks response from API
        ra_top_tracks_id_list = [track["id"] for track in response_ra_top_tracks["tracks"]] # list of the top track ids for the related artist 
        response_ra_audio_features = Spotify_API_caller.get_audio_features(ra_top_tracks_id_list) # get the audio features of the tracks in ra_top_tracks_id_list

        # Formatting related artists and top tracks information into a DataFrame
        # Q3
        ra_audio_features_dict, r_artist_tracks_dict, top_tracks_info_dict = data_formatter.format_dicts(response_ra_audio_features, response_ra_top_tracks, related_artist_name, related_artist_id)
        data_formatter.format_df(ra_audio_features_dict, r_artist_tracks_dict, top_tracks_info_dict) # formats a DataFrame containing info about the related artist and their tracks
        df = data_formatter.create_large_df(df)

    data_formatter.df = df
    data_formatter.save_as_csv("artist_info.csv")
    

    # # Q4
    clustering_model = ClusteringModel(K, INIT_PARAM, RANDOM_STATE, N_INIT, FEATURES)
    labels = clustering_model.build_pipeline(df)
    
    # # Q5
    df = clustering_model.q5(df, labels)