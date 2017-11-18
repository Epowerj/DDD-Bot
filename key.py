import os

#this is in a seperate file to prevent accidental commits that contain api keys
#you can replace the environment variable calls with normal strings
apikey = str(os.environ["DDDKEY"])
admin_id = int(os.environ["DDDADMIN"])
chatroom_id = int(os.environ["DDDCHAT"])

table_name = str(os.environ.get("APPNAME")).replace("-", "")
