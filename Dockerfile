FROM python:3.8.5

EXPOSE "8000"

WORKDIR code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "manage.py"]

CMD ["runserver", "0.0.0.0:8000"]
