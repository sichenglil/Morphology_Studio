param(
  [Parameter(Mandatory=$true)][ValidateSet("pre","post")][string]$Stage,
  [string]$Label="joint-rendering-performance",
  [string]$BackupRepository=$env:MORPHOLOGY_BACKUP_REPO
)
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Run([string]$Exe,[string[]]$CommandArgs){
  $old=$script:ErrorActionPreference; $script:ErrorActionPreference="Continue"
  $out=& $Exe @CommandArgs; $code=$LASTEXITCODE
  $script:ErrorActionPreference=$old
  if($code -ne 0){throw "$Exe $($CommandArgs -join ' ') failed ($code): $($out -join [Environment]::NewLine)"}
  return @($out|ForEach-Object{"$_"})
}
function Git([string[]]$CommandArgs){Run git.exe $CommandArgs}
function RemoteGit([string[]]$CommandArgs){Run git.exe (@('-c','http.version=HTTP/1.1')+$CommandArgs)}
function RemoteRetry([string[]]$CommandArgs){
  for($i=1;$i -le 5;$i++){try{return RemoteGit $CommandArgs}catch{if($i -eq 5){throw};Start-Sleep -Seconds (2*$i)}}
}
function Gh([string[]]$CommandArgs){Run gh.exe $CommandArgs}
function Save([string]$Path,[string[]]$Lines){[IO.File]::WriteAllText($Path,(($Lines-join "`n")+"`n"),[Text.UTF8Encoding]::new($false))}
function Sha([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash}
function Norm([string]$Url){($Url.Trim()-replace '\.git$',''-replace '^git@github\.com:','https://github.com/').ToLowerInvariant()}

if(-not(Get-Command gh -ErrorAction SilentlyContinue)){throw 'BACKUP_BLOCKED_GH_NOT_INSTALLED'}
if(-not(Get-Command git -ErrorAction SilentlyContinue)){throw 'BACKUP_BLOCKED_GIT_NOT_INSTALLED'}
$owner=(Gh @('api','user','--jq','.login')|Select-Object -First 1).Trim()
if(-not $BackupRepository){$BackupRepository="$owner/Morphology_Studio-backup"}
try{Gh @('repo','view',$BackupRepository,'--json','visibility')|Out-Null}catch{Gh @('repo','create',$BackupRepository,'--private','--description','Private snapshots for Morphology Studio development')|Out-Null}
$repo=Gh @('repo','view',$BackupRepository,'--json','visibility,url')|ConvertFrom-Json
if($repo.visibility -ne 'PRIVATE'){throw 'BACKUP_BLOCKED_REPOSITORY_NOT_PRIVATE'}
$url="$($repo.url).git"
$remotes=@(Git @('remote'))
if($remotes -contains 'github-backup'){
  $existing=Git @('remote','get-url','github-backup')|Select-Object -First 1
  if((Norm $existing) -ne (Norm $url)){throw "REMOTE_NAME_CONFLICT: $existing"}
}else{Git @('remote','add','github-backup',$url)|Out-Null}
RemoteRetry @('ls-remote','github-backup')|Out-Null

$files=@((Git @('ls-files'))+(Git @('ls-files','--others','--exclude-standard')))|Sort-Object -Unique
$pattern='(^|/)(\.env($|\.)|id_rsa$|id_ed25519$|credentials[^/]*$|secrets[^/]*$|token[^/]*$|auth[^/]*$|service-account[^/]*$)|\.(pem|key|pfx|p12)$'
$sensitive=@($files|Where-Object{$_ -match $pattern})
if($sensitive.Count){throw "BACKUP_BLOCKED_SENSITIVE_FILES: $($sensitive -join ', ')"}

$ts=Get-Date -Format 'yyyyMMdd-HHmmss'; $branch="snapshots/$Stage-$Label-$ts"
if(@(RemoteRetry @('ls-remote','--heads','github-backup',"refs/heads/$branch")).Count){$branch+="-$([Guid]::NewGuid().ToString('N').Substring(0,6))"}
$dir=Join-Path $Root "build/backups/$ts-$Stage"; New-Item -ItemType Directory -Force $dir|Out-Null
$origBranch=Git @('branch','--show-current')|Select-Object -First 1; $origHead=Git @('rev-parse','HEAD')|Select-Object -First 1
$bs=Join-Path $dir 'before-status.txt';$bd=Join-Path $dir 'before-working.diff';$bc=Join-Path $dir 'before-cached.diff'
Save $bs (Git @('status','--porcelain=v1','-uall'));Save $bd (Git @('diff','--binary','HEAD'));Save $bc (Git @('diff','--cached','--binary'))
$hash=@{s=Sha $bs;d=Sha $bd;c=Sha $bc};$dirty=(Get-Content $bs -Raw).Trim().Length -gt 0;$stashed=$false
if($dirty){Git @('stash','push','--include-untracked','--message',"github-backup:$Stage`:$Label`:$ts")|Out-Null;$commit=Git @('rev-parse','refs/stash')|Select-Object -First 1;$stashed=$true}else{$commit=$origHead}
try{RemoteRetry @('push','github-backup',"$commit`:refs/heads/$branch")|Out-Null}finally{if($stashed){try{Git @('stash','pop','--index')|Out-Null}catch{throw 'BACKUP_RESTORE_CONFLICT'}}}
$as=Join-Path $dir 'after-status.txt';$ad=Join-Path $dir 'after-working.diff';$ac=Join-Path $dir 'after-cached.diff'
Save $as (Git @('status','--porcelain=v1','-uall'));Save $ad (Git @('diff','--binary','HEAD'));Save $ac (Git @('diff','--cached','--binary'))
$restored=$origBranch -eq (Git @('branch','--show-current')|Select-Object -First 1) -and $origHead -eq (Git @('rev-parse','HEAD')|Select-Object -First 1) -and $hash.s -eq (Sha $as) -and $hash.d -eq (Sha $ad) -and $hash.c -eq (Sha $ac)
if(-not $restored){throw 'BACKUP_RESTORE_VERIFICATION_FAILED'}
$verified=$false
for($attempt=1;$attempt -le 4;$attempt++){
  try{RemoteGit @('ls-remote','--exit-code','github-backup',"refs/heads/$branch")|Out-Null;$verified=$true;break}
  catch{if($attempt -eq 4){throw};Start-Sleep -Seconds (2*$attempt)}
}
if(-not $verified){throw 'BACKUP_REMOTE_VERIFICATION_FAILED'}
$manifest=[ordered]@{stage=$Stage;created_at=(Get-Date).ToString('o');repository=$BackupRepository;visibility='PRIVATE';remote_url=$url;snapshot_branch=$branch;snapshot_commit=$commit;original_branch=$origBranch;original_head=$origHead;had_uncommitted_content=$dirty;sensitive_file_scan='PASS';local_restore_verified=$true;force_push_used=$false}
[IO.File]::WriteAllText((Join-Path $dir 'backup-manifest.json'),($manifest|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
$apply=if($dirty){"git stash apply refs/remotes/github-backup/$branch"}else{"git switch --detach refs/remotes/github-backup/$branch"}
Save (Join-Path $dir 'backup-report.md') @('# GitHub snapshot backup','',"- Status: $($Stage.ToUpper())_BACKUP_PASS","- Repository: $BackupRepository (PRIVATE)","- Branch: $branch","- Commit: $commit",'- Sensitive scan: PASS','- Local restore: VERIFIED','- Force push: false','','Create a safety branch, then:','```powershell',"git fetch github-backup refs/heads/$branch`:refs/remotes/github-backup/$branch",$apply,'```')
Write-Output "$($Stage.ToUpper())_BACKUP_PASS";Write-Output "SNAPSHOT_BRANCH=$branch";Write-Output "SNAPSHOT_COMMIT=$commit";Write-Output "MANIFEST=$($dir.Replace('\','/'))/backup-manifest.json"
