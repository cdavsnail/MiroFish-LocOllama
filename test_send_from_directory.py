import os
import tempfile
from flask import Flask, send_from_directory
app = Flask(__name__)

@app.route('/test')
def test():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("test")
        temp_path = f.name
    return send_from_directory(tempfile.gettempdir(), os.path.basename(temp_path))

if __name__ == '__main__':
    with app.test_request_context('/test'):
        res = test()
        print(res)
