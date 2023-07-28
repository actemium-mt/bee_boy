FROM python:3.8.10
WORKDIR /app
COPY ./ /app
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 8501
ENTRYPOINT ["streamlit", "run"]
CMD ["bee_boy.py"]
