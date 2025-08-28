# Use Node.js as the base image
FROM node:18

# Set the working directory
WORKDIR /app

# Install Hardhat globally
RUN npm install -g hardhat

# Copy package files and install dependencies
COPY package.json ./
RUN npm install

# Copy the entire Hardhat project (including hardhat.config.js)
COPY . .

# Compile the smart contracts
RUN npx hardhat compile

# Expose Hardhat's default network port
EXPOSE 8545

# Start the Hardhat network and deploy contracts
CMD ["npx", "hardhat", "node"]