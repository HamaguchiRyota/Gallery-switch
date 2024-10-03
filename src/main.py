import pygame
import sys
import json
from ffpyplayer.player import MediaPlayer

# 初期化
pygame.init()

# 画面サイズを設定
screen = pygame.display.set_mode((1280, 720))

# JSONファイルからメディア情報を読み込み
with open('media.json', 'r') as f:
    media_data = json.load(f)

# 画像のパスとタイトルを読み込み
images = [
    {"surface": pygame.image.load(item["path"]), "title": item["title"]}
    for item in media_data["images"]
]

# 動画のパス、タイトル、フレームレートを読み込み
videos = []
for item in media_data["videos"]:
    videos.append({"path": item["path"], "title": item["title"], "player": None, "fps": 30})

# 現在表示されているメディアのインデックス
current_media_index = 0

# 現在表示しているのが画像か動画かを判定 (True: 画像, False: 動画)
is_image = True

def get_video_frame(video_player):
    """動画フレームを取得してpygame用に変換する"""
    frame, val = video_player.get_frame()
    if val == 'eof':  # 動画が終わったらループ再生
        video_player.seek(0, relative=False)
        frame, val = video_player.get_frame()

    if frame is None:
        return None

    img, t = frame
    img = pygame.image.frombuffer(img.to_bytearray()[0], img.get_size(), "RGB")
    return img

def get_video_fps(video_path):
    """動画のフレームレートを取得する"""
    player = MediaPlayer(video_path)
    metadata = player.get_metadata()
    player.close_player()
    return metadata.get('fps', 15)  # デフォルトで30fpsを設定

# 動画のフレームレートを設定
for video in videos:
    video["fps"] = get_video_fps(video["path"])

# メインループ
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # テンキーによる画像・動画切り替え
            if pygame.K_KP1 <= event.key <= pygame.K_KP6:
                current_media_index = event.key - pygame.K_KP1
                is_image = True  # 画像に切り替え
                # 現在再生中の動画を停止
                if videos[current_media_index]["player"]:
                    videos[current_media_index]["player"].close_player()
                    videos[current_media_index]["player"] = None
            elif pygame.K_KP7 <= event.key <= pygame.K_KP9:
                # 新しい動画のプレーヤーを作成して再生開始
                new_index = event.key - pygame.K_KP7
                if new_index != current_media_index:  # 異なる動画に切り替えの場合
                    if videos[current_media_index]["player"]:
                        videos[current_media_index]["player"].close_player()  # 現在の動画を停止
                    current_media_index = new_index
                    # 新しい動画を再生
                    videos[current_media_index]["player"] = MediaPlayer(videos[current_media_index]["path"])
                else:
                    # 同じ動画の再生を最初から
                    if videos[current_media_index]["player"]:  # プレーヤーが存在する場合のみ
                        videos[current_media_index]["player"].seek(0, relative=False)
                is_image = False  # 動画に切り替え
            elif event.key == pygame.K_ESCAPE:
                running = False

    # 画面を白でクリア
    screen.fill((255, 255, 255))
    
    if is_image:
        # 現在の画像を表示
        screen.blit(images[current_media_index]["surface"], (0, 0))
        title = images[current_media_index]["title"]
    else:
        # 現在の動画フレームを表示
        try:
            frame_surface = get_video_frame(videos[current_media_index]["player"])
            if frame_surface:
                screen.blit(frame_surface, (0, 0))
            title = videos[current_media_index]["title"]
        except Exception as e:
            print(f"Error while getting video frame: {e}")
            is_image = True  # エラー発生時に画像に切り替え
            if videos[current_media_index]["player"]:
                videos[current_media_index]["player"].close_player()
                videos[current_media_index]["player"] = None

    # タイトルの表示
    font = pygame.font.Font(None, 36)
    text_surface = font.render(title, True, (0, 0, 0))
    screen.blit(text_surface, (20, 550))  # 画面下にタイトルを表示
    
    # 画面を更新
    pygame.display.flip()
    
    # FPSに基づいて待機
    if not is_image:
        clock.tick(videos[current_media_index]["fps"])  # 動画のフレームレートに合わせて待機
    else:
        clock.tick(60)  # 画像の更新速度

# 終了処理
for video in videos:
    if video["player"]:
        video["player"].close_player()
pygame.quit()
sys.exit()
