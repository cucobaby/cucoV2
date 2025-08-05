@echo off
echo Deploying enhanced question answering to Railway...

cd /d "e:\VSCODE\cucoV2"

echo Adding all changes...
git add .

echo Committing changes...
git commit -m "Force deploy enhanced question answering with smart chunking and built-in definitions"

echo Pushing to Railway...
git push --force origin main

echo Done! Changes should deploy automatically to Railway.
pause
