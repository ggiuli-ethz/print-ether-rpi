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

    def __update_status(self, document_id, failed=False):
        doc_ref = self.db.collection(self.uid).document(document_id)
        
        doc_ref.update({
            'status': 'printed' if not failed else 'error'
        })
        
        print(f"Status updated to {'printed' if not failed else 'error'} for document with ID: {document_id}")


    def __get_firestore_data(self):
        collection_ref = self.db.collection(self.uid)
        docs = collection_ref.where('status', '==', 'queued').order_by('date').stream()

        self.posts = [{'id': doc.id, **doc.to_dict()} for doc in docs]

    def print_post(self, post):
        try:
            self.printer.text(post['title'])
            self.__update_status(post['id'])
        except:
            self.__update_status(post['id'], failed=True)


    def execute(self):
        if (self.internet_connection()):
            self.__get_firestore_data()
            print(self.posts)
            for post in self.posts:
                self.print_post(post)
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

