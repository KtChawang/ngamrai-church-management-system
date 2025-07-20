@echo off
REM ------------------------- CONFIG -------------------------
cd /d "C:\Users\USER\Church Management System"

REM 1) Activate virtual environment
call venz\Scripts\activate

REM 2) Ensure backup folder exists
if not exist backups mkdir backups

REM 3) Create timestamp
for /f %%i in ('powershell -command "Get-Date -format yyyy-MM-dd_HH-mm-ss"') do set TSTAMP=%%i

echo === Backing up database …
copy /y "db.sqlite3" "backups\db_%TSTAMP%.sqlite3" > nul

echo === Dumping JSON snapshot (UTF-8) …
python dump_json_utf8.py

REM Optionally rename the output with timestamp
rename backups\db_dump.json db_dump_%TSTAMP%.json

echo === Zipping media folder …
powershell -command ^
  "Compress-Archive -Path 'media' -DestinationPath 'backups\media_%TSTAMP%.zip' -Force"

echo.
echo ✅ Backup finished! Files saved in the \backups folder.
pause
