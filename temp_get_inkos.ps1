$resp = Invoke-WebRequest -Uri 'https://api.github.com/repos/Narcooo/inkos/git/trees/master?recursive=1' -UseBasicParsing
$data = $resp.Content | ConvertFrom-Json
$data.tree | Where-Object { $_.path -like '*skill*' } | ForEach-Object { $_.path }