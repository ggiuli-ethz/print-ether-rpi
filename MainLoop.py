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
from datetime import datetime


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
        self.port = port

        self.posts = []
        self.uid = uid
        self.db = firestore.client()

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
            printer = Serial(
            devfile=self.port,
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1.00,
            dsrdtr=True
            )

            printer.set(
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
            printer.text('\n')
            printer.textln('--------------------------------')

            printer.set(
                underline=1,
                font="b",
            )
            title_str = self.text_wrap(post['title'])
            date_str = self.format_date_stamp(post['date'])
            printer.textln(title_str)

            printer.set(
                underline=0,
                font="a",
                width=1,
                height=1,
            )
            printer.textln(date_str)

            printer.set(
                underline=0,
                width=2,
                height=2,
            )
            text_str = self.text_wrap(post['body'])
            printer.text('\n')
            printer.textln(text_str)

            printer.text('\n')
            self.print_image(post, printer)

            printer.textln('--------------------------------')
            printer.text('\n\n')

            self.__update_status(post['id'])
        except:
            self.__update_status(post['id'], failed=True)
        finally:
            printer.close()

    def execute(self):
        if (self.internet_connection()):
            self.__get_firestore_data()
            logger.info('Fetched new posts:')
            logger.info(self.posts)
            for post in self.posts:
                self.print_post(post)
        else:
            logger.warning('No connection, pause')
            
    def print_image(self, post, printer):
        if not post['drawing']:
            return
        
        image: Image = import_to_pil(post['drawing'])
        printer.image(image, impl="bitImageColumn")

    def internet_connection(self):
        try:
            requests.get("https://google.com", timeout=15)
            return True
        except requests.ConnectionError:
            return False    
        
    def text_wrap(self, text, max_length = 32):

        words = text.split()
        lines = []
        current_line = ""
    
        for word in words:

            if len(current_line) + len(word) + (1 if current_line else 0) > max_length:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
    
        if current_line:
            lines.append(current_line)
    
        return "\n".join(lines)


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

    def format_date_stamp(self, date_str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        return date_obj.strftime('%M:%H %d/%m/%Y')

