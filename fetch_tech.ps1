
$topics = @("coding", "deployment", "devops", "programming", "tools")
$allNews = @()

foreach ($topic in $topics) {
    $url = "https://hn.algolia.com/api/v1/search?query=$topic&amp;tags=story&amp;hitsPerPage=5"
    $response = Invoke-RestMethod -Uri $url -UseBasicParsing
    $allNews += $response.hits
}

$allNews | Select-Object title, url, points, num_comments, created_at | ConvertTo-Json -Depth 10
