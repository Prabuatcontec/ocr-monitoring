class Config(object):
    DATABASE_CONFIG = {
        'server': 'crs-dev.rds.gocontec.com',
        'user': 'VulcanWebUser',
        'password': 'Vulcan123',
        'name': 'Automation',
    }
    UPLOAD_FOLDER = './static/uploads/'
    API_URL = 'http://localhost:5000/api/'
    API_USER_URL = 'http://api.vulcan.contecprod.com/api/'
    REPO_PATH = 'https://github.com/Prabuatcontec/ocr-receiving'
