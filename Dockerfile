FROM python:3.10

# Copy requirements files
COPY requirements.txt /AutoReddit_v2.0.1/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r /AutoReddit_v2.0.1/requirements.txt

# Install CLI packages
RUN apt-get -y update
RUN apt-get update \
    && apt-get install -qq -y build-essential xvfb xdg-utils wget ffmpeg libpq-dev vim curl libmagick++-dev fonts-liberation sox bc --no-install-recommends\
    && apt-get clean

## ImageMagicK Installation ##
RUN mkdir -p /tmp/distr && \
    cd /tmp/distr && \
    wget https://download.imagemagick.org/ImageMagick/download/releases/ImageMagick-7.0.11-2.tar.xz && \
    tar xvf ImageMagick-7.0.11-2.tar.xz && \
    cd ImageMagick-7.0.11-2 && \
    ./configure --enable-shared=yes --disable-static --without-perl && \
    make && \
    make install && \
    ldconfig /usr/local/lib && \
    cd /tmp && \
    rm -rf distr

# Create a policy file for ImageMagick to be able to write files
COPY policy.xml /etc/ImageMagick-6/policy.xml

# Set working directory
WORKDIR /AutoReddit_v2.0.1

# Copy application code
COPY . /AutoReddit_v2.0.1

# Set command
CMD ["python3", "-u", "main.py"]