"""실습 2: 배치를 바꾸고 RtxCamera와 CameraSensor로 RGB·깊이를 저장한다."""
import argparse  # 명령행 seed와 프레임 수를 읽는다.
import json  # 실험 조건을 메타데이터로 저장한다.
import random  # 재현 가능한 상자 배치와 색을 생성한다.

parser = argparse.ArgumentParser()  # 명령행 해석기를 만든다.
parser.add_argument("--seed", type=int, default=7)  # 같은 seed는 같은 배치와 색을 만든다.
parser.add_argument("--frames", type=int, default=180)  # 센서 준비를 포함한 업데이트 횟수다.
parser.add_argument("--headless", action="store_true")  # 화면 창만 생략하고 RTX 센서는 계속 사용한다.
args = parser.parse_args()  # 입력을 객체에 저장한다.
if args.frames < 30:  # 카메라 초기화 전에 읽는 실수를 줄인다.
    parser.error("--frames must be at least 30 for camera warmup")  # GPU 초기화 전에 오류를 낸다.

from isaacsim import SimulationApp  # omni·pxr를 불러오기 전에 Kit을 준비한다.

# VRAM 사용을 줄이는 작은 창 설정이며 공식 최소 GPU 사양을 대체하지 않는다.
app = SimulationApp({"headless": args.headless, "width": 640, "height": 360,
                     "anti_aliasing": 0, "multi_gpu": False})
try:  # 실패한 경우에도 앱을 정리한다.
    import numpy as np  # 깊이 배열과 보기용 명암 영상을 처리한다.
    import omni.timeline  # 센서 갱신에 필요한 시간 재생을 제어한다.
    from PIL import Image  # RGB와 깊이 미리보기를 PNG로 저장한다.
    from isaacsim.sensors.experimental.rtx import CameraSensor, RtxCamera  # 6.1 카메라 정의와 데이터 접근 API다.
    from scene_tools import create_scene, make_box, output_directory, point_camera  # 공통 장면 생성 함수를 사용한다.
    from omni.kit.viewport.utility import get_active_viewport  # 화면에 카메라 시점을 표시한다.

    stage = create_scene()  # 바닥과 조명을 만든다.
    rng = random.Random(args.seed)  # 전역 난수 상태와 분리된 생성기를 쓴다.
    boxes = []  # 결과 이미지와 함께 상자 배치 조건을 기록한다.
    for index in range(5):  # 작은 장면을 위해 상자 다섯 개를 만든다.
        position = (rng.uniform(-1.4, 1.4), rng.uniform(-1.0, 1.0), 0.25)  # 바닥에 놓인 중심 위치다.
        color = tuple(rng.uniform(0.1, 0.95) for _ in range(3))  # 각 RGB 성분을 무작위로 만든다.
        make_box(stage, f"/World/Box_{index}", position, (0.5, 0.5, 0.5), color)  # mass가 없으므로 고정 관찰 대상이다.
        boxes.append({"position_m": position, "color": color})  # 이 실행의 배치와 색을 보존한다.
    author = RtxCamera("/World/Camera", tick_rate=0.0)  # RTX 카메라 prim을 정의한다.
    point_camera(stage, "/World/Camera", (3.5, -5.0, 3.5), (0, 0, 0.2))  # 장면을 비스듬히 내려다본다.
    sensor = CameraSensor(author, resolution=(320, 240), annotators=["rgb", "distance_to_image_plane"])  # 색과 이미지 평면 깊이를 요청한다.
    viewport = get_active_viewport()  # 사용 가능한 화면을 조회한다.
    if viewport is not None:  # 창이 없는 실행에서도 동작하도록 분기한다.
        viewport.camera_path = "/World/Camera"  # 센서 시점과 관찰 화면을 일치시킨다.
    out = output_directory("02_camera")  # 이번 촬영의 고유 결과 폴더다.
    stage.GetRootLayer().Export(str(out / "scene.usda"))  # 장면을 다시 열 수 있게 저장한다.
    timeline = omni.timeline.get_timeline_interface()  # 재생 제어기를 얻는다.
    timeline.play()  # 센서 프레임 갱신을 시작한다.
    rgb = depth = None  # 유효한 프레임을 아직 받지 않았음을 표시한다.
    for frame in range(args.frames):  # 요청한 횟수 동안 프레임을 진행한다.
        if not app.is_running():  # 사용자가 창을 닫으면 중단한다.
            break  # 닫힌 앱을 갱신하지 않는다.
        app.update()  # 렌더러와 센서를 갱신한다.
        if frame >= 29:  # 최소 준비 구간 이후부터 데이터를 읽는다.
            rgb_data, _ = sensor.get_data("rgb")  # Warp RGB 배열과 부가 정보 중 배열을 사용한다.
            depth_data, _ = sensor.get_data("distance_to_image_plane")  # 광선 길이가 아닌 평면까지 깊이다.
            if rgb_data is not None and depth_data is not None:  # 두 출력이 모두 준비된 경우에만 보관한다.
                rgb = rgb_data.numpy()  # GPU 배열을 CPU 배열로 옮긴다.
                depth = depth_data.numpy()  # 깊이를 m 단위 배열로 옮긴다.
    if rgb is None or depth is None or rgb.size == 0 or depth.size == 0:  # 빈 출력은 촬영 성공이 아니다.
        raise RuntimeError("Camera returned no frame. Inspect RTX errors or increase --frames.")
    if rgb.shape[:2] != (240, 320) or rgb.shape[-1] not in (3, 4):  # 높이·너비·색상 채널 수를 확인한다.
        raise RuntimeError(f"Unexpected RGB shape: {rgb.shape}")
    if rgb.dtype != np.uint8:  # PNG 변환에서 색 범위가 조용히 깨지는 것을 막는다.
        raise RuntimeError(f"Expected uint8 RGB, got {rgb.dtype}; check the installed sensor API.")
    Image.fromarray(rgb[..., :3]).save(out / "rgb.png")  # 알파가 있으면 제외하고 RGB를 저장한다.
    np.save(out / "depth_m.npy", depth)  # 분석용 원본 깊이는 변환 없이 저장한다.
    preview = np.clip(np.nan_to_num(depth, nan=5.0, posinf=5.0, neginf=0.0), 0, 5)  # 미리보기만 0~5 m로 제한한다.
    Image.fromarray((255 * preview.squeeze() / 5).astype(np.uint8)).save(out / "depth_preview.png")  # 거리 범위를 0~255 명암으로 바꾼다.
    metadata = {"seed": args.seed, "resolution": [320, 240], "depth_unit": "metre", "depth_type": "distance_to_image_plane", "boxes": boxes}  # 해석에 필요한 조건을 모은다.
    (out / "scene_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")  # 조건을 사람이 읽을 수 있게 저장한다.
    timeline.stop()  # 촬영을 마치고 시간 재생을 멈춘다.
    print(f"Saved RGB {rgb.shape}, depth {depth.shape}: {out}")  # 크기와 저장 위치를 출력한다.
finally:  # 성공·실패에 상관없이 자원을 정리한다.
    app.close()  # 센서와 Kit을 종료한다.
