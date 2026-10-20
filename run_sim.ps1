# Windows에서 공통 Python 예제를 실행하는 옵션이다.
param(
    # 01은 상자 낙하, 02는 카메라 촬영이다.
    [Parameter(Mandatory=$true)][ValidateSet('01','02')][string]$Example,
    # Sim 가상환경의 Python 또는 Workstation의 python.bat를 지정한다.
    [string]$Python = 'C:\isaac-course\simenv\Scripts\python.exe',
    # 남은 인자는 높이·중력·seed 같은 예제 옵션으로 전달한다.
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$ExampleArgs
# 옵션 정의를 끝낸다.
)
# PowerShell 오류를 무시하지 않는다.
$ErrorActionPreference = 'Stop'
# 일반 Python을 잘못 선택하지 않도록 지정 경로를 확인한다.
if (-not (Test-Path -LiteralPath $Python)) { throw 'Pass -Python with the full path to Isaac Sim Python or python.bat.' }
# 허용된 예제 번호를 파일 이름에 대응시킨다.
$scripts = @{'01'='01_drop_cubes.py';'02'='02_camera_capture.py'}
# 배열 전달로 경로의 공백과 예제 옵션을 보존한다.
& $Python (Join-Path $PSScriptRoot ('examples\'+$scripts[$Example])) @ExampleArgs
# 실행 실패가 성공처럼 보이지 않도록 종료 코드를 확인한다.
if ($LASTEXITCODE -ne 0) { throw "Example $Example failed (exit $LASTEXITCODE). Read the first Python error above." }
