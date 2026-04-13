FROM node:20-alpine

WORKDIR /app

# Install Expo CLI globally
RUN npm install -g expo-cli

# Install dependencies first (layer cache)
COPY package.json ./
RUN npm install

# Copy source
COPY . .

EXPOSE 8081 19000 19001

# Start Metro bundler
CMD ["npx", "expo", "start", "--host", "0.0.0.0", "--port", "8081"]
