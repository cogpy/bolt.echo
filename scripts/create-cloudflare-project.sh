#!/bin/bash

# Cloudflare Pages Project Creation Script
# This script creates a Cloudflare Pages project if it doesn't exist

set -e

PROJECT_NAME="bolt-echo"
ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID}"
API_TOKEN="${CLOUDFLARE_API_TOKEN}"

echo "🔍 Checking if Cloudflare Pages project '$PROJECT_NAME' exists..."

# Method 1: Try using wrangler to list projects
if command -v wrangler &> /dev/null; then
    echo "📋 Using wrangler to check project existence..."
    
    # Try to get project info
    if wrangler pages project list --json 2>/dev/null | grep -q "\"name\":\"$PROJECT_NAME\""; then
        echo "✅ Project '$PROJECT_NAME' already exists"
        exit 0
    else
        echo "❌ Project '$PROJECT_NAME' not found"
    fi
fi

# Method 2: Use Cloudflare API directly
echo "🚀 Creating project '$PROJECT_NAME' via Cloudflare API..."

if [ -z "$ACCOUNT_ID" ] || [ -z "$API_TOKEN" ]; then
    echo "❌ Error: CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN must be set"
    exit 1
fi

# Create project using Cloudflare API
RESPONSE=$(curl -s -w "%{http_code}" -X POST \
    "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "'$PROJECT_NAME'",
        "production_branch": "main",
        "build_config": {
            "build_command": "pnpm run build:pages",
            "destination_dir": "build/client",
            "root_dir": "/"
        }
    }')

HTTP_CODE="${RESPONSE: -3}"
RESPONSE_BODY="${RESPONSE%???}"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✅ Project '$PROJECT_NAME' created successfully!"
    echo "📊 Response: $RESPONSE_BODY"
elif [ "$HTTP_CODE" = "409" ]; then
    echo "ℹ️  Project '$PROJECT_NAME' already exists (409 Conflict)"
else
    echo "❌ Failed to create project. HTTP Code: $HTTP_CODE"
    echo "📊 Response: $RESPONSE_BODY"
    echo "⚠️  Continuing with deployment anyway..."
fi

echo "🎯 Project creation step completed"