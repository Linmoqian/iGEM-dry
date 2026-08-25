$ErrorActionPreference = 'Continue'
$dl = 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/datasets'
$tmp = 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/_tmp.json'

$zids = @('17566822','4025048','17341156','17807781')
foreach ($zid in $zids) {
  Write-Output ('=== Zenodo ' + $zid + ' ===')
  curl.exe -sSL --max-time 90 -A 'Mozilla/5.0' -o $tmp ('https://zenodo.org/api/records/' + $zid)
  if ($LASTEXITCODE -ne 0 -or (Get-Item $tmp).Length -lt 500) { Write-Output '  JSON fetch failed'; continue }
  $j = Get-Content $tmp -Raw -Encoding UTF8 | ConvertFrom-Json
  Write-Output ('  title: ' + $j.metadata.title)
  foreach ($f in $j.files) {
    $name = $f.key -replace '[\\/:*?"<>|]', '_'
    $out = "$dl/${zid}_${name}"
    Write-Output ('  file: ' + $f.key + '  ' + [math]::Round($f.size/1024) + 'KB')
    curl.exe -sSL --max-time 300 -A 'Mozilla/5.0' -o $out $f.links.self
    if ($LASTEXITCODE -eq 0 -and (Test-Path $out)) { Write-Output ('    saved ' + (Get-Item $out).Length + ' bytes') }
    else { Write-Output '    download failed' }
  }
}

$fids = @('32928698','32928701')
foreach ($fid in $fids) {
  Write-Output ('=== Figshare ' + $fid + ' ===')
  curl.exe -sSL --max-time 90 -A 'Mozilla/5.0' -o $tmp ('https://api.figshare.com/v2/articles/' + $fid)
  if ($LASTEXITCODE -ne 0) { Write-Output '  JSON fetch failed'; continue }
  $j = Get-Content $tmp -Raw -Encoding UTF8 | ConvertFrom-Json
  Write-Output ('  title: ' + $j.title)
  foreach ($f in $j.files) {
    $name = $f.name -replace '[\\/:*?"<>|]', '_'
    $out = "$dl/figshare_${fid}_${name}"
    Write-Output ('  file: ' + $f.name + '  ' + [math]::Round($f.size/1024) + 'KB')
    curl.exe -sSL --max-time 300 -A 'Mozilla/5.0' -o $out $f.download_url
    if ($LASTEXITCODE -eq 0 -and (Test-Path $out)) { Write-Output ('    saved ' + (Get-Item $out).Length + ' bytes') }
    else { Write-Output '    download failed' }
  }
}