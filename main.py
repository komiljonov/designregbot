import threading
import os
import sys

def main():
    
    site = threading.Thread(target=os.system, args=("python manage.py runserver 0.0.0.0:8000",))
    bot = threading.Thread(target=os.system, args=("python manage.py bot",))
    site.start()
    bot.start()
    while True:
        pass

main()
