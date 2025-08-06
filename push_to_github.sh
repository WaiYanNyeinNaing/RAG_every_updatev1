#!/bin/bash

echo "GitHub Push Helper Script"
echo "========================="
echo ""
echo "This script will help you push to your GitHub repository."
echo ""

# Check current branch
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"
echo ""

echo "Please follow these steps:"
echo ""
echo "1. Go to GitHub.com → Settings → Developer Settings → Personal Access Tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Give it a name like 'RAG-Anything-Push'"
echo "4. Select scopes: 'repo' (full control)"
echo "5. Generate and copy the token"
echo ""

read -p "Enter your GitHub username: " USERNAME
read -s -p "Enter your Personal Access Token: " TOKEN
echo ""

# Push using the token
echo ""
echo "Pushing to repository..."
git push https://${USERNAME}:${TOKEN}@github.com/WaiYanNyeinNaing/RAG_Every.git ${BRANCH}:main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "View your repo at: https://github.com/WaiYanNyeinNaing/RAG_Every"
else
    echo ""
    echo "❌ Push failed. Please check your credentials and try again."
fi