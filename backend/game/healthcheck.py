from urllib.request import urlopen


if __name__ == "__main__":
    with urlopen("http://127.0.0.1:8000/openapi.json", timeout=3):
        pass
