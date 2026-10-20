#!/usr/bin/env bash
# Ubuntu용 Lab 실행기다. Windows PS1과 동일한 버전 및 과제를 사용한다.
set -euo pipefail # 명령 실패, 미정의 변수, 파이프 내부 실패에서 중단한다.
mode='' # 수행할 단계는 필수 옵션이다.
lab_dir="$HOME/pa-course/IsaacLab-6.1" # Lab 저장소와 .venv를 저장할 경로다.
num_envs=1 # 8 GB 소형 실습은 환경 1개부터 시작한다.
iterations=300 # PPO 갱신 횟수이며 학습 성공 보장이 아니다.
checkpoint=latest # 재현할 때는 실제 학습 파일 경로로 교체한다.
viz=kit # none은 창을 생략하지만 GPU는 여전히 필요하다.
preview=0 # 1이면 실행하지 않고 인자만 출력한다.
commit=ae37b028ea415c91ea2bc32609efcd759ed2b974 # 수업의 Sim 6.1 대응 EA 커밋이다.
while (($#)); do # 옵션을 왼쪽부터 하나씩 읽는다.
    case "$1" in # 지원하는 이름만 허용한다.
        --print-command) preview=1; shift ;; # 값 없는 미리보기 옵션이다.
        --mode|--lab-dir|--num-envs|--iterations|--checkpoint|--viz)
            (($# >= 2)) || { echo "Missing value: $1" >&2; exit 2; } # 옵션 값 누락을 검사한다.
            case "$1" in # 각 값의 공백을 보존한다.
                --mode) mode="$2" ;; # 실행할 단계를 저장한다.
                --lab-dir) lab_dir="$2" ;; # Lab 경로를 저장한다.
                --num-envs) num_envs="$2" ;; # 환경 수를 저장한다.
                --iterations) iterations="$2" ;; # 갱신 횟수를 저장한다.
                --checkpoint) checkpoint="$2" ;; # 정책 파일이나 선택자를 저장한다.
                --viz) viz="$2" ;; # 화면 모드를 저장한다.
            esac
            shift 2 ;; # 이름과 값을 처리했으므로 두 항목을 소비한다.
        *) echo "Unknown option: $1" >&2; exit 2 ;; # 오타를 무시하지 않는다.
    esac
done
case "$mode" in setup|list|random|train|play) ;; *) echo 'Use --mode setup|list|random|train|play' >&2; exit 2 ;; esac # 단계 이름을 검증한다.
case "$viz" in kit|none) ;; *) echo 'Use --viz kit|none' >&2; exit 2 ;; esac # 화면 모드를 검증한다.
[[ "$num_envs" =~ ^[1-9][0-9]{0,3}$ ]] && ((num_envs <= 4096)) || { echo 'Invalid --num-envs' >&2; exit 2; } # 정수 범위를 검사한다.
[[ "$iterations" =~ ^[1-9][0-9]{0,5}$ ]] && ((iterations <= 100000)) || { echo 'Invalid --iterations' >&2; exit 2; } # 갱신 횟수 범위를 검사한다.
args=(run --frozen --extra isaacsim isaaclab) # 배열로 인자를 전달해 셸 재해석을 피한다.
task=(--task Isaac-Cartpole --num_envs "$num_envs") # 수업 과제와 환경 수를 지정한다.
backend=(physics=isaacsim_physx --viz "$viz") # 강의의 물리 엔진과 화면 모드다.
play_options=() # 창 없는 재생은 기존 장치 및 실행 속도를 유지한다.
if [[ "$mode" == play && "$viz" == kit ]]; then # 화면 재생은 마우스 외력 실습용으로 구성한다.
    play_options=(--device cpu --real-time '--kit_args=--enable omni.physx.ui') # CPU 물리와 실시간 재생을 선택하고 물리 마우스 UI를 자동 활성화한다.
fi
case "$mode" in # 단계별 공식 CLI 인자를 구성한다.
    setup) args=(sync --frozen --extra isaacsim) ;; # 잠금 파일의 의존성을 설치한다.
    list) args=(run --frozen --extra isaacsim python scripts/environments/list_envs.py --show_presets) ;; # 이 EA에는 list_envs 하위 명령이 없어 공식 스크립트를 직접 실행한다.
    random) args+=(random_agent "${task[@]}" "${backend[@]}") ;; # 무작위 정책을 실행한다.
    train) args+=(train --rl_library rsl_rl "${task[@]}" --seed 42 --max_iterations "$iterations" "${backend[@]}") ;; # PPO를 학습한다.
    play) args+=(play --rl_library rsl_rl "${task[@]}" --seed 123 --checkpoint "$checkpoint" "${backend[@]}" "${play_options[@]}") ;; # 저장된 정책을 재생한다.
esac
if ((preview)); then # 미리보기는 Git이나 uv를 실행하지 않는다.
    python3.12 - "$lab_dir" "$commit" "${args[@]}" <<'PY'
import json  # JSON 출력용 표준 라이브러리다.
import sys  # Bash가 전달한 인자 배열을 읽는다.
print(json.dumps(dict(cwd=sys.argv[1], commit=sys.argv[2], executable="uv", arguments=sys.argv[3:])))  # Windows와 같은 구조로 출력한다.
PY
    exit 0 # 미리보기 뒤 실제 실행을 막는다.
fi
command -v git >/dev/null # Git 설치 여부를 확인한다.
command -v uv >/dev/null # uv 설치 여부를 확인한다.
if [[ "$mode" == setup && ! -e "$lab_dir" ]]; then # 새 경로에만 저장소를 만든다.
    git clone --filter=blob:none --no-checkout --branch v3.0.0-EA https://github.com/isaac-sim/IsaacLab.git "$lab_dir" # 공식 EA를 받는다.
    git -C "$lab_dir" checkout --detach "$commit" # 정확한 커밋을 선택한다.
fi
[[ -e "$lab_dir/.git" ]] || { echo 'Run --mode setup first' >&2; exit 1; } # 잘못된 작업 폴더 실행을 막는다.
actual=$(git -C "$lab_dir" rev-parse HEAD) # 현재 커밋을 조회한다.
[[ "$actual" == "$commit" ]] || { echo 'Checkout differs from the course pin' >&2; exit 1; } # 버전 혼용을 거부한다.
changes=$(git -C "$lab_dir" status --porcelain --untracked-files=no) # 로그 이외의 추적 소스 변경을 확인한다.
[[ -z "$changes" ]] || { echo 'Tracked Lab files have changes' >&2; exit 1; } # 원본 수정은 자동으로 되돌리지 않는다.
if [[ "$mode" == play && "$checkpoint" != latest && "$checkpoint" != best ]]; then # 정책 파일 경로를 검사한다.
    [[ -f "$checkpoint" ]] || { echo 'Checkpoint must be a file' >&2; exit 1; } # 없는 파일과 디렉터리를 거부한다.
    checkpoint=$(realpath -- "$checkpoint") # cd 전에 상대 경로를 절대 경로로 바꾼다.
    args=(run --frozen --extra isaacsim isaaclab play --rl_library rsl_rl "${task[@]}" --seed 123 --checkpoint "$checkpoint" "${backend[@]}" "${play_options[@]}") # 공백과 마우스 실습 설정을 보존한다.
fi
cd -- "$lab_dir" # uv가 Lab의 프로젝트 및 잠금 파일을 사용하게 한다.
exec uv "${args[@]}" # uv 종료 코드를 호출자에게 그대로 전달한다.
