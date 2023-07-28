from flask import Flask, request, jsonify
from src.FBApp2 import firebaseDB
from json import loads
from time import sleep
import mysql.connector
import threading

# Initialise Configuration
with open("./config/db.json") as file, open("./config/config.json") as file1:
    conf = file.read()
    conf1=file1.read()
_confJSON1=loads(conf1)
_confJSON = loads(conf)

dc={}
class SQLConnect:
    def __init__(self, cnx=None):
        if cnx is None:
            self._connect_()
        else:
            if cnx.is_connected():
                pass
            else:
                self._connect_()

    def _connect_(self):
        self.client = mysql.connector.connect(
            host=_confJSON1["SQL"]["credentials"]["host"],
            user=_confJSON1["SQL"]["credentials"]["username"],
            password=_confJSON1["SQL"]["credentials"]["password"],
            database=_confJSON1["SQL"]["credentials"]["database"]
        )

    def _getCursor_(self):
        return self.client.cursor()

    def _getClient_(self):
        return self.client

app = Flask(__name__)
app.secret_key = "12345"

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Active"})

@app.route("/freq", methods=["GET"])
def freq():
    global dc
    sid=request.args.get("SID")
    if sid in dc:
        return jsonify({"value": dc[sid]})
    return jsonify({"value": "Not Found"})

@app.route("/worker", methods=["GET", "POST"])
def worker():
    global dc
    sid=request.args.get("sid")
    cid=request.args.get("cid")
    freq=int(request.args.get("freq"))
    
    try:
        fdb=firebaseDB(sid, cid)
        if sid not in dc:
            dc[sid]=freq
        t1=threading.Thread(target=thr, args=(fdb, freq, sid))
        t1.start()
    except:
        return jsonify({"status": -1})
    return jsonify({"status": 1})

def thr(fdb, freq, sid):
    global dc
    tm=0
    while fdb.get_status():
        if (tm>3600):
            fdb.exit_session()
            
            s = SQLConnect()
            client = s._getClient_()
            cursor = s._getCursor_()

            cursor.execute(f"UPDATE sessions SET endtime='{get('http://worldtimeapi.org/api/timezone/Asia/Kolkata').json()['datetime'][:19].replace('T', ' ')}' WHERE sessionID='{sid}';")
            client.commit()

            cursor.close()
            client.close()
            break
        sleep(freq)
        tm+=freq
        fdb.update_taken(tm//freq)
        print("[INFO] Updated", tm, freq)
    if sid in dc: dc.pop(sid)
    print("[INFO] Stopped")

if __name__ == "__main__":
    app.run(debug=True,port=5000)
