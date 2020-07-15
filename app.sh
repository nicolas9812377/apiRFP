apt update && apt install libglib2.0-0 -y
gunicorn --bind=0.0.0.0 --timeout 600 aplication:app
