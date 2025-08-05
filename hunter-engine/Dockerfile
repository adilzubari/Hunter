FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y xvfb && \
    pip install --no-cache-dir -r requirements.txt

# Set environment variable for display
ENV DISPLAY=:99

# Start Xvfb manually and run script with unbuffered output
CMD bash -c "Xvfb :99 -screen 0 1024x768x24 & python -u aapl_scraper.py"



# Ensure we use xvfb-run to create a fake display
# CMD ["xvfb-run", "python", "aapl_scraper.py"]
# CMD ["xvfb-run", "-a", "-e", "/dev/stdout", "python", "-u", "aapl_scraper.py"]
# CMD ["python", "aapl_scraper.py"]

