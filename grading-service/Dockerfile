# -------------------------------------------------------------------
# Stage 1: Builder
# -------------------------------------------------------------------
# 改用 alpine 版本，它是最輕量且權限最單純的
FROM python:3.11-alpine as builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安裝編譯工具 (alpine 需要 build-base 來編譯某些 python 套件)
RUN apk add --no-cache build-base

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------------
# Stage 2: Final
# -------------------------------------------------------------------
FROM python:3.11-alpine

WORKDIR /app

# 從 builder 複製環境
COPY --from=builder /opt/venv /opt/venv

COPY . .

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]