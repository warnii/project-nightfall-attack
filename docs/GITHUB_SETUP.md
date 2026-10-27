# Publish the Project on GitHub

These are instructions for students. The application does not create repositories, configure remotes, or push code automatically.

## Create the repository

1. Sign in to GitHub and choose **New repository**.
2. Use `project-nightfall-attack-investigation` as the repository name.
3. Choose public or private according to your workshop requirements.
4. Do not initialize with a README, license, or `.gitignore`; those files already exist locally.
5. Copy the repository's HTTPS URL from GitHub.

## Initialize and publish

From PowerShell in the project directory:

```powershell
git init
git add .
git status
git commit -m "Build Project Nightfall investigation lab"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/project-nightfall-attack-investigation.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your own GitHub username and use your repository URL. Never put passwords, tokens, `.env` files, or real incident data into Git.

From macOS/Linux, the same Git commands work in a terminal. Review `git status` before committing and confirm only intended synthetic training files are staged.
