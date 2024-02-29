import requests
import os


class SpotifyAPICaller():

    
    def __init__(self, client_id, client_secret):
        self.API_KEY = None # will be generated
        self.client_id = client_id
        self.client_secret = client_secret


    def request_spotify_access_token(self):
        '''
        Send a POST request to obtain a Spotify API key. Sets self.API_KEY
        to the generated API Key.
        '''
        endpoint = "https://accounts.spotify.com/api/token" # URL of the endpoint to send request to
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = {"grant_type": "client_credentials", "client_id": self.client_id, "client_secret": self.client_secret}
        response = requests.post(url = endpoint, headers = headers, data = data)
        data = response.json() # response received from endpoint
        self.API_KEY = data["access_token"] # data["access_token"] contains the API key that will allow us to make requests with


    def get_tracks(self, artist_id):
        '''
        Send a GET request to obtain the top tracks of an artist given the ID of the
        artist artist_id.
        '''
        endpoint = "https://api.spotify.com/v1/artists/" + artist_id + "/top-tracks?market=ES" # URL of the endpoint to send request to
        headers = {"Authorization": "Bearer  " + self.API_KEY}
        response = requests.get(url = endpoint, headers = headers) # send GET request to URL using provided API_KEY
        data = response.json() # response received from endpoint
        if "error" in data:
            self.handle_error(data)
        return data


    def get_audio_features(self, track_id_list):
        '''
        Send a GET request to obtain the audio features of a list of track IDs provided
        by track_id_list.
        '''
        endpoint = "https://api.spotify.com/v1/audio-features?ids=" # URL of the endpoint to send request to
        
        # this endpoint takes in comma separated String of track ids. Formatting the String here.
        for i in range(len(track_id_list)):
            endpoint += track_id_list[i] + ","

        headers = {"Authorization": "Bearer  " + self.API_KEY}
        response = requests.get(url = endpoint, headers = headers) # send GET request to URL using provided API_KEY
        data = response.json() # response received from endpoint
        if "error" in data:
            self.handle_error(data)
        return data


    def get_related_artists(self, artist_id):
        '''
        Send a GET request to obtain the related artists given the artist ID artist_id
        '''
        endpoint = "https://api.spotify.com/v1/artists/" + artist_id + "/related-artists" # URL of the endpoint to send request to
        headers = {"Authorization": "Bearer  " + self.API_KEY}
        response = requests.get(url = endpoint, headers = headers) # send GET request to URL using provided API_KEY
        data = response.json() # response received from endpoint
        if "error" in data:
            self.handle_error(data)
        return data
    

    def handle_error(self, error_data):
        '''
        This method is called if a 400 or 500 level error is encountered. The method
        will display the error message and error code and will then terminate the program.
        '''
        print("A 400 or 500 level error has occurred, please read the following message for more details on what error has occurred.")
        print(error_data)
        print("Exiting program.")
        os._exit(0)
