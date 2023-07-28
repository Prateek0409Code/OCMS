import pyrebase
import json

class firebaseDB:
    def __init__(self,SID,CID,json_loc="./config/db.json"):
        with open(json_loc) as f:
            config = json.load(f)
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()
        self.SID=SID
        self.CID=CID

    def init_session(self):
        data = {"status": 1, "attendees": {}, "ttaken": 0}
        self.db.child(self.CID).child("active").set(self.SID)
        self.db.child(self.CID).child(self.SID).set(data)

    def join(self,sid,name):
        self.db.child(self.CID).child(self.SID).child("attendees").child(sid).child("taken").set(0)
        self.db.child(self.CID).child(self.SID).child("attendees").child(sid).child("present").set(0)
        self.db.child(self.CID).child(self.SID).child("attendees").child(sid).child("name").set(name)

    def get_att(self , sid):
        taken = self.db.child(self.CID).child(self.SID).child("attendees").child(sid).child("taken").get()
        present = self.db.child(self.CID).child(self.SID).child("attendees").child(sid).child("present").get()
        return taken.val(),present.val()

    def set_att(self,sid,present1,taken1):
        self.db.child(self.CID).child(self.SID).child("attendees").child(sid).child("taken").set(taken1)
        self.db.child(self.CID).child(self.SID).child("attendees").child(sid).child("present").set(present1)

    def get_all(self):
        all_users = self.db.child(self.CID).child(self.SID).child('attendees').get()
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
        all_users = self.db.child(self.CID).child(SID).child('attendees').get()
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

    def get_class(self, CID):
        sessionnames=self.db.child(self.CID).get().val()
        ubase={}
        mxattendance=0
        stcount=0
        try:
            for sess in sessionnames.keys():
                tp=self.db.child(self.CID).child(sess).child('attendees').get().val()
                for users in tp.keys():
                    if users not in ubase:
                        ubase[users]={"name":tp[users]['name'], "present":tp[users]['present'], "taken":tp[users]['taken']}
                    else:
                        ubase[users]["present"]+=tp[users]['present']
                        ubase[users]["taken"]+=tp[users]['taken']
            
            for val in ubase.keys():
                stcount+=1
                tpval=float("{0:.2f}".format((ubase[val]["present"]/ubase[val]["taken"])*100))
                ubase[val]["attendance"]=tpval
                mxattendance+=tpval
        except:
            pass
        return ubase, mxattendance, stcount

    def update_taken(self, tt):
        self.db.child(self.CID).child(self.SID).child("ttaken").set(tt)

    def get_taken(self):
        return self.db.child(self.CID).child(self.SID).child("ttaken").get().val()

    def get_status(self):
        return self.db.child(self.CID).child(self.SID).child("status").get().val()

    def check(self, cid):
        return self.db.child(self.CID).child("active").get().val()

    def exit_session(self):
        self.db.child(self.CID).child(self.SID).child("status").set(0)
        self.db.child(self.CID).child("active").set("")
