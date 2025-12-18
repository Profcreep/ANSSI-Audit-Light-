import socket
from datetime import datetime

def get_context():
    return {
        "hostname": socket.gethostname(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename_date": datetime.now().strftime("%Y%m%d_%H%M%S")
    }
