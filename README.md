# MongoDB Migration for Koyeb

## Setup
1. Set these secrets in Koyeb:
   - `OLD_MONGODB_URI`
   - `NEW_MONGODB_URI`

2. Deploy the Docker container

## Variables
| Name              | Example Value                          |
|-------------------|----------------------------------------|
| OLD_MONGODB_URI   | `mongodb+srv://user:pass@old-cluster/` |
| NEW_MONGODB_URI   | `mongodb://new-user:pass@new-host/`    |
