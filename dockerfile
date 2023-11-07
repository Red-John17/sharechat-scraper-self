# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Chrome, xvfb, and other dependencies for running a GUI
RUN apt-get update && apt-get install -y wget gnupg2 xvfb \
    && wget -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install

# Skip installing ChromeDriver because we'll use chromedriver_autoinstaller in our script

# Install Python dependencies (make sure you have a requirements.txt with selenium and chromedriver_autoinstaller)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Ensure that the main.py configures Selenium to run Chrome in non-headless mode
# You can do this by setting the `headless` option to `False` when configuring the WebDriver.

# Use xvfb-run to start a virtual display and then execute the main.py script
# RUN google-chrome --version
CMD xvfb-run --auto-servernum --server-num=1 python ./main.py > /usr/src/app/script.log 2>&1


# CMD ["xvfb-run", "--auto-servernum", "--server-num=1", "python", "./main.py"]
# CMD ["python", "./main.py"]


