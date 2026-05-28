$root = "c:\Users\wuyih\Desktop\1\v1.2"
$doc = Get-ChildItem -Path $root -Recurse -Filter "15*.doc" | Select-Object -First 1
Write-Host "FILE:" $doc.FullName
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$d = $word.Documents.Open($doc.FullName)
$text = $d.Content.Text
$d.Close($false)
$word.Quit()
[System.IO.File]::WriteAllText("c:\Users\wuyih\Desktop\1\v1.2\project1\docs\_ref_outline.txt", $text, [System.Text.Encoding]::UTF8)
Write-Host "DONE len" $text.Length
