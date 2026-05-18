# 执行 database/init.sql
$ErrorActionPreference = "Stop"
$mysql = "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
$password = "Baiyu0713@"
$sqlFile = Join-Path $PSScriptRoot "..\database\init.sql"

& $mysql -u root "-p$password" -e "source $($sqlFile -replace '\\','/')"
Write-Host "数据库 init.sql 执行完成。"
