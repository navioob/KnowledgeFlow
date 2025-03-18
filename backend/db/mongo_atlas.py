import bcrypt
from datetime import datetime
from bson import ObjectId
from pytz import timezone
from pymongo.mongo_client import MongoClient


class AtlasClient:
    def __init__(self, altas_uri, dbname):
        self.mongodb_client = MongoClient(altas_uri)
        self.database = self.mongodb_client[dbname]
        self.users_credentials = self.database.users_credentials
        self.users_documents = self.database.users_documents

    ## A quick way to test if we can connect to Atlas instance
    def ping(self):
        self.mongodb_client.admin.command("ping")

    def find(self, collection_name, filter={}, limit=0):
        collection = self.database[collection_name]
        items = list(collection.find(filter=filter, limit=limit))
        return items
    
    def delete_document(self, user_id, document_id):
        delete_query = {"user_id":user_id, "_id":ObjectId(document_id)}
        try:
            self.users_documents.delete_one(delete_query)
            return {"success":True}
        except Exception as error:
            return {"success":False}

    
    def get_user_details(self, user_id):
        user_details = self.users_credentials.find_one({"_id": ObjectId(user_id)})
        if user_details is None:
            return None
        else:
            return user_details

    def create_user(self, username, first_name, last_name, password):
        if self.users_credentials.find_one({"username": username}) is None:
            # converting password to array of bytes
            password_bytes = password.encode("utf-8")

            # generating the salt
            salt = bcrypt.gensalt()

            # Hashing the password
            hashed_password = bcrypt.hashpw(password_bytes, salt)

            user_credential = {
                "username": username,
                "password": hashed_password,
                "first_name": first_name,
                "last_name": last_name,
                "ts": datetime.now(timezone('Asia/Kuala_Lumpur')).timestamp(),
            }

            self.users_credentials.insert_one(user_credential)

            # return user details
            user_details = self.users_credentials.find_one(
                {
                    "username": username,
                    "password": hashed_password,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            )

            return {"success": True, "user_id": str(user_details.get('_id'))}
        else:
            return {"success": False, "user_id": None}

    def authenticate_user(self, username, password):
        print(self.users_credentials.find_one({"username": username}) is None)
        if self.users_credentials.find_one({"username": username}) is None:
            return {"success": False, "message": "Username/Password is invalid."}
        else:
            user_credential = self.users_credentials.find_one({"username": username})

            password_entered = password.encode("utf-8")

            # checking password
            result = bcrypt.checkpw(password_entered, user_credential["password"])

            print(str(user_credential['_id']))

            if result:
                return {"success": True, "message": "Password Matched.","user_id": str(user_credential['_id'])}

            else:
                return {"success": False, "message": "Username/Password is invalid.", "user_id": None }
            
    def upload_document(self, user_id, document_title, document_summary):
         
            document_details = {
                    "user_id" : user_id,
                    "document_title": document_title,
                    "document_summary": document_summary,
                    "ts": datetime.now(timezone('Asia/Kuala_Lumpur')).timestamp(),
                }

            insert_process = self.users_documents.insert_one(document_details)

            return insert_process.inserted_id
    
    def get_documents(self, user_id):
            
            cursor = self.users_documents.find({"user_id": user_id})

            try:
                list_of_documents = [{
                    'document_id': str(document['_id']),
                    'user_id':str(document['user_id']),
                    'document_title': document['document_title'],
                    'document_summary': document['document_summary'],
                    'ts': document['ts'],
                } for document in cursor]
            except Exception as error:
                list_of_documents = []

            return list_of_documents

