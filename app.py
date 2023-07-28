from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from collections import OrderedDict
from shutil import copyfileobj
from json import loads
from random import choices
from random import randint
from string import ascii_uppercase
from datetime import timedelta
from FBApp2 import firebaseDB
from requests import get
import mysql.connector
import base64
import re
import os

# Initialise Configuration
with open("configuration/config.json") as file:
    conf = file.read()
_confJSON = loads(conf)

app = Flask(__name__)
app.secret_key = "12345"
app.permanent_session_lifetime=timedelta(days=1); # minutes=2, seconds=20

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
            host=_confJSON["SQL"]["credentials"]["host"],
            user=_confJSON["SQL"]["credentials"]["username"],
            password=_confJSON["SQL"]["credentials"]["password"],
            database=_confJSON["SQL"]["credentials"]["database"]
        )

    def _getCursor_(self):
        return self.client.cursor()

    def _getClient_(self):
        return self.client

@app.route("/")
@app.route("/index.html", methods=["GET", "POST"])
def index():
    if 'email' in session:
        return redirect(url_for('home'))
    session["loggedin"] = False
    slogin = SQLConnect()
    client = slogin._getClient_()
    cursor = slogin._getCursor_()
    if (
        request.method == "POST"
        and "email" in request.form
        and "password" in request.form
    ):
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(f"SELECT * FROM login WHERE email = '{email}' AND password = '{password}';")
        account = cursor.fetchone()
        cursor.close()
        client.close()
        if account:
            session["permanent"]=True
            session["loggedin"]=True
            session["email"] = account[1]
            session["name"] = account[0]
            return redirect(url_for('home'))
    else:
        return render_template("index.html")
    return render_template("index.html", msg1="Incorrect Username/Password!")

@app.route("/logout.html", methods=["GET"])
def logout():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template("index.html", msg1="You're Not Logged in!")
    session["loggedin"] = False
    session.pop("email")
    session.pop("name")
    return render_template("index.html", msg1="Logged out Successfully!")

@app.route("/signup.html", methods=["GET", "POST"])
def signup():
    if "loggedin" not in session.keys():
        session["loggedin"] = False
    if session["loggedin"]:
        return redirect(url_for('home'))
    ssignup = SQLConnect()
    client = ssignup._getClient_()
    cursor = ssignup._getCursor_()
    msg, tempCheck = '', False
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        checkbox = request.form.getlist('check')

        cursor.execute(f"SELECT * FROM login WHERE email = '{email}';")
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not checkbox:
            msg = 'Please Accept the Terms!'
        else:
            cursor.execute(f"INSERT INTO login (name, email, password) VALUES ('{name}', '{email}', '{password}');")
            client.commit()
            tempCheck, msg = True, 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    if (tempCheck is True):
        cursor.close()
        client.close()
        return render_template('index.html', msg = msg)
    return render_template('signup.html', msg = msg)

@app.route("/register.html", methods=["GET", "POST"])
def register():
    sregister = SQLConnect()
    client = sregister._getClient_()
    cursor = sregister._getCursor_()
    msg, tempCheck = '', False
    if request.method == "POST" and "classid" in request.form and "name" in request.form and "email" in request.form and "regid" in request.form and "snapData" in request.form:
        classid = request.form['classid']
        name = request.form['name']
        email = request.form['email']
        regid = request.form['regid']
        snapData = request.form['snapData']
        checkbox = request.form.getlist('check')

        cursor.execute(f"SELECT * FROM register WHERE classid = '{classid}' AND regid = '{regid}';")
        account = cursor.fetchone()
        if account:
            msg = 'Already registered for this class!'
        elif not snapData:
            msg = 'Please retake Snap!'
        elif not name or not classid or not email or not snapData:
            msg = 'Please fill out the form!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not checkbox:
            msg = 'Please Accept the Terms!'
        else:
            cursor.execute(f"INSERT INTO register (classid, name, email, regid) VALUES ('{classid}', '{name}', '{email}', '{regid}');")
            client.commit()
            saveSnapData(classid, regid, snapData)
            tempCheck, msg = True, 'You have successfully registered!'
    elif request.method == "POST":
        msg = 'Please fill out the form!'
    if (tempCheck is True):
        cursor.close()
        client.close()
        return render_template('register.html', msg=msg)
    return render_template('register.html', msg_incorrect=msg)

def saveSnapData(classid, regid, snap):
    folderPATH = f'filecache/{classid}'
    filePATH = f'filecache/{classid}/{regid}.jpeg'
    try:
        os.makedirs(folderPATH)
    except:
        pass
    with open(filePATH, 'wb') as buffer:
        buffer.write(base64.b64decode(snap.split('data:image/jpeg;base64,')[1].encode()))
    # Incomplete code | Create DATA file with idName=filePATH.split('/')[-1].replace('.jpeg', '')

@app.route("/joinlink.html", methods=["GET","POST"])
def join2():
#http://localhost:5000/join.html?cid=DDWENZ&cname=Algo&freq=60&sid=DDWENZ_93750&In=Admin&st=23
    msg=""

    #print(classid)

    if request.method == "POST" and "regid" in request.form and "localCheck" in request.form:
        #print(request.url)
        classid = request.args.get('cid')
        cname = request.args.get('cname')
        freq = request.args.get('freq')
        sid = request.args.get('sid')
        Iname = request.args.get('In')
        start_time = request.args.get('st')
        regid = request.form['regid']
        lcheck = request.form["localCheck"]
        #print(classid)
        fdb = firebaseDB("", classid)
        ck=fdb.check(classid)
        if ck=="" or ck is None:
            return render_template('joinlink.html', msg_incorrect="Classes not running!")
        SID = ck
        sjoin = SQLConnect()
        client = sjoin._getClient_()
        cursor = sjoin._getCursor_()
        cursor.execute(f"SELECT * FROM register WHERE classid = '{classid}' AND regid = '{regid}';")
        account = cursor.fetchone()
        if account:
            name = account[1]
            sknet_id = account[4]

            cursor.close()
            client.close()
            if lcheck != "Active":
                return render_template('joinlink.html', msg_incorrect="Application isn't running on your device!")
            #if status:
            res = fdb.get_freq(SID)
            if res == "" or res is None:
                return render_template('join.html', msg_incorrect="Session is not running!")
            return redirect(f"http://127.0.0.1:5000/joinclass.html?freq={int(res)}&cid={classid}&cname={cname}&SID={SID}&Iname={Iname}&start_time={start_time}&name={name}&id={regid}&sknet_id={sknet_id}")
            #else:
            #    return render_template('join.html', msg_incorrect="Session Not Active!")
        elif not classid or not regid:
            msg = 'Please fill out the form!'
        else:
            msg = "Not enrolled for Class!"
    elif request.method == "POST":
        msg = 'Please fill out the form!'
    return render_template('joinlink.html', msg_incorrect=msg)

@app.route("/join.html", methods=["GET", "POST"])
def join():
    sjoin = SQLConnect()
    client = sjoin._getClient_()
    cursor = sjoin._getCursor_()
    msg = ''        
    if request.method == "POST" and "classid" in request.form and "regid" in request.form and "localCheck" in request.form:
        classid = request.form['classid']
        regid = request.form['regid']
        lcheck = request.form["localCheck"]
        
        fdb = firebaseDB("", classid)
        ck=fdb.check(classid)
        if ck=="" or ck is None:
            return render_template('join.html', msg_incorrect="Classes not running!")
        
        cursor.execute(f"SELECT * FROM register WHERE classid = '{classid}' AND regid = '{regid}';")
        account = cursor.fetchone()
        if account:
            name = account[1]
            sknet_id = account[4]

            cursor.execute(f"SELECT classes.class_name, login.name from classes JOIN login ON classes.email = login.email WHERE classes.class_id='{classid}';")
            data_1 = cursor.fetchone()

            cname = data_1[0]
            Iname = data_1[1]

            cursor.execute(f"SELECT sessionID, starttime FROM sessions;")
            data_2 = cursor.fetchall()
            found = 0
            SID = ck
            for i in data_2:
                if i[0][:6] == classid:
                    start_time = int(str(i[1])[11:-3].split(':')[0])*60 + int(str(i[1])[11:-3].split(':')[1])
                    fdb = firebaseDB(SID, SID[:6])
                    #status = fdb.get_status()
                    found = 1
            if found == 0:
                cursor.close()
                client.close()
                return render_template('join.html', msg_incorrect="Error while starting class!")

            cursor.close()
            client.close()
            if lcheck != "Active":
                return render_template('join.html', msg_incorrect="Application isn't running on your device!")
            #if status:
            res=fdb.get_freq(SID)
            if res=="" or res is None:
                return render_template('join.html', msg_incorrect="Session is not running!")
            #return redirect(url_for('joinclass', freq=int(res), cid=classid, cname=cname, SID=SID, Iname=Iname, start_time=start_time, name=name, id=regid, sknet_id=sknet_id))
            return redirect(f"http://127.0.0.1:5000/joinclass.html?freq={int(res)}&cid={classid}&cname={cname}&SID={SID}&Iname={Iname}&start_time={start_time}&name={name}&id={regid}&sknet_id={sknet_id}")
            #"http://127.0.0.1:9000/joinclass.html?freq={int(res)}&cid={classid}&cname={cname}&SID={SID}&Iname={Iname}&start_time={start_time}&name={name}&id={regid}&sknet_id={sknet_id}"
            #else:
            #    return render_template('join.html', msg_incorrect="Session Not Active!")
        elif not classid or not regid:
            msg = 'Please fill out the form!'
        else:
            msg = "Not enrolled for Class!"
    elif request.method == "POST":
        msg = 'Please fill out the form!'
    return render_template('join.html', msg_incorrect=msg)

@app.route("/status.html", methods=["GET"])
def status():
    response = jsonify({"result":"Active"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/joinclass.html", methods=["GET", "POST"])
def joinclass():
    #http://localhost:5000/joinclass.html?freq=10&cid=something1&cname=something2&SID=something3&Iname=something4
    #&start_time=30&name=something6&id=something7&sknet_id=AABI66B1DM-hay4iYmP32D4uQuXO3oJLD7n_BN46h65l6A
    cid = request.args.get('cid')
    freq = request.args.get('freq')
    cname = request.args.get('cname')
    SID = request.args.get('SID')
    Iname = request.args.get('Iname')
    start_time = request.args.get('start_time')
    name = request.args.get('name')
    id = request.args.get('id')
    sknet_id = request.args.get('sknet_id')

    if None in [cid, freq, cname, SID, Iname, start_time, name, id, sknet_id]:
        return render_template('join.html', msg_incorrect="Incorrect Joining Link!")
    else:
        return render_template('joinclass.html', cid=cid, freq=freq, cname=cname, SID=SID, Iname=Iname, start_time=start_time, name=name, id=id, sknet_id=sknet_id)
    #return redirect(f'http://localhost:5000/joinclass.html?freq={freq}&cid={cid}&cname={cname}&SID={SID}&Iname={Iname}&start_time={start_time}&name={name}&id={id}&sknet_id={sknet_id}')

@app.route("/home.html", methods=["GET", "POST"])
def home():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    return render_template('home.html', instructor_name=session['name'], instructor_email=session['email'])

@app.route('/create.html', methods=['GET', 'POST'])
def create():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    msg = ''
    s = SQLConnect()
    client = s._getClient_()
    cursor = s._getCursor_()

    if request.method == "POST" and "name" in request.form and "from_date" in request.form and "to_date" in request.form:
        className = request.form['name']
        fromDate = request.form['from_date']
        toDate = request.form['to_date']
        classID = genClassID()

        if not className or not fromDate or not toDate:
            msg = "Please fill out the form!"
        else:
            cursor.execute(f"""INSERT INTO classes (class_name, class_id, date_from, date_to, email) VALUES ('{className}', '{classID}', '{fromDate}', '{toDate}', '{session["email"]}');""")
            client.commit()
            cursor.close()
            client.close()
            return render_template('create.html', msg="Class Created Successfully!")
    elif request.method == "POST":
        msg = "Please fill out the form!"
    return render_template('create.html', instructor_name=session['name'], msg_incorrect=msg)

def genClassID():
    return "".join(choices(ascii_uppercase, k=6))

@app.route('/start.html', methods=['GET', 'POST'])
def start():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    msg = ''
    s = SQLConnect()
    client = s._getClient_()
    cursor = s._getCursor_()

    try:
        cursor.execute(f"""SELECT * from classes WHERE email = '{session["email"]}';""")
    except:
        return render_template('home.html', msg1="SQL Malfunction!")
    data = cursor.fetchall()
    
    newdata=[]
    for val in data:
        fdb = firebaseDB("", val[1])
        ch=fdb.check(val[1])
        xl=-1 if ch=="" or ch==None else fdb.get_freq(ch)
        if ch==None: ch=""
        newval=list(val)+[ch,xl]
        newdata+=[newval]
    del data

    cursor.close()
    client.close()
    return render_template('start.html', instructor_name=session['name'], TClasses=len(newdata), data=newdata)

def setSessionID(cid):
    return "_".join([cid, str(randint(10000, 99999))])

@app.route('/manage.html', methods=["GET"])
def manage():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    s = SQLConnect()
    client = s._getClient_()
    cursor = s._getCursor_()

    try:
        cursor.execute(f"SELECT class_name, class_id, date_from, date_to FROM classes WHERE email='{session['email']}';")
        data = cursor.fetchall()
    except:
        cursor.close()
        client.close()
        return render_template('index.html', msg1="You're Not Logged in!")

    lis = []
    for i in data:
        lis_2 = []
        lis_2.append(i[0])
        lis_2.append(i[1])
        cursor.execute(f"SELECT COUNT(regid) FROM register WHERE classid='{i[1]}';")
        lis_2.append(cursor.fetchone()[0])
        lis_2.append(i[2])
        lis_2.append(i[3])
        lis.append(lis_2)

    cursor.close()
    client.close()
    return render_template('manage.html', instructor_name=session['name'], TClasses=len(data), data=lis)

@app.route('/manageattendance.html', methods=["GET"])
def manageattendance():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    
    cname = request.args.get('cname')
    cid = request.args.get('cid')
    dfrom = request.args.get('stdate')
    dto = request.args.get('enddate')
    rst = request.args.get('sreg')
    
    fdb = firebaseDB("", cid)
    allStudents,mxattendance,stcount=fdb.get_class()
    s = SQLConnect()
    client = s._getClient_()
    cursor = s._getCursor_()
    
    try:
        cursor.execute(f"SELECT name, regId FROM register WHERE classId='{cid}';")
        data = cursor.fetchall()
    except:
        cursor.close()
        client.close()
        return render_template('manage.html', msg_incorrect="SQL Error, Try again later!")
    
    for i in data:
        if i[1] not in allStudents.keys():
            stcount+=1
            allStudents[i[1]]={"name":i[0], "present":0, "attendance":0}
    allStudents=dict(OrderedDict(sorted(allStudents.items(), key=lambda st: st[1]['attendance'])))
    
    return render_template('manageattendance.html', instructor_name=session['name'], cid=cid, cname=cname, dfrom=dfrom, dto=dto, rst=rst, data=allStudents, TStudents=len(allStudents), mxattendance=int(mxattendance/max(1,stcount)))

@app.route('/manageclass.html', methods=["GET"])
def manageclass():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    s = SQLConnect()
    client = s._getClient_()
    cursor = s._getCursor_()

    cname = request.args.get('cname')
    cid = request.args.get('cid')
    dfrom = request.args.get('stdate')
    dto = request.args.get('enddate')
    rst = request.args.get('sreg')

    if None in [cname, cid, dfrom, dto, rst]:
        return redirect(url_for('manage'))
    else:
        cursor.execute(f"SELECT sessionID, starttime, endtime FROM sessions;")
        data = cursor.fetchall()

        TClasses = len(data)
        fdb = firebaseDB("", cid)
        lis = []
        for i in data:
            lis_2 = []
            if i[0].split('_')[0] != cid:
                TClasses -= 1
                continue
            lis_2.append(i[0])
            lis_2.append(str(i[1]).split(' ')[0])
            lis_2.append(str(i[1]).split(' ')[1])
            if i[2] is not None:
                lis_2.append(str(i[2]).split(' ')[1])
            else:
                lis_2.append("NaN")
            lis_2.append(len(fdb.get_new(i[0])))
            lis.append(lis_2)
    cursor.close()
    client.close()
    # Incomplete
    return render_template('manageclass.html', instructor_name=session['name'], cname=cname, cid=cid, dfrom=dfrom, dto=dto, rst=rst, TClasses=TClasses, data=lis)

@app.route('/sessionInfo.html', methods=["GET", "POST"])
def sessionInfo():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    SID = request.args.get('SID')
    cname = request.args.get('cname')
    dfrom = request.args.get('dfrom')
    sttime = request.args.get('sttime')
    endtime = request.args.get('endtime')

    fdb = firebaseDB(SID, SID[:6])

    data, ttaken = fdb.get_all(), fdb.get_taken()
    TClasses = len(data)

    return render_template('sessionInfo.html', instructor_name=session['name'], SID=SID, cname=cname, dfrom=dfrom, sttime=sttime[:5], endtime=endtime[:5], TClasses=TClasses, data=data, ttaken=ttaken)

@app.route('/startsession.html', methods=['GET', 'POST'])
def startsession():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    cid = request.args.get('cid')
    cname = request.args.get('cname')
    freq=request.args.get('freq')

    s = SQLConnect()
    client = s._getClient_()
    cursor = s._getCursor_()

    SID = setSessionID(cid)

    fdb = firebaseDB(SID, SID[:6])
    prevSID = fdb.check(cid)

    if prevSID == "" or prevSID is None:
        tempTime = get('http://worldtimeapi.org/api/timezone/Asia/Kolkata').json()['datetime'][:19].replace('T', ' ')
        cursor.execute(f"INSERT INTO `sessions`(`sessionID`, `totalstudents`, `starttime`, `endtime`) VALUES ('{SID}', 0, '{tempTime}', NULL);")
        client.commit()

        fdb.init_session(int(freq))
        res=get("{0}/worker?sid={1}&cid={2}&freq={3}".format(_confJSON["API"]["path"], SID, cid, freq))
        if not res.json()["status"]:
            fdb.exit_session()
            return render_template('home.html', error="Server Busy, Try again later!")
    else:
        SID = prevSID

    cursor.execute(f"SELECT starttime FROM sessions WHERE sessionID='{SID}';")
    starttime = str(cursor.fetchone()[0])

    starttime = int(starttime.split(' ')[1].split(':')[0])*60 + int(starttime.split(' ')[1].split(':')[1])

    cursor.close()
    client.close()
    return render_template('startsession.html', instructor_name=session['name'], cid=cid, cname=cname, SID=SID, starttime=starttime, freq=freq)

'''
@app.route('/test', methods=["GET"])
def test():
    return render_template('home.html', error="Server Busy, Try again later!")
'''

@app.route('/getData.html', methods=["GET"])
def getData():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    SID = request.args.get('SID')

    fdb = firebaseDB(SID, SID[:6])
    return jsonify([fdb.get_all(), fdb.get_taken()])

@app.route('/exitsession.html', methods=['GET', 'POST'])
def exitsession():
    if not session:
        return render_template("index.html", msg1="Session Timed Out!")
    if not session["loggedin"]:
        return render_template('index.html', msg1="You're Not Logged in!")
    SID = request.args.get('SID')

    fdb = firebaseDB(SID, SID[:6])
    fdb.exit_session()

    s = SQLConnect()
    client = s._getClient_()
    cursor = s._getCursor_()

    cursor.execute(f"UPDATE sessions SET endtime='{get('http://worldtimeapi.org/api/timezone/Asia/Kolkata').json()['datetime'][:19].replace('T', ' ')}' WHERE sessionID='{SID}';")
    client.commit()

    cursor.close()
    client.close()
    return redirect(url_for('start'))

if __name__ == "__main__":
    app.run(debug=True,port=9000)
