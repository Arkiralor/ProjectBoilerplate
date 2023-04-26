from dotenv import read_dotenv
from waitress import serve

def server():
    read_dotenv(override=True)

    from core.wsgi import application
    serve(application, port='8000')
    
if __name__ == '__main__':
    server()