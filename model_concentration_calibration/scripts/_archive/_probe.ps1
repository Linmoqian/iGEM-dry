$ErrorActionPreference = 'Continue'
Write-Output "=== ZENODO: microcystin ==="
curl.exe -sSL --max-time 90 "https://zenodo.org/api/records?q=microcystin&size=20&sort=mostrecent"
Write-Output "=== ZENODO: fluorescence biosensor ==="
curl.exe -sSL --max-time 90 "https://zenodo.org/api/records?q=biosensor+AND+fluorescence&size=20&sort=mostrecent"
Write-Output "=== FIGSHARE: microcystin ==="
curl.exe -sSL --max-time 90 "https://api.figshare.com/v2/articles/search" -H "Content-Type: application/json" -d '{"search_for":"microcystin","page_size":20}'