"""실습 1: 질량이 다른 상자를 같은 높이에서 떨어뜨리고 높이를 기록한다."""
import argparse  # 터미널에서 높이, 중력, 프레임 수를 받는다.
import csv  # 물리 스텝별 위치를 표로 저장한다.
import math  # 유효한 수인지 검사하고 자유낙하 시간을 계산한다.

parser = argparse.ArgumentParser()  # 명령행 옵션 해석기를 만든다.
parser.add_argument("--height", type=float, default=2.0)  # 상자 중심의 시작 높이(m)다.
parser.add_argument("--gravity", type=float, default=9.81)  # 아래쪽 중력 가속도의 크기(m/s²)다.
parser.add_argument("--frames", type=int, default=600)  # 앱 업데이트 횟수로 물리 스텝 수와 다를 수 있다.
parser.add_argument("--headless", action="store_true")  # 창 없이 실행하되 GPU 요구는 유지한다.
args = parser.parse_args()  # 입력값을 args 객체에 저장한다.
if not math.isfinite(args.height) or args.height <= 0.25:  # 반변 0.25 m인 상자가 바닥 위에서 출발해야 한다.
    parser.error("--height must be finite and greater than 0.25 m")  # Sim 시작 전에 잘못된 높이를 거부한다.
if not math.isfinite(args.gravity) or args.gravity <= 0 or args.frames < 1:  # 0·음수·무한대 중력과 빈 실행을 막는다.
    parser.error("--gravity must be positive and finite; --frames must be positive")  # 잘못된 입력을 설명한다.

from isaacsim import SimulationApp  # 다른 omni/pxr 모듈보다 먼저 앱을 초기화해야 한다.

# 작은 창, AA 끄기, 단일 GPU는 VRAM 사용을 줄이기 위한 시작 설정이다.
app = SimulationApp({"headless": args.headless, "width": 640, "height": 360,
                     "anti_aliasing": 0, "multi_gpu": False})
try:  # 이후 예외가 발생해도 finally에서 앱을 종료한다.
    import omni.timeline  # 물리 시간의 재생과 정지를 제어한다.
    from isaacsim.core.experimental.prims import RigidPrim  # 두 강체의 세계 좌표를 함께 읽는다.
    from isaacsim.core.simulation_manager import SimulationManager  # 물리 이벤트 콜백을 관리한다.
    from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents  # 물리 스텝 직후 이벤트를 선택한다.
    from pxr import UsdGeom  # USD 카메라를 정의한다.
    from scene_tools import create_scene, make_box, output_directory, point_camera  # 공통 장면 함수를 사용한다.
    from omni.kit.viewport.utility import get_active_viewport  # 화면에 표시할 카메라를 고른다.

    stage = create_scene(args.gravity)  # 바닥, 조명, 중력을 포함한 장면을 만든다.
    make_box(stage, "/World/LightCube", (-0.7, 0, args.height), (0.5, 0.5, 0.5), (0.1, 0.5, 0.9), mass=1.0)  # 파란 1 kg 상자다.
    make_box(stage, "/World/HeavyCube", (0.7, 0, args.height), (0.5, 0.5, 0.5), (0.9, 0.4, 0.1), mass=10.0)  # 주황 10 kg 상자다.
    bodies = RigidPrim(paths=["/World/LightCube", "/World/HeavyCube"])  # 배열 순서는 CSV의 열 순서와 같다.
    UsdGeom.Camera.Define(stage, "/World/Overview")  # 관찰용 카메라를 만든다.
    point_camera(stage, "/World/Overview", (5, -7, 4), (0, 0, 1))  # 두 상자가 보이도록 시점을 정한다.
    viewport = get_active_viewport()  # 화면이 없는 경우 None일 수 있다.
    if viewport is not None:  # headless에서도 이 조건을 안전하게 통과한다.
        viewport.camera_path = "/World/Overview"  # 관찰 카메라를 화면에 연결한다.
    out = output_directory("01_drop")  # 실행마다 별도의 결과 폴더를 만든다.
    stage.GetRootLayer().Export(str(out / "initial_scene.usda"))  # 움직이기 전 장면을 저장한다.
    rows = []  # 시간, 가벼운 상자 z, 무거운 상자 z를 모은다.
    elapsed = 0.0  # 실제 물리 스텝의 dt를 누적할 변수다.

    def record_step(dt, context):  # 엔진이 물리 계산을 끝낼 때 호출한다. context는 API가 전달하는 문맥이다.
        global elapsed  # 콜백 밖의 누적 시각을 갱신한다.
        elapsed += float(dt)  # 화면 프레임 수 대신 물리 시간을 누적한다.
        positions, _ = bodies.get_world_poses()  # 위치와 자세 중 위치만 사용한다.
        values = positions.numpy()  # Warp 배열을 CPU NumPy 배열로 옮겨 CSV 숫자로 읽는다.
        rows.append((elapsed, float(values[0, 2]), float(values[1, 2])))  # z축 성분만 기록한다.

    callback = SimulationManager.register_callback(record_step, IsaacEvents.POST_PHYSICS_STEP)  # 물리 계산 직후를 구독한다.
    timeline = omni.timeline.get_timeline_interface()  # 전역 재생 제어기를 얻는다.
    timeline.play()  # 물리 시뮬레이션을 시작한다.
    for frame in range(args.frames):  # 정해진 횟수 동안 앱을 갱신한다.
        if not app.is_running():  # 사용자가 창을 닫았다면 반복을 끝낸다.
            break  # 닫힌 앱에 update를 호출하지 않는다.
        app.update()  # 물리·렌더·이벤트 처리를 진행한다.
    SimulationManager.deregister_callback(callback)  # 사용이 끝난 이벤트 구독을 해제한다.
    timeline.stop()  # 파일을 쓰기 전에 재생을 멈춘다.
    if not rows:  # 초기화 실패를 빈 CSV의 성공처럼 보이게 하지 않는다.
        raise RuntimeError("No physics samples. Check physics startup errors in the console.")
    with (out / "heights.csv").open("w", newline="", encoding="utf-8") as stream:  # OS에 상관없이 CSV를 연다.
        writer = csv.writer(stream)  # 쉼표와 줄바꿈 처리를 CSV 모듈에 맡긴다.
        writer.writerow(["simulation_seconds", "mass_1kg_z_m", "mass_10kg_z_m"])  # 단위를 열 이름에 적는다.
        writer.writerows(rows)  # 측정한 모든 물리 스텝을 저장한다.
    expected = math.sqrt(2 * (args.height - 0.25) / args.gravity)  # 상자 바닥이 지면에 닿는 해석적 시간이다.
    print(f"Expected first contact without drag: approximately {expected:.3f} s")  # 측정값과 비교할 기준이다.
    print(f"Samples: {len(rows)}, last heights: {rows[-1][1:]}; output: {out}")  # 데이터 개수와 저장 위치를 알린다.
finally:  # 정상 종료와 예외 모두 처리한다.
    app.close()  # Kit과 GPU 자원을 정리한다.
