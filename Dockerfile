# set python3 base image
FROM python:3.9-slim

# label
LABEL Olga Lalakulich "olalakul@gmail.com"

# install curl
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# --no-install-recommends
RUN apt-get  update && apt-get install  -y curl &&  apt-get clean && rm -rf /var/lib/apt/lists/*

# embed Trivy for Security scan
# MicroScanner is now deprecated in favour of Trivy - as it written at the https://github.com/aquasecurity/microscanner
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/master/contrib/install.sh | sh -s -- -b /usr/local/bin \
    && trivy filesystem --ignore-unfixed --exit-code 1 --severity HIGH,CRITICAL --no-progress /

# working directory in the container
WORKDIR /get-movie-info

# copy the files to the working directory
#COPY run_flask_metadaten.py .
#COPY app_info_about_movies/ .
COPY . .

# install dependencies
RUN python3 -m pip install -r app_info_about_movies/requirements.txt

# expose HTTP ports
EXPOSE 5000

RUN groupadd -r user && useradd -r -g user user

USER user

# command to run on container start
CMD ["python3",  "run_flask_metadaten.py"]

