FROM nginx:alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy health check script
COPY health_check.sh /health_check.sh
RUN chmod +x /health_check.sh

# Remove default nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Create directory for static files
RUN mkdir -p /usr/share/nginx/html/

# Copy HTML files
COPY html/ /usr/share/nginx/html/

EXPOSE 8080

CMD [ "nginx", "-g", "daemon off;" ]