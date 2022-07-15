from typing import Type
import cv2
import config


def add_emotion(frame, emotion_list, n, initialize, scale_factor, flag):
    height, width, channels = frame.shape

    # jpgに変換 画像ファイルをインターネットを介してAPIで送信するのでサイズを小さくしておく
    small = cv2.resize(frame, (int(width * scale_factor),
                       int(height * scale_factor)))
    ret, buf = cv2.imencode('.jpg', small)

    # Amazon RekognitionにAPIを投げる
    rekognition = config.config_AWS()
    response = rekognition.detect_faces(
        Image={'Bytes': buf.tobytes()}, Attributes=['ALL'])
    i = 1  # 個別の計算で使用

    count = 0
    for face in response['FaceDetails']:
        emothions = face['Emotions']

        boundingBox = face['BoundingBox']
        box_height = int(boundingBox['Height']*height)
        box_left = int(boundingBox['Left']*width)
        box_top = int(boundingBox['Top']*height)
        box_width = int(boundingBox['Width']*width)
        # box_image = pil_image.crop((box_left, box_top, box_left + box_width, box_top+ box_height))
        box_image = frame[box_top: box_top + box_height, box_left: box_left + box_width]
        print(flag)
        if flag == 0:
            cv2.imwrite('static/css/images/chart_' + str(count) + '.png', box_image)
        count = count + 1

        if not initialize:
            emotion_list.append([])  # 初期人数分の空配列を作成

        if len(emotion_list) >= i:  # 初期人数以上の人数を検知した場合は処理しない
            for per_emothions in emothions:  # 個々のびびり度を計算
                if per_emothions['Type'] == "SAD" or per_emothions['Type'] == "FEAR" or per_emothions['Type'] == "CONFUSED" or per_emothions['Type'] == "SURPRISED":
                    emotion_list[i-1].append(per_emothions['Confidence'])
        i += 1


def make_chicken_rate_list(emotion_list):
    chicken_rate_list = []
    for i in range(len(emotion_list)):
        chicken_rate = sum(emotion_list[i])/len(emotion_list[i]) # i+1人目のビビり度 = chicken_rate
        chicken_rate_list.append(chicken_rate)
    return chicken_rate_list


def make_emotion_list():
    scale_factor = .15
    video_path = "./uploads/sample.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("例外が発生しました")

    read_fps = cap.get(cv2.CAP_PROP_FPS) # 元のfps
    fps = 1  # 希望のfps（動画1秒あたり何枚切り出して処理したいか）
    thresh = read_fps / fps  # フレーム何枚につき1枚処理するか
    frame_counter = 0

    # digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    initialize = False  # 初期処理
    emotion_list = []  # 4人っていう設定
    n = 0  # フレーム計算で使用

    flag = 0
    isContinued = True
    while isContinued:
        ret, frame = cap.read()
        if ret:
            frame_counter += 1
            if (frame_counter >= thresh):  # フレームカウントがthreshを超えたら処理する

                add_emotion(
                    frame=frame,
                    emotion_list=emotion_list,
                    n=n,
                    initialize=initialize,
                    scale_factor=scale_factor,
                    flag=flag
                )
                flag = 1
                n += 1
                frame_counter = 0  # フレームカウントを0に戻す
                initialize = True

        else:
            isContinued = False

    return emotion_list


if __name__ == '__main__':
    emotion_list = make_emotion_list()
    chicken_rate_list = make_chicken_rate_list(emotion_list=emotion_list)
