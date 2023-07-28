import pyrebase
import json

class firebaseDB:
    def __init__(self,SID,CID,json_loc="./configuration/db.json"):
        with open(json_loc) as f:
            config = json.load(f)
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()
        self.SID=SID
        self.CID=CID

    def init_session(self,freq):
        data = {"status": 1, "attendees": {}, "ttaken": 0 , "freq": freq}
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

    def get_taken(self):
        return self.db.child(self.CID).child(self.SID).child("ttaken").get().val()

    def get_all(self):
        all_users = self.db.child(self.CID).child(self.SID).child('attendees').get()
        lis1=[]
        try:
            for user in all_users.each():
                lis2={}
                lis2['sid']=(user.key())
                lis2['name']=(user.val()['name'])
                lis2['taken']=(user.val()['taken'])
                if 'sus' in user.val():
                    lis2['sus']=(user.val()['sus'])
                else:
                    lis2['sus']=(0)
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

    def get_class(self):
        sessionnames=self.db.child(self.CID).get().val()
        ubase={}
        mxattendance=0
        stcount=0
        try:
            for sess in sessionnames.keys():
                if sess=="active":
                    continue
                stcount+=1
                tp=self.db.child(self.CID).child(sess).child('attendees').get().val()
                for users in tp.keys():
                    if users not in ubase:
                        ubase[users]={"name":tp[users]["name"],"present":1}
                    else:
                        ubase[users]["present"]+=1
            '''
            for sess in sessionnames.keys():
                if sess=="active":
                    continue
                ttaken=self.db.child(self.CID).child(sess).child("ttaken").get().val()
                tp=self.db.child(self.CID).child(sess).child('attendees').get().val()
                if tp is None: continue
                for users in tp.keys():
                    if users not in ubase:
                        ubase[users]={"name":tp[users]['name'], "present":tp[users]['present'], "taken":ttaken}
                    else:
                        ubase[users]["present"]+=tp[users]['present']
            '''
            for val in ubase.keys():
                tpval=float("{0:.2f}".format((ubase[val]["present"]/stcount)*100))
                ubase[val]["attendance"]=tpval
                mxattendance+=tpval
        except Exception as ex:
            print(ex)
            pass
        return ubase, mxattendance, stcount

    def get_status(self):
        return self.db.child(self.CID).child(self.SID).child("status").get().val()

    def get_freq(self, sid):
        return self.db.child(self.CID).child(sid).child("freq").get().val()

    def check(self, cid):
        return self.db.child(self.CID).child("active").get().val()
        '''
        for id in self.db.child(self.SID).get().val():
            if id.split('_')[0] == cid:
                if self.db.child(self.CID).child(id).child("status").get().val():
                    return id
        return ""
        '''

    def exit_session(self):
        self.db.child(self.CID).child(self.SID).child("status").set(0)
        self.db.child(self.CID).child("active").set("")

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

#f1=firebaseDB("class1")
#f1.init_session()
#sid="2020acsc"
#f1.join(sid,"ankit")
# f1.set_att(sid,3,4)
#f1.init_session()
#f1.get_all()
