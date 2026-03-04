from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json

app = Flask(__name__)

# データベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# モデル定義
class CSVData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.JSON, nullable=False)

# データベースの初期化
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # 全データを取得してリスト形式に変換
    records = CSVData.query.all()
    data_list = [record.content for record in records]
    
    # カラム名を取得（データが存在する場合のみ）
    columns = data_list[0].keys() if data_list else []
    
    return render_template('index.html', data=data_list, columns=columns)

@app.route('/import', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        try:
            # 【修正ポイント】既存のデータをすべて削除してリセットする
            db.session.query(CSVData).delete()
            db.session.commit()

            # CSV読み込み
            df = pd.read_csv(file)
            
            # 各行をJSON形式でデータベースに保存
            for _, row in df.iterrows():
                # NaN（欠損値）をNoneに変換してJSONエラーを回避
                row_dict = row.where(pd.notnull(df), None).to_dict()
                new_data = CSVData(content=row_dict)
                db.session.add(new_data)
            
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return f"エラーが発生しました: {e}"

@app.route('/chart_data')
def chart_data():
    records = CSVData.query.all()
    data_list = [record.content for record in records]
    return jsonify(data_list)

if __name__ == '__main__':
    app.run(debug=True)
