FROM node:23-slim

WORKDIR /app

COPY dataset /app/dataset
COPY model /app/model/taxadvisordb_v2-0

CMD ["bash"] 
