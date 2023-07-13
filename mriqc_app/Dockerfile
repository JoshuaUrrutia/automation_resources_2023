FROM poldracklab/mriqc:0.15.1

COPY assets /tapis/assets
RUN chmod +x /tapis/assets/runner-template.sh

RUN apt-get update && \
    apt install unzip && \
    apt install zip 

ENTRYPOINT ["/tapis/assets/runner-template.sh"]
