from main_loop import ExecLoop
from time import sleep

ml = None

while True:
    try:
        if ml is None:
            ml = ExecLoop('eA5d03H8VigkQ8sJXjoIZrBu3nu1', '/dev/serial0')
        ml.execute()
    except Exception as error:
        print(error)
        ml = None
        sleep(60)

    sleep(30)