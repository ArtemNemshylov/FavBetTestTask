FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Dependencies instalation
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y supervisor && \
    mkdir -p /var/log/supervisor

# Streamlit configuration
RUN mkdir -p /root/.streamlit && \
    echo "[server]\nheadless = true\nenableCORS = false\nport = 8501" > /root/.streamlit/config.toml

# Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 8501

CMD ["/usr/bin/supervisord", "-n"]
