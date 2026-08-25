$ErrorActionPreference = 'Continue'
$dl = 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/datasets'
$tmp = 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/_tmp.json'
$ids = @(17566822, 4025048, 17341156, 17807781)
foreach ($id in $ids) {
  curl.exe -sSL --max-time 90 -A 'Mozilla/5.0' -o $tmp ('https://zenodo.org/api/records/' + $id + '?size=1')
  if ($LASTEXITCODE -ne 0) { Write-Output ('FETCH FAIL ' + $id); continue }
  $j = Get-Content $tmp -Raw -Encoding UTF8 | ConvertFrom-Json
  if (-not $j.metadata) { Write-Output ('NO METADATA ' + $id); continue }
  Write-Output ('=== ' + $id + ': ' + $j.metadata.title)
  foreach ($f in $j.files) {
    $name = $f.key -replace '[\\/:*?"<>|]', '_'
    $out = "$dl/${id}_${name}"
    if (Test-Path $out) { Write-Output ('  exists, skip ' + $name); continue }
    curl.exe -sSL --max-time 300 -A 'Mozilla/5.0' -o $out $f.links.self
    if ($LASTEXITCODE -eq 0 -and (Test-Path $out) -and (Get-Item $out).Length -gt 100) { Write-Output ('  OK ' + $name + ' ' + (Get-Item $out).Length + ' bytes') }
    else { Write-Output ('  FAIL ' + $name) }
    Start-Sleep -Seconds 4
  }
  Start-Sleep -Seconds 8
}