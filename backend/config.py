import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # MongoDB - Standard port is 27017
    # If you're using a different port, set MONGO_URI in your .env file
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    DATABASE_NAME = 'traffic_violations'
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'processed')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Detection
    CONFIG_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']
    
    # Pagination
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 100
    
    @staticmethod
    def init_app():
        """Initialize application directories"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.PROCESSED_FOLDER, exist_ok=True)
