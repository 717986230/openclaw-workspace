
$url = "https://hn.algolia.com/api/v1/search?query=ai&amp;tags=story&amp;hitsPerPage=10"
$response = Invoke-RestMethod -Uri $url -UseBasicParsing
$response.hits | Select-Object title, url, points, num_comments, created_at | ConvertTo-Json -Depth 10
