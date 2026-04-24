import requests
from flask import current_app

class YouTubeService:
    
    @staticmethod
    def search_videos(query, max_results=10):
        """Busca videos en YouTube"""
        api_key = current_app.config['YOUTUBE_API_KEY']
        url = "https://www.googleapis.com/youtube/v3/search"
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'key': api_key,
            'videoEmbeddable': 'true'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                video = {
                    'id': item['id']['videoId'],
                    'titulo': item['snippet']['title'],
                    'descripcion': item['snippet']['description'],
                    'canal': item['snippet']['channelTitle'],
                    'fecha': item['snippet']['publishedAt'][:10],
                    'miniatura': item['snippet']['thumbnails']['medium']['url']
                }
                videos.append(video)
            
            return videos
        except Exception as e:
            print(f"Error al buscar videos: {e}")
            return []
    
    @staticmethod
    def get_video_details(video_id):
        """Obtiene detalles de un video específico"""
        api_key = current_app.config['YOUTUBE_API_KEY']
        url = "https://www.googleapis.com/youtube/v3/videos"
        
        params = {
            'part': 'snippet,statistics',
            'id': video_id,
            'key': api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('items'):
                item = data['items'][0]
                video = {
                    'id': video_id,
                    'titulo': item['snippet']['title'],
                    'descripcion': item['snippet']['description'],
                    'canal': item['snippet']['channelTitle'],
                    'fecha': item['snippet']['publishedAt'][:10],
                    'vistas': item['statistics'].get('viewCount', 0),
                    'likes': item['statistics'].get('likeCount', 0)
                }
                return video
            return None
        except Exception as e:
            print(f"Error al obtener detalles del video: {e}")
            return None