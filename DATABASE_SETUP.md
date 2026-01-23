# MySQL Database Setup Guide

Follow these steps to set up the database for the AI Interview Coach.

## 1. Install MySQL
If you don't have MySQL installed, download and install **MySQL Community Server** from [dev.mysql.com](https://dev.mysql.com/downloads/mysql/).

## 2. Initialize the Database
Open your MySQL terminal or a tool like MySQL Workbench and run the script located at:
`server/database/init.sql`

Alternatively, from your command prompt (if MySQL is in your PATH):
```bash
mysql -u root -p < server/database/init.sql
```

## 3. Configure Environment Variables
Ensure your `server/.env` file has the correct database credentials:

```env
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=interview_coach
```

## 4. Verification
Once the script runs, it will create:
- Database: `interview_coach`
- Tables: `users`, `sessions`, `responses`

The application will now be able to save and retrieve your interview history.
