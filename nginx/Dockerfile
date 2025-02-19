FROM nginx:1.22.1
COPY nginx/nginx.conf /etc/nginx/templates/default.conf.template
COPY frontend/build /usr/share/nginx/html
COPY docs /usr/share/nginx/html/docs
