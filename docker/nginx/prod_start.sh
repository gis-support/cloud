curl https://${APP_PROD_HOST_URL}/api/docs/api.json -o /cloud/src/docs/api.json && \
cd /cloud && \
npm i && \
npm run build && \
envsubst '$$CONTAINER_BASENAME $$APP_PROD_API_PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf && \
echo 'Cloud application ready to use' && \
nginx -g 'daemon off;'