# Use official Node 20 Alpine image
FROM node:20-alpine

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Enable Yarn 4+ corepack
RUN corepack enable

# Set working directory
WORKDIR /app

# Copy package files first for optimal caching
COPY package.json yarn.lock .yarnrc.yml ./

# Install production dependencies (Yarn 4+)
COPY .yarn ./.yarn
RUN yarn install

# Copy application files
COPY . .

# Create and activate Python virtual environment
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies in virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Set non-root user for security
RUN chown -R node:node /app
USER node

# Expose application port
EXPOSE 3000

ENV NODE_ENV="dev"

# Start command
CMD ["yarn", "start"]