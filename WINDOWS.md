# Windows 11 실행 안내

일반 PowerShell에서 아래 순서로 진행한다. Python 3.12 x64와 Git이 필요하다. 설치 파일은 [Python](https://www.python.org/downloads/windows/), [Git](https://git-scm.com/download/win) 공식 사이트에서 받는다. Windows 긴 경로 사용 설정은 Lab 설치 전에 준비한다. 기존 Sim 6.1 Workstation을 쓰면 아래의 Sim 설치 단계를 생략하고 해당 `python.bat`를 사용한다.

## 1. 자료 준비

실습자료 전용 공개 저장소를 받는다. 이미 받았다면 아래 다운로드 단계는 생략하고 기존 폴더에서 `99_self_check.py`를 실행한다. 새로 받는 경우의 예시는 다음과 같다.

```powershell
# 새 작업 위치를 준비한다.
New-Item -ItemType Directory -Force C:\isaac-course | Out-Null
# 이전 실습 결과를 덮어쓰지 않는다.
if (Test-Path C:\isaac-course\windows_lab) { throw 'Choose a new course folder or use the existing copy.' }
# 공개 실습자료만 PPT와 같은 짧은 영문 경로에 받는다.
git clone --depth 1 https://github.com/SeongminJaden/isaac-sim-lab-practice.git C:\isaac-course\windows_lab
# 다운로드 실패를 무시하고 다음 단계로 진행하지 않는다.
if ($LASTEXITCODE -ne 0) { throw 'Practice repository clone failed.' }
# 이후 모든 실습 명령의 시작 폴더다.
Set-Location C:\isaac-course\windows_lab
# 일반 Python으로 코드와 PowerShell 실행기 검사 16개를 실행한다.
py -3.12 .\99_self_check.py
```

`OK`는 CPU·실행기 검사 통과다. GPU 실습 성공은 아래의 실제 출력으로 확인한다.

## 2. Sim 전용 환경

8 GB GPU에서 기본 화면이 느리면 호환성 검사 창을 닫은 뒤, 아래 마지막 `& $sim` 대신 **2-1의 저사양 실행 명령**을 사용한다. 설치가 끝났다면 설치 스크립트를 다시 실행할 필요가 없다.

```powershell
# 드라이버, GPU 메모리, RAM, 긴 경로 설정을 읽는다.
.\00_check_environment.ps1
# 없는 새 경로에 Sim 6.1 환경을 설치한다. 기존 환경은 덮어쓰지 않는다.
.\01_install_sim.ps1
# 설치된 Sim 환경의 Python 경로를 보관한다.
$simPython = 'C:\isaac-course\simenv\Scripts\python.exe'
# 환경 내의 Sim 실행 파일 위치다.
$sim = 'C:\isaac-course\simenv\Scripts\isaacsim.exe'
# 호환성 검사 창에서 결과를 확인하고 창을 닫는다.
& $sim isaacsim.exp.compatibility_check
# 기본 Sim 창이 열리는지 확인하고 다시 닫는다.
& $sim
```

첫 실행의 NVIDIA 약관은 내용을 읽고 직접 응답한다. 설치 성공만으로 화면·물리 성공을 판정하지 않는다. 이미 설치한 6.1 Workstation은 `$simPython`을 실제 `C:\isaacsim\python.bat` 경로로 지정하면 된다.

### 2-1. 8 GB GPU용 저사양 화면 실행

열려 있는 Sim과 호환성 검사 창을 먼저 닫는다. 아래 코드를 PowerShell에 한 번에 붙여 넣는다. 단순화된 렌더러, 렌더링 해상도 640×360, 안티앨리어싱 끄기, 단일 GPU, 텍스처 스트리밍 예산 20%를 적용한다.

```powershell
# 설치된 Isaac Sim 실행 파일이다.
$sim = 'C:\isaac-course\simenv\Scripts\isaacsim.exe'
# 저사양 실행 옵션을 문자열 배열로 구성한다.
$lowOptions = @(
    # 단순화된 렌더러를 사용한다.
    '--/rtx/rendermode=MinimalRendering'
    # 텍스처 표현을 줄이는 Constant Diffuse 모드다.
    '--/rtx/minimal/mode=3'
    # 실제 렌더링 너비를 낮춘다.
    '--/app/renderer/resolution/width=640'
    # 실제 렌더링 높이를 낮춘다.
    '--/app/renderer/resolution/height=360'
    # 조작용 창 너비는 별도로 지정한다.
    '--/app/window/width=960'
    # 조작용 창 높이는 별도로 지정한다.
    '--/app/window/height=540'
    # 안티앨리어싱을 끈다.
    '--/rtx/post/aa/op=0'
    # 단일 GPU로 렌더링한다.
    '--/renderer/multiGpu/enabled=false'
    # 텍스처 스트리밍의 VRAM 예산을 20%로 낮춘다.
    '--/rtx-transient/resourcemanager/texturestreaming/memoryBudget=0.2'
)
# 기본 실행 명령 대신 저사양 옵션을 전달한다.
& $sim @lowOptions
```

텍스처가 필요하면 `--/rtx/minimal/mode=3`을 `2`로 바꾼다. `memoryBudget=0.2`는 **텍스처 스트리밍 예산**이며 프로그램 전체 VRAM을 20%로 제한하는 값은 아니다. 너무 낮추면 텍스처 품질이나 로딩에 영향을 줄 수 있다.

이 설정은 이번에 여는 Sim에 적용된다. 별도로 시작하는 Python 예제와 Isaac Lab에는 자동 적용되지 않는다. RGB 카메라 실습은 재질·조명 표현이 달라질 수 있으므로 기본 설정의 결과와 구분한다. 기본 화면으로 돌아가려면 창을 닫고 옵션 없이 `& $sim`을 실행한다.

Isaac Sim 6.1의 [렌더링 모드](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/reference_material/rendering_modes.html)와 [메모리 최적화 안내](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/reference_material/sim_performance_optimization_handbook.html#reducing-gpu-memory-utilization)를 기준으로 작성했다. 이 옵션 조합의 실제 GPU 메모리 감소량은 아직 측정하지 않았으며, 8 GB에서 실행을 보장하지 않는다.

## 3. 낙하, 카메라, 보상

명령 하나가 끝나면 다음 명령을 실행한다. 다른 Sim 창은 닫아 GPU 메모리를 확보한다.

```powershell
# 1 kg과 10 kg 상자의 높이 CSV를 만든다.
.\run_sim.ps1 -Example 01 -Python $simPython
# 초기 높이 4 m로 조건을 바꾸어 비교한다.
.\run_sim.ps1 -Example 01 -Python $simPython -ExampleArgs '--height','4'
# seed 7의 RGB·깊이·장면 조건 파일을 만든다.
.\run_sim.ps1 -Example 02 -Python $simPython -ExampleArgs '--seed','7'
# seed를 바꾸어 다른 배치를 저장한다.
.\run_sim.ps1 -Example 02 -Python $simPython -ExampleArgs '--seed','42'
# GPU 없이 보상 점수 표를 계산한다.
py -3.12 .\examples\03_reward_design.py
# 이 폴더 아래의 실행별 결과를 확인한다.
Get-ChildItem .\outputs
```

낙하는 `heights.csv`에 실제 물리 시간과 두 상자 중심 높이가 기록되어야 한다. 카메라는 검정 화면이 아닌 `rgb.png`, `depth_m.npy`, `depth_preview.png`, `scene_metadata.json`을 확인한다. 결과를 [활동지](EXERCISES.md)에 적는다.

## 4. Isaac Lab 설치와 Cartpole

[uv 공식 설치 안내](https://docs.astral.sh/uv/getting-started/installation/)에 따라 uv를 준비한다. Python Launcher가 있다면 다음처럼 설치할 수 있다. 설치 뒤 새 터미널에서도 `uv --version`이 동작해야 한다.

```powershell
# uv만 사용자 Python 도구로 설치한다. Sim 환경을 수정하는 명령이 아니다.
py -3.12 -m pip install --user uv
# 명령이 PATH에 있는지 확인한다.
uv --version
# 고정된 Lab 소스를 받고 Lab 자체 .venv에 의존성을 설치한다.
.\04_cartpole.ps1 -Mode Setup
# 사용할 수 있는 과제와 프리셋을 조회한다.
.\04_cartpole.ps1 -Mode List
# 학습 전 무작위 행동을 관찰하고 창 닫기 또는 Ctrl+C로 끝낸다.
.\04_cartpole.ps1 -Mode Random
# 환경 1개, seed 42, PPO 갱신 300회로 학습한다.
.\04_cartpole.ps1 -Mode Train -NumEnvs 1 -Iterations 300
# 학습이 정상 종료되고 체크포인트가 만들어졌을 때만 재생한다.
.\04_cartpole.ps1 -Mode Play -Checkpoint latest
```

Lab 기본 경로는 `C:\isaac-course\IsaacLab-6.1`이다. 다른 경로를 사용할 때는 **모든 단계**에 같은 `-LabDir '경로'`를 지정한다. `latest`는 최근 학습 결과를 고르므로 수업 재현 시 실제 파일 경로를 기록한다. 300회 갱신은 시작 설정이며 수렴을 보장하지 않는다.

```powershell
# 실제 실행 없이 사용할 명령 배열을 확인한다.
.\04_cartpole.ps1 -Mode Train -NumEnvs 1 -Iterations 2 -Viz none -PrintCommand
# 짧은 실제 GPU 시험이다. 위 미리보기와 달리 Kit/물리/학습을 실행한다.
.\04_cartpole.ps1 -Mode Train -NumEnvs 1 -Iterations 2 -Viz none
# 학습이 만든 모델 파일을 찾아 실제 경로를 확인한다.
Get-ChildItem C:\isaac-course\IsaacLab-6.1\logs -Filter 'model_*.pt' -Recurse
# 아래 경로는 예시이며, 위에서 확인한 실제 체크포인트로 교체한다.
.\04_cartpole.ps1 -Mode Play -Checkpoint 'C:\isaac-course\IsaacLab-6.1\logs\rsl_rl\실제실행폴더\model_299.pt'
```

실습 폴더가 아닌 Lab의 `logs`에 학습 결과가 저장된다. `-Viz none`은 창을 생략하며 NVIDIA GPU 요구는 유지된다. 앱 제어의 `WinError 4551`이 나오면 차단된 실행 파일·DLL을 기록하고 실행이 허용된 PC 환경에서 재시험한다. 이 자료는 보안 정책을 해제하거나 우회하지 않는다. 제작 PC의 실제 결과는 [검증 보고서](VALIDATION.md)에 있다.
