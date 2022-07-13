FROM python
WORKDIR /app
COPY . /app
ENV export PIP_DEFAULT_TIMEOUT=1000
RUN pip install -r /app/req.txt
EXPOSE 8222
CMD python3 manage.py runserver 0.0.0.0:8222