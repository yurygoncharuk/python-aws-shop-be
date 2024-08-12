FROM python:3.12-alpine
WORKDIR /opt/app
COPY requirements.txt /opt/app/
RUN pip install -r requirements.txt --break-system-packages
COPY .env app.py /opt/app/
EXPOSE 3000
CMD [ "python3", "app.py" ]