@echo off
chcp 65001 >nul
echo 启动 MySQL（若已运行会提示端口占用，可忽略）
start "" /B "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" --defaults-file="%~dp0my.ini"
timeout /t 3 >nul
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" --defaults-file="%~dp0my.ini" -u root -pBaiyu0713@ -e "SELECT VERSION();"
pause
