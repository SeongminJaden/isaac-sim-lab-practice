# Windows에서 Lab 설치, 목록 조회, 무작위 행동, PPO 학습, 정책 재생을 실행한다.
param(
    # 수행할 단계를 선택하며 오타는 실행 전에 거부한다.
    [Parameter(Mandatory=$true)][ValidateSet('Setup','List','Random','Train','Play')][string]$Mode,
    # Lab 저장소 경로다. 실습자료 폴더나 Sim 전용 환경과 다르다.
    [string]$LabDir = 'C:\isaac-course\IsaacLab-6.1',
    # 병렬 환경 수다. 8 GB에서는 1개부터 확인한다.
    [ValidateRange(1,4096)][int]$NumEnvs = 1,
    # PPO 정책 갱신 횟수이며 학습 성공을 보장하는 값은 아니다.
    [ValidateRange(1,100000)][int]$Iterations = 300,
    # 재현할 때는 latest 대신 실제 정책 파일 경로를 사용한다.
    [string]$Checkpoint = 'latest',
    # none은 창을 생략한다. PhysX 실행의 GPU 요구는 유지된다.
    [ValidateSet('kit','none')][string]$Viz = 'kit',
    # 실제 실행 없이 명령 인자를 JSON으로 확인한다.
    [switch]$PrintCommand
)
$ErrorActionPreference = 'Stop' # PowerShell 오류를 무시하고 다음 단계로 진행하지 않는다.
$commit = 'ae37b028ea415c91ea2bc32609efcd759ed2b974' # Sim 6.1 대응 Lab EA 커밋이다.
$prefix = @('run','--frozen','--extra','isaacsim','isaaclab') # 잠금 파일과 Sim 의존성을 선택한다.
$task = @('--task','Isaac-Cartpole','--num_envs',"$NumEnvs") # 수업 과제와 병렬 환경 수다.
$backend = @('physics=isaacsim_physx','--viz',$Viz) # 기본 Newton 대신 강의의 PhysX를 선택한다.
switch ($Mode) { # 단계별 공식 CLI 인자를 문자열 배열로 만든다.
    'Setup' { $uvArgs = @('sync','--frozen','--extra','isaacsim') } # Lab의 .venv에 패키지를 설치한다.
    'List' { $uvArgs = $prefix + @('list_envs','--show_presets') } # 과제와 프리셋 목록을 조회한다.
    'Random' { $uvArgs = $prefix + @('random_agent') + $task + $backend } # 무작위 정책으로 움직인다.
    'Train' { $uvArgs = $prefix + @('train','--rl_library','rsl_rl') + $task + @('--seed','42','--max_iterations',"$Iterations") + $backend } # PPO를 학습한다.
    'Play' { $uvArgs = $prefix + @('play','--rl_library','rsl_rl') + $task + @('--seed','123','--checkpoint',$Checkpoint) + $backend } # 저장된 정책을 재생한다.
}
if ($PrintCommand) { # 미리보기는 파일 생성이나 패키지 설치를 하지 않는다.
    [pscustomobject]@{cwd=$LabDir;commit=$commit;executable='uv';arguments=$uvArgs} | ConvertTo-Json -Depth 3 # 인자 경계를 출력한다.
    return # 실제 실행 경로로 내려가지 않는다.
}
foreach ($tool in @('git','uv')) { # 필수 도구를 하나씩 확인한다.
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool is required. See README setup." } # 없는 도구를 알려준다.
}
if ($Mode -eq 'Setup' -and -not (Test-Path -LiteralPath $LabDir)) { # 새 경로에만 저장소를 만든다.
    & git clone --filter=blob:none --no-checkout --branch v3.0.0-EA https://github.com/isaac-sim/IsaacLab.git $LabDir # 공식 EA를 받는다.
    if ($LASTEXITCODE -ne 0) { throw 'Clone failed.' } # Git 실패 후 계속하지 않는다.
    & git -C $LabDir checkout --detach $commit # 브랜치 최신값이 아닌 정확한 커밋을 선택한다.
    if ($LASTEXITCODE -ne 0) { throw 'Pinned checkout failed.' } # checkout 실패도 검사한다.
}
if (-not (Test-Path -LiteralPath (Join-Path $LabDir '.git'))) { throw 'Run -Mode Setup first, or specify -LabDir.' } # 일반 폴더 실행을 막는다.
$actual = & git -C $LabDir rev-parse HEAD # 현재 checkout의 전체 SHA를 읽는다.
if ($LASTEXITCODE -ne 0 -or $actual.Trim() -ne $commit) { throw 'Checkout differs from the course pin. Use a separate new course directory.' } # 버전 혼용을 막는다.
$changes = & git -C $LabDir status --porcelain --untracked-files=no # 로그 파일은 허용하고 원본 소스 변경을 조회한다.
if ($LASTEXITCODE -ne 0 -or $changes) { throw 'Tracked course files have changes. Keep the original pinned checkout for this exercise.' } # 사용자 수정은 자동으로 되돌리지 않는다.
if ($Mode -eq 'Play' -and $Checkpoint -ne 'latest' -and $Checkpoint -ne 'best') { # 명시한 정책 파일을 검사한다.
    $Checkpoint = (Resolve-Path -LiteralPath $Checkpoint).Path # cd 전에 상대 경로를 절대 경로로 고정한다.
    if (-not (Test-Path -LiteralPath $Checkpoint -PathType Leaf)) { throw 'Checkpoint must be a file.' } # 디렉터리는 모델이 아니다.
    $at = [array]::IndexOf($uvArgs,'--checkpoint') # 교체할 값의 위치를 찾는다.
    $uvArgs[$at+1] = $Checkpoint # 공백이 있는 경로도 단일 인자로 보존한다.
}
Push-Location -LiteralPath $LabDir # uv가 Lab의 pyproject.toml과 uv.lock을 사용하도록 이동한다.
try {
    Write-Host "Isaac Lab $commit / Isaac-Cartpole / Isaac Sim PhysX / $Viz" # 실행 조건을 기록한다.
    & uv @uvArgs # 문자열을 다시 해석하지 않고 배열 인자를 전달한다.
    if ($LASTEXITCODE -ne 0) { throw "Isaac Lab $Mode failed (exit $LASTEXITCODE). Read the first error above." } # 외부 명령 실패를 전파한다.
} finally {
    Pop-Location # 실패해도 호출자가 있던 폴더로 복귀한다.
}
