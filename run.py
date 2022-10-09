import sys
from waitress import serve

from app import app

if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'dev':
        print ('[LOG] Run development server')
        app.run(debug=True)
    else:
        print ('[LOG] Run production server')
        serve(app, host='0.0.0.0', port=8080)