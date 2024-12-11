import firebase_admin
from firebase_admin import credentials, firestore
import requests
from escpos.printer import Serial

class ExecLoop:

    def __init__(self, uid, port):
        cred = credentials.Certificate("screds/key.json")
        self.app = firebase_admin.initialize_app(cred)

        self.posts = []
        self.uid = uid
        self.db = firestore.client()

        self.printer = Serial(
            devfile=port,
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1.00,
            dsrdtr=True
        )

    def __update_status_to_printed(self, document_id):
        doc_ref = self.db.collection(self.uid).document(document_id)
        
        doc_ref.update({
            'status': 'printed'
        })
        
        print(f"Status updated to 'printed' for document with ID: {document_id}")


    def __get_firestore_data(self):
        collection_ref = self.db.collection(self.uid)
        self.posts = collection_ref.where('status', '==', 'queued').order_by('date').stream()

        for doc in self.posts:
            print(f"Document ID: {doc.id}")
            print(f"Document Data: {doc.to_dict()}")


    def execute(self):
        if (self.internet_connection()):
            self.__get_firestore_data()
        else:
            print('No connection, pause')

    def internet_connection(self):
        try:
            requests.get("https://google.com", timeout=15)
            return True
        except requests.ConnectionError:
            return False    
        
    def __del__(self):
        print('Deleted App')
        try:
            firebase_admin.delete_app(self.app)
        except:
            pass

        try:
            self.printer.close()
        except:
            pass

