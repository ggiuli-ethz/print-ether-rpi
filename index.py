import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("screds/key.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def update_status_to_printed(document_id):
    try:
        # Reference to the Firestore document (replace 'your-collection-name' with your actual collection name)
        doc_ref = db.collection('prints').document(document_id)
        
        # Update the status field to 'bobob'
        doc_ref.update({
            'status': 'printed'
        })
        
        print(f"Status updated to 'printed' for document with ID: {document_id}")
    
    except Exception as e:
        print(f"Error updating status: {e}")

# Function to retrieve data from Firestore
def get_firestore_data():
    try:
        # Reference to the Firestore collection
        collection_ref = db.collection('prints')
        docs = collection_ref.order_by('createdAt').stream()

        # Iterate through documents and print them
        for doc in docs:
            print(f"Document ID: {doc.id}")
            print(f"Document Data: {doc.to_dict()}")
            update_status_to_printed(doc.id)
    
    except Exception as e:
        print(f"Error fetching data: {e}")

# Call the function to get data
get_firestore_data()
