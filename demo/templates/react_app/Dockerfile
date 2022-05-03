FROM node:18.0.0 AS build

WORKDIR /app
COPY . /app/

RUN npm install
RUN npm run build

FROM nginx:stable

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

COPY --from=build /app/build/ /usr/share/nginx/html
