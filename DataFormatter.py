import pandas as pd


class DataFormatter():


    def __init__(self):
        self.df = None


    def format_dicts(self, audio_features, tracks_data, artist_name, artist_id):
        '''
        Format dictionaries that will be used to create a single large DataFrame holding
        information on audio features, top tracks, and artist data.
        '''
        modified_audio_features_dict = {} # dictionary will contain information on audio features for every track provided by audio_features
        for track_audio_features in audio_features["audio_features"]: # iterate over each track's audio features
            for audio_feature in track_audio_features: # iterate over each audio feature
                if audio_feature not in modified_audio_features_dict:
                    modified_audio_features_dict[audio_feature] = [] # create the key
                modified_audio_features_dict[audio_feature].append(track_audio_features[audio_feature]) # append to the list held in the value

        track_and_artist_dict = {"track_id": [], "track_name": [], "artist_name": [], "artist_id": []} # will contain simple information on top tracks and artist
        for track in tracks_data["tracks"]:
            track_and_artist_dict["track_id"].append(track["id"])
            track_and_artist_dict["track_name"].append(track["name"])
            track_and_artist_dict["artist_name"].append(artist_name)
            track_and_artist_dict["artist_id"].append(artist_id)

        top_tracks_info_dict = {} # will contain more specific information on top tracks
        for track in tracks_data["tracks"]:
            for k in track:
                if k not in top_tracks_info_dict:
                    top_tracks_info_dict[k] = []
                top_tracks_info_dict[k].append(track[k])

        return modified_audio_features_dict, track_and_artist_dict, top_tracks_info_dict


    def format_df(self, audio_features_dict, artist_tracks_dict, top_tracks_info_dict):
        '''
        Given two dictionaries, set self.df to become a DataFrame holding all information on artists, 
        and top tracks, by converting the provided dictionaries to DataFrames, and merging them into
        one DataFrame.
        '''
        # create the DataFrame containing information about the audio features of the top tracks
        audio_features_df = pd.DataFrame.from_dict(audio_features_dict) # turning audio_features_dict into a DataFrame
        audio_features_df.rename(columns={"id": "track_id"}, inplace=True) # rename column titled "id" to "track_id" so it is more specific

        # create the DataFrame containing information about the artist and their top tracks
        artist_tracks_df = pd.DataFrame.from_dict(artist_tracks_dict) # turning artist_tracks_dict into a DataFrame

        # create a DataFrame containing all the information on top tracks
        top_tracks_info_df = pd.DataFrame.from_dict(top_tracks_info_dict)
        top_tracks_info_df.rename(columns={"id": "track_id"}, inplace=True) # rename column titled "id" to "track_id" so it is more specific

        self.df = pd.merge(artist_tracks_df, audio_features_df, how="outer", on=["track_id"]) # merge the two DataFrames on the column titled "track_id"
        self.df = pd.merge(self.df, top_tracks_info_df, how="outer", on=["track_id"]) # merge the two DataFrames on the column titled "track_id"


    def create_large_df(self, df):
        '''
        Combine self.df with the passed in df.
        Return the new DataFrame.
        '''
        df = pd.concat([df, self.df], ignore_index=True) # data_formatter.df is the DataFrame containing information about the related artist and their tracks
        return df
    

    def save_as_csv(self, path):
        '''
        Save self.df to the path provided.
        '''
        self.df.to_csv(path)
