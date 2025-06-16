import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import datetime
from dotenv import load_dotenv

load_dotenv()


# Path to your service account key file you downloaded
# Make sure this path is correct!
cred = credentials.Certificate(firebase_admin_config)

# Initialize the app with the service account, and specify your database URL
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://chat-bot-1db9a-default-rtdb.firebaseio.com'
})

print("Firebase Admin SDK initialized successfully!")

ref=db.reference('/')
clients_ref=ref.child('Clients')
def store_data(basic_data,detail_data,client_id):
    if not client_id:
        client_ref = clients_ref.push()
        client_ref.set(basic_data)
      
        client_id = client_ref.key
    else:
        # Optional: update existing basic info
        clients_ref.child(client_id).update(basic_data)
        
    
    now = datetime.datetime.now()
    year = str(now.year)
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"

    new_client_ref = clients_ref.child(client_id).child("daily_usage").child(year).child(month).child(day)

    new_client_ref.set(detail_data)
    return client_id

def retrieve_data(client_id):
    return clients_ref.child(client_id).get()
