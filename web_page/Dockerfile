FROM node:16-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the app if it's a production build
RUN npm run build

# Expose the port that web server will run on
EXPOSE 3000

# Command to run the web application
CMD ["npm", "start"]
