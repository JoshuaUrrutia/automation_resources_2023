FROM python:3.8

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install wget -y \
    && apt-get install zip -y \
    && apt-get install default-jre -y

RUN wget https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.9.zip \
    && unzip fastqc_v0.11.9.zip \
    && rm fastqc_v0.11.9.zip \
    && chmod +x FastQC/fastqc

ENV PATH "/FastQC/:$PATH"
#CMD [ "fastqc" ]
ENTRYPOINT [ "/FastQC/fastqc" ]
