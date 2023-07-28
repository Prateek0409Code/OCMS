import pyrebase
import json

class firebaseDB:
    def __init__(self,SID,json_loc="./configuration/db.json"):
        with open(json_loc) as f:
            config = json.load(f)
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()
        self.SID=SID

    def init_session(self):
        data = {"status": 1, "attendees": {}}
        self.db.child(self.SID).set(data)

    def join(self,sid,name):
        self.db.child(self.SID).child("attendees").child(sid).child("taken").set(0)
        self.db.child(self.SID).child("attendees").child(sid).child("present").set(0)
        self.db.child(self.SID).child("attendees").child(sid).child("name").set(name)

    def get_att(self , sid):
        taken = self.db.child(self.SID).child("attendees").child(sid).child("taken").get()
        present = self.db.child(self.SID).child("attendees").child(sid).child("present").get()
        return taken.val(),present.val()

    def set_att(self,sid,present1,taken1):
        self.db.child(self.SID).child("attendees").child(sid).child("taken").set(taken1)
        self.db.child(self.SID).child("attendees").child(sid).child("present").set(present1)

    def get_all(self):
        all_users = self.db.child(self.SID).child('attendees').get()
        lis1=[]
        try:
            for user in all_users.each():
                lis2={}
                lis2['sid']=(user.key())
                lis2['name']=(user.val()['name'])
                lis2['taken']=(user.val()['taken'])
                lis2['present']=(user.val()['present'])
                lis1.append(lis2)
        except:
            pass
        return lis1

    def get_new(self, SID):
        all_users = self.db.child(SID).child('attendees').get()
        lis1=[]
        try:
            for user in all_users.each():
                lis2={}
                lis2['sid']=(user.key())
                lis2['name']=(user.val()['name'])
                lis2['taken']=(user.val()['taken'])
                lis2['present']=(user.val()['present'])
                lis1.append(lis2)
        except:
            pass
        return lis1

    def get_status(self):
        return self.db.child(self.SID).child("status").get().val()

    def check(self, cid):
        for id in self.db.get().val():
            if id.split('_')[0] == cid:
                if self.db.child(id).child("status").get().val():
                    return id
        return ""

    def exit_session(self):
        self.db.child(self.SID).child("status").set(0)

with open('configuration/db.json') as f:
    config = json.load(f)

# firebase = pyrebase.initialize_app(config)
# db=firebase.database()
#
# SID="abc123"
# # #---------initiate
# data={"status":0,"attendees":{}}
# db.child(SID).set(data)
#
# sid="2018acsc"
#
# #-------add student regid(sid)
# #db.child(SID).child("attendees").set(sid)
#
# #-------add student attendance
# #att={"taken":2,"present":1}
# #db.child(SID).child("attendees").child(sid).set(att)
#
# #--------fetch attendance and update
# # taken = db.child(SID).child("attendees").child(sid).child("taken").get()
# # present = db.child(SID).child("attendees").child(sid).child("present").get()
# # live_att=1
# # t=taken.val()
# # p=present.val()
# # print("taken: {} , present: {}".format(t,p))
# # db.child(SID).child("attendees").child(sid).child("taken").set(t+1)
# # db.child(SID).child("attendees").child(sid).child("present").set(p+live_att)
#
# # st_data={}
# # st_child=db.child(SID).child('attendees')
# # #print(f"taken: {st_child.child(sid).child('taken').get().val()} times,")
# # for x in st_child.get().val():
# #     print(x+" ,")
# #     print(f"taken: {st_child.child(x).child('taken').get().val()} times,")
# #     print(f"detected: {st_child.child(x).child('present').get().val()} times")
#

f1=firebaseDB("class1")
f1.init_session()
sid="2020acsc"
f1.join(sid,"ankit")
# f1.set_att(sid,3,4)
#f1.init_session()
#f1.get_all()
