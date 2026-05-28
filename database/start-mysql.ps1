# 启动本机 MySQL 8.4（数据目录：ProgramData）
# 用法：在 PowerShell 中执行  .\database\start-mysql.ps1

$mysqlBin = "C:\Program Files\MySQL\MySQL Server 8.4\bin"
$ini = Join-Path $PSScriptRoot "my.ini"

if (-not (Test-Path "$mysqlBin\mysqld.exe")) {
    Write-Error "未找到 MySQL，请确认已安装 MySQL Server 8.4"
    exit 1
}

$running = Get-Process mysqld -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "MySQL 已在运行 (PID: $($running.Id -join ','))"
    exit 0
}

Start-Process -FilePath "$mysqlBin\mysqld.exe" -ArgumentList "--defaults-file=`"$ini`"" -WindowStyle Hidden
Start-Sleep -Seconds 4

$ok = (Test-NetConnection 127.0.0.1 -Port 3306 -WarningAction SilentlyContinue).TcpTestSucceeded
if ($ok) {
    Write-Host "MySQL 已启动，端口 3306"
} else {
    Write-Error "启动失败，请查看 C:\ProgramData\MySQL\MySQL Server 8.4\Data\Third.err"
    exit 1
}
