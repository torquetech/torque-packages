FROM node:18.0.0 AS build

WORKDIR /app
COPY . /app/

RUN npm install
RUN npm run build

FROM node:18.0.0

EXPOSE 8080
WORKDIR /app
CMD ["node", "./index.html"]

COPY --from=build /app/build/ /app/
COPY package.json /app

RUN npm install -only=production
