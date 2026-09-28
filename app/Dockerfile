FROM python:3.12-slim
WORKDIR /app
COPY src/app.py .
EXPOSE 8080
USER 65532:65532
ENTRYPOINT ["python", "-u", "app.py"]
