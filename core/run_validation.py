import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.validation_ui import app

if __name__ == "__main__":
    print("=" * 50)
    print("実食検証システム起動")
    print("http://localhost:5001")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=False)
