FROM continuumio/miniconda3

RUN mkdir /app
WORKDIR /app
# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
RUN echo "conda activate aviation" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

# The code to run when container is started:
COPY . /app/
WORKDIR /app

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]