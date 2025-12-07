FROM node:alpine AS build

COPY ./package.json \
    ./package-lock.json \
    ./tsconfig.json \
    ./tsconfig.app.json \
    ./tsconfig.node.json \
    ./vite.config.ts \
    ./eslint.config.js \
    /app/

COPY ./src/frontend /app/src/frontend

WORKDIR /app
RUN --mount=type=cache,target=/root/.npm \
    npm install .
RUN npm run build

FROM nginxinc/nginx-unprivileged
USER root

# Clean default nginx html folder (run as root to avoid permission errors)
RUN rm -rf /usr/share/nginx/html/*

# Copy built files into nginx and fix ownership for the unprivileged nginx user
COPY --from=build /app/src/frontend/dist /usr/share/nginx/html
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
# RUN chown -R nginx:nginx /usr/share/nginx/html

# Switch back to the unprivileged nginx user provided by the base image
USER nginx

EXPOSE 80
CMD nginx -g "daemon off;"
