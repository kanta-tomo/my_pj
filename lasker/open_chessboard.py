"""Start the browser chessboard and open it in the default browser."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import webbrowser


PROJECT_DIRECTORY = Path(__file__).resolve().parent
SERVER_ADDRESS = "127.0.0.1"
PREFERRED_PORT = 8000
PAGE_PATH = "/web/"


def create_server() -> ThreadingHTTPServer:
    """Use port 8000 when available, or let the OS choose another port."""
    handler = partial(SimpleHTTPRequestHandler, directory=str(PROJECT_DIRECTORY))
    try:
        return ThreadingHTTPServer((SERVER_ADDRESS, PREFERRED_PORT), handler)
    except OSError:
        return ThreadingHTTPServer((SERVER_ADDRESS, 0), handler)


def main() -> None:
    server = create_server()
    port = server.server_address[1]
    url = f"http://{SERVER_ADDRESS}:{port}{PAGE_PATH}"
    print(f"Chessboard opened at {url}")
    print("Keep this terminal open while playing. Press Ctrl+C here to stop the server.")

    try:
        webbrowser.open(url, new=2)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nChessboard server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
