import os, sys

sys.path.append(os.getcwd())
from src.serve import app

app

if __name__ == "__main__":
    print(
        "Please run this script through your bash cli with command 'uvicorn webserver:app'. See 'https://www.uvicorn.org/' for more information about uvicorn settings."
    )
