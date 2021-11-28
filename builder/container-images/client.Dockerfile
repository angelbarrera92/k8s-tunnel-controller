FROM docker.io/library/node:lts

# TODO. The localtunnel version should be gathered from another place
RUN npm install -g localtunnel@2.0.2
