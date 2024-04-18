import asyncio
import json
import sys

import mariadb


class db_connector:
     def __init__(self, host:str="localhost", port:int=3306, user:str="root", database:str="dev") -> None:
          try:
               self.conn = mariadb.connect(
                    host=host,
                    port=port,
                    user=user,
                    database=database
               )
               self.cur = self.conn.cursor()
          except mariadb.Error as e:
               print(f"An error has occurred while connecting to the database!\n-> {e}")
               sys.exit(1)
     
     #* Search for modlogs on a user, by user id
     async def get_logs(self, user_id: int):
          #* Initialize the dict used to return the data
          #* Below is the structure of the dictionary
          # log_info = {
          #      "<cid>": {
          #           "uid": int,
          #           "type": str,
          #           "reason": str,
          #           "mod_id": int
          #      }
          # }
          log_info = {}
               
          #* Select all columns inside the table
          self.cur.execute("SELECT * FROM usr_logs")
          
          #* Loop around all the information
          for (cid, uid, typ, reason, mod_id) in self.cur:
               #* If the user id is equal to the user id passed in,
               #* Add it to the dict
               if uid == user_id:
                    log_info[cid] = {
                         "uid": uid,
                         "type": typ,
                         "reason": reason,
                         "mod_id": mod_id
                    }
          
          #* If the given user id didn't have any logged punishments,
          #* Return None
          if not log_info:
               return None
          #* Return the user's logs         
          return log_info
     
     #* Add logs to a user
     async def add_logs(self, uid: int, type: str, reason: str, mod_id: int):
          try:
               self.cur.execute("INSERT INTO usr_logs(uid, type, reason, mod_id) VALUES (?, ?, ?, ?)",
                                (uid, type, reason, mod_id))
               self.conn.commit()
               
               return True
          except mariadb.Error as e:
               print(f"There was an error while inserting a user log: {e}")
               return False

     #* Get a specific case's details, by case id
     async def get_case(self, case_id: int):
          #* Initialize the dict used to return the data
          #* Below is the structure of the dictionary
          # log_info = {
          #      "<cid>": {
          #           "uid": int,
          #           "type": str,
          #           "reason": str,
          #           "mod_id": int
          #      }
          # }
          log_info = {}
               
          #* Select all columns inside the table
          try:
               self.cur.execute("SELECT * FROM usr_logs")
          except mariadb.Error as e:
               print(f"There was an error while getting a user log: {e}")
               return False
          
          print(self.cur)
          #* Loop around all the information
          for (cid, uid, typ, reason, mod_id) in self.cur:
               #* If the case id is equal to the case id passed in,
               #* Add it to the dict
               if cid == case_id:
                    log_info[cid] = {
                         "uid": uid,
                         "type": typ,
                         "reason": reason,
                         "mod_id": mod_id
                    }
                    break
          
          #* If the given user id didn't have any logged punishments,
          #* Return None
          if not log_info:
               return None
          #* Return the user's logs         
          return log_info
     
     async def close_conn(self):
          self.conn.close()
          
if __name__ == "__main__":
     db = db_connector()
     data = asyncio.run(db.add_logs(uid=1050334563840315424, type="Warn", reason="Test"))
     print(data)
     asyncio.run(db.close_conn())