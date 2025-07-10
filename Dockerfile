FROM python:3.12-slim
RUN pip install uv
WORKDIR /src
COPY . .
RUN uv pip sync --system requirements.lock
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]