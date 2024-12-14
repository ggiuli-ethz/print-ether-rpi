import firebase_admin
import logging
from firebase_admin import credentials, firestore
import requests
from escpos.printer import Serial
from PIL import Image
import re
import base64
from io import BytesIO
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt="%(asctime)s %(name)s.%(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

def import_to_pil(data):
    image_data = re.sub('^data:image/.+;base64,', '', data)
    return  Image.open(BytesIO(base64.b64decode(image_data)))

class ExecLoop:

    def __init__(self, uid, port):
        cred = credentials.Certificate("screds/key.json")
        logger.info('Starting application')
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
        
        logger.info(f"Status updated to {'printed' if not failed else 'error'} for document with ID: {document_id}")


    def __get_firestore_data(self):
        collection_ref = self.db.collection(self.uid)
        docs = collection_ref.where('status', '==', 'queued').order_by('date').stream()

        self.posts = [{'id': doc.id, **doc.to_dict()} for doc in docs]

    def print_post(self, post):
        try:
            self.printer.set(
                underline=0,
                align="left",
                font="a",
                width=2,
                height=2,
                density=3,
                invert=0,
                smooth=False,
                flip=False,
            )
            self.printer.text(post['title'])
            self.print_image(post)
            self.__update_status(post['id'])
        except:
            self.__update_status(post['id'], failed=True)


    def execute(self):
        if (self.internet_connection()):
            self.__get_firestore_data()
            logger.info('Fetched new posts:')
            logger.info(self.posts)
            for post in self.posts:
                self.print_post(post)
        else:
            logger.warning('No connection, pause')
            
    def print_image(self, post):
        if not post['drawing']:
            return
        
        image: Image = import_to_pil(post['drawing'])
        self.printer.image(image, impl="bitImageColumn")

    def internet_connection(self):
        try:
            requests.get("https://google.com", timeout=15)
            return True
        except requests.ConnectionError:
            return False    
        
    def __del__(self):
        logger.info('Deleted App')
        try:
            firebase_admin.delete_app(self.app)
        except:
            pass

        try:
            self.printer.close()
        except:
            pass

