# Ubuntu 24.04 실행 안내

GPU 실습은 **NVIDIA RTX GPU를 직접 사용하는 Ubuntu 24.04 x86_64 PC** 기준이다. WSL Ubuntu에서는 이 자료의 CPU·Bash 검사를 실제 실행했다. WSL의 CUDA 인식이나 VirtualBox 설치 성공을 Isaac Sim의 RTX 실행 성공으로 취급하지 않는다. Jetson용 설치 절차와도 다르다.

## 1. 기본 도구와 자료

Ubuntu의 드라이버 설치를 먼저 완료하고 `nvidia-smi`에서 GPU를 확인한다. 이 안내는 이미 작동하는 드라이버를 자동 교체하지 않는다. Python 3.12는 Ubuntu 24.04의 기본 계열이다.

```bash
# Ubuntu 패키지 목록을 갱신한다.
sudo apt update
# Python 가상환경, Git, Lab 설치에 필요한 기본 빌드 도구를 설치한다.
sudo apt install -y git build-essential cmake python3.12-venv python3-pip pipx
# 사용자 도구용으로 uv를 설치한다. 시스템 Python에 pip로 패키지를 섞지 않는다.
pipx install uv
# 이번 터미널에서 pipx의 실행 파일 경로를 추가한다.
export PATH="$HOME/.local/bin:$PATH"
# uv 설치를 확인한다.
uv --version
# 수업 폴더를 만든다.
mkdir -p "$HOME/pa-course"
# 기존 실습자료를 덮어쓰지 않는다.
test ! -e "$HOME/pa-course/windows_lab" || { echo 'Use the existing copy or choose a new folder'; exit 1; }
# 공개 실습자료만 PPT와 같은 경로에 받으며 다운로드 실패 시 중단한다.
git clone --depth 1 https://github.com/SeongminJaden/isaac-sim-lab-practice.git "$HOME/pa-course/windows_lab" || exit 1
# 이후 실습을 실행할 위치로 이동한다.
cd "$HOME/pa-course/windows_lab"
# OS·GPU·RAM·디스크 상태를 확인한다.
bash ubuntu/00_check_environment.sh
# GPU 없이 코드와 Bash 실행기 검사 16개를 수행한다.
python3.12 99_self_check.py
```

이미 이 공개 저장소를 받았다면 다운로드 단계는 생략하고 해당 폴더로 이동한다. `windows_lab`이라는 폴더명은 PPT와 맞추기 위한 것이며 Ubuntu 파일은 그 안의 `ubuntu/`에 있다.

## 2. Sim 6.1 전용 환경

8 GB GPU에서 기본 화면이 느리면 호환성 검사 창을 닫은 뒤, 아래 마지막 기본 화면 실행 명령 대신 **2-1의 저사양 실행 명령**을 사용한다. 설치가 끝났다면 설치 스크립트를 다시 실행할 필요가 없다.

```bash
# 새 가상환경에 Sim과 확장 캐시를 설치한다. 기존 경로는 덮어쓰지 않는다.
bash ubuntu/01_install_sim.sh
# 예제 실행기가 사용할 Sim Python을 지정한다.
export ISAAC_PYTHON="$HOME/pa-course/.venv-isaacsim/bin/python"
# 호환성 검사 창을 확인한 뒤 닫는다.
"$HOME/pa-course/.venv-isaacsim/bin/isaacsim" isaacsim.exp.compatibility_check
# 기본 Sim 창을 열고 NVIDIA 약관을 직접 확인한 뒤 창을 닫는다.
"$HOME/pa-course/.venv-isaacsim/bin/isaacsim"
```

기존 Isaac Sim 6.1 Workstation을 쓰면 설치 스크립트를 생략하고 `ISAAC_PYTHON`에 실제 `python.sh` 경로를 지정한다. 예: `export ISAAC_PYTHON="$HOME/isaacsim/python.sh"`. 새 터미널을 열면 이 변수를 다시 지정한다.

### 2-1. 8 GB GPU용 저사양 화면 실행

열려 있는 Sim과 호환성 검사 창을 먼저 닫는다. 아래 코드를 Ubuntu Bash 터미널에 한 번에 붙여 넣는다. NVIDIA GPU를 직접 사용하는 Ubuntu PC 기준이며, WSL의 RTX 실행 지원을 추가하는 설정은 아니다.

```bash
# 설치된 Isaac Sim 실행 파일이다.
SIM="$HOME/pa-course/.venv-isaacsim/bin/isaacsim"
# 저사양 실행 옵션을 문자열 배열로 구성한다.
LOW_OPTIONS=(
    # 단순화된 렌더러를 사용한다.
    "--/rtx/rendermode=MinimalRendering"
    # 텍스처 표현을 줄이는 Constant Diffuse 모드다.
    "--/rtx/minimal/mode=3"
    # 실제 렌더링 너비를 낮춘다.
    "--/app/renderer/resolution/width=640"
    # 실제 렌더링 높이를 낮춘다.
    "--/app/renderer/resolution/height=360"
    # 조작용 창 너비는 별도로 지정한다.
    "--/app/window/width=960"
    # 조작용 창 높이는 별도로 지정한다.
    "--/app/window/height=540"
    # 안티앨리어싱을 끈다.
    "--/rtx/post/aa/op=0"
    # 단일 GPU로 렌더링한다.
    "--/renderer/multiGpu/enabled=false"
    # 텍스처 스트리밍의 VRAM 예산을 20%로 낮춘다.
    "--/rtx-transient/resourcemanager/texturestreaming/memoryBudget=0.2"
)
# 기본 실행 명령 대신 저사양 옵션을 전달한다.
"$SIM" "${LOW_OPTIONS[@]}"
```

렌더링 해상도는 640×360, 조작용 창은 960×540이다. 텍스처가 필요하면 `--/rtx/minimal/mode=3`을 `2`로 바꾼다. `memoryBudget=0.2`는 **텍스처 스트리밍 예산**이며 프로그램 전체 VRAM을 20%로 제한하는 값은 아니다. 너무 낮추면 텍스처 품질이나 로딩에 영향을 줄 수 있다.

이 설정은 이번에 여는 Sim에 적용된다. 별도로 시작하는 Python 예제와 Isaac Lab에는 자동 적용되지 않는다. RGB 카메라 실습은 재질·조명 표현이 달라질 수 있으므로 기본 설정의 결과와 구분한다. 기본 화면으로 돌아가려면 창을 닫고 같은 터미널에서 옵션 없이 `"$SIM"`을 실행한다.

Isaac Sim 6.1의 [렌더링 모드](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/reference_material/rendering_modes.html)와 [메모리 최적화 안내](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/reference_material/sim_performance_optimization_handbook.html#reducing-gpu-memory-utilization)를 기준으로 작성했다. 이 옵션 조합의 실제 GPU 메모리 감소량은 아직 측정하지 않았으며, 8 GB에서 실행을 보장하지 않는다.

## 3. 낙하, 카메라, 보상

```bash
# 기본 조건의 낙하를 실행하고 실제 높이 CSV를 저장한다.
bash ubuntu/run_sim.sh 01
# 초기 높이 4 m를 시험한다.
bash ubuntu/run_sim.sh 01 --height 4
# 중력을 달 표면에 가까운 값으로 바꿔 비교한다.
bash ubuntu/run_sim.sh 01 --gravity 1.62
# 첫 배치의 RGB·깊이 파일을 만든다.
bash ubuntu/run_sim.sh 02 --seed 7
# 다른 배치를 같은 카메라 조건으로 촬영한다.
bash ubuntu/run_sim.sh 02 --seed 42
# 일반 Python으로 보상 식을 계산한다. 이 명령은 WSL에서도 검증했다.
python3.12 examples/03_reward_design.py
# 실행별 결과 폴더를 확인한다.
ls outputs
```

각 실행이 종료된 다음 명령을 수행한다. `outputs/01_drop_.../heights.csv`, `outputs/02_camera_.../rgb.png`와 깊이 파일을 확인하고 [활동지](EXERCISES.md)에 결과를 기록한다.

## 4. Isaac Lab 설치와 Cartpole

```bash
# 공식 EA 고정 커밋을 받고 Lab 자체 .venv를 설치한다.
bash ubuntu/04_cartpole.sh --mode setup
# 설치 환경에서 과제와 프리셋 목록을 조회한다.
bash ubuntu/04_cartpole.sh --mode list
# 무작위 행동을 관찰한 후 창 닫기 또는 Ctrl+C로 종료한다.
bash ubuntu/04_cartpole.sh --mode random
# 환경 1개, seed 42, PPO 갱신 300회로 학습한다.
bash ubuntu/04_cartpole.sh --mode train --num-envs 1 --iterations 300
# 학습이 체크포인트를 저장한 다음 최신 정책을 재생한다.
bash ubuntu/04_cartpole.sh --mode play --checkpoint latest
```

기본 Lab 경로는 `$HOME/pa-course/IsaacLab-6.1`이다. 바꾸려면 모든 단계에 `--lab-dir "경로"`를 동일하게 붙인다. 기존 checkout의 버전이 다르면 새 경로를 사용한다. 공식 lock을 유지하며 Sim 전용 환경과 섞지 않는다.

`unrecognized arguments: list_envs --show_presets`가 나오면 이전 실행기를 사용 중이다. Git으로 받은 실습자료는 실습 폴더에서 `git pull --ff-only`로 갱신한다. ZIP으로 받았다면 최신 `ubuntu/04_cartpole.sh`를 받는다. 설치를 다시 할 필요는 없다. PPT/PDF 24쪽의 이전 목록 조회 명령도 아래 명령으로 교체한다.

```bash
# 서브셸 안에서만 Lab 폴더로 이동하여 원래 작업 위치를 유지한다.
(
    # 별도 Lab 경로를 사용했다면 이 경로를 바꾼다.
    cd "$HOME/pa-course/IsaacLab-6.1" || exit 1
    # 이 EA 버전에서는 목록 조회용 Python 스크립트를 직접 실행한다.
    uv run --frozen --extra isaacsim python scripts/environments/list_envs.py --show_presets
)
```

```bash
# 실제 설치·학습 없이 인자 배열만 확인한다.
bash ubuntu/04_cartpole.sh --mode train --iterations 2 --viz none --print-command
# 짧은 실제 GPU 실행 시험이다. 창은 생략하지만 GPU는 필요하다.
bash ubuntu/04_cartpole.sh --mode train --num-envs 1 --iterations 2 --viz none
# 실제로 생성된 정책 파일 경로를 조회한다.
find "$HOME/pa-course/IsaacLab-6.1/logs" -type f -name 'model_*.pt'
# 아래 예시를 조회한 실제 파일 경로로 교체하여 재생한다.
bash ubuntu/04_cartpole.sh --mode play --checkpoint "$HOME/pa-course/IsaacLab-6.1/logs/rsl_rl/실제실행폴더/model_299.pt"
```

`--print-command` 통과는 실행 인자 검사일 뿐이다. 실제 GPU 시험에서는 학습 반복 완료·체크포인트 저장·정책 재생까지 확인해야 한다.

## WSL에서 확인한 범위

2026-10-20 WSL Ubuntu 24.04.5 / Python 3.12.3 / Bash 5.2.21에서 `99_self_check.py` 16개 검사와 보상 예제의 CSV 출력을 확인했다. **Ubuntu용 Lab 전체 의존성 설치와 GPU 실행은 이번 환경에서 시험하지 않았다.** 네이티브 Ubuntu RTX PC에서 위 설치·실행 단계의 후속 확인이 필요하다. [검증 보고서](VALIDATION.md)에 시험 범위와 미검증 항목을 적었다.
