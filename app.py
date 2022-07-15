import os
from flask import send_from_directory
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session
import detect_faces as df
import config


# Flaskオブジェクトの生成
app = Flask(__name__)
app.secret_key = 'haruthon'


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/movie")
def movie():
    return render_template("movie.html")


# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = './uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif', 'mp4', 'mov'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# def allwed_file(filename):
#     # .があるかどうかのチェックと、拡張子の確認
#     # OKなら１、だめなら0
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ファイルを受け取る方法の指定


@app.route('/result', methods=['GET', 'POST'])
def uploads_file():
    # リクエストがポストかどうかの判別
    if request.method == 'POST':
        # ファイルがなかった場合の処理
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        # データの取り出し
        file = request.files['file']
        # ファイル名がなかった時の処理
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        # # ファイルのチェック
        # if file and allwed_file(file.filename):
        # 危険な文字を削除（サニタイズ処理）
        filename = secure_filename(file.filename)
        # ファイルの保存
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # アップロード後のページに転送
        # return redirect(url_for('uploaded_file', filename=filename))

    emotion_list = df.make_emotion_list()
    chicken_rate_list = df.make_chicken_rate_list(emotion_list=emotion_list)
    a1 = int(chicken_rate_list[0])
    a2 = int(chicken_rate_list[1])
    a3 = int(chicken_rate_list[2])
    return render_template("result.html", a1=a1, a2=a2, a3=a3)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, use_debugger=False)
