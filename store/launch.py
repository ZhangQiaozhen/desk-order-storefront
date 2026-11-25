"""Start or reopen the local storefront."""
import urllib.request
import webbrowser
from http.server import ThreadingHTTPServer
from server import Handler, ORIGIN, PORT, initialize

def is_running():
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(ORIGIN+"/", timeout=1) as response:
            return b"/assets/shop.js" in response.read()
    except OSError:
        return False

if is_running():
    webbrowser.open(ORIGIN+"/en/")
else:
    initialize()
    with ThreadingHTTPServer(("127.0.0.1",PORT),Handler) as server:
        print("Desk Order: "+ORIGIN+"   (Ctrl+C to stop)",flush=True)
        webbrowser.open(ORIGIN+"/en/")
        server.serve_forever()

