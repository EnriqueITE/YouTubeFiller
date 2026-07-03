# YouTube Filler
# Copyright (C) 2026 Enrique Serrano Aparicio
#
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions; see LICENSE for details.
#
# SPDX-License-Identifier: GPL-3.0-only
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -Raw -Path (Join-Path $root 'manifest.json') | ConvertFrom-Json
$dist = Join-Path $root 'dist'
$packageName = "youtube-filler-$($manifest.version)-chrome-web-store.zip"
$packagePath = Join-Path $dist $packageName

New-Item -ItemType Directory -Force -Path $dist | Out-Null
if (Test-Path $packagePath) {
  Remove-Item -LiteralPath $packagePath -Force
}

$include = @(
  'manifest.json',
  'background.js',
  'content.js',
  'styles.css',
  'options.html',
  'options.css',
  'options.js',
  '_locales',
  'icons'
)

$temp = Join-Path $env:TEMP ("youtube-filler-package-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $temp | Out-Null
try {
  foreach ($item in $include) {
    $source = Join-Path $root $item
    $target = Join-Path $temp $item
    if (Test-Path $source -PathType Container) {
      Copy-Item -LiteralPath $source -Destination $target -Recurse
    } else {
      Copy-Item -LiteralPath $source -Destination $target
    }
  }
  Compress-Archive -Path (Join-Path $temp '*') -DestinationPath $packagePath -Force
  Write-Host "Created $packagePath"
} finally {
  Remove-Item -LiteralPath $temp -Recurse -Force
}
