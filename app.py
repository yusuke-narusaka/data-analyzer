import os
from flask import Flask, render_template, request, redirect, url_for
from database import db, DynamicData
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dx_dynamic.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'dynamic-dx-secret'

db.init_app(app)

with app.app_context():
    if not os.path.exists('uploads'): os.makedirs('uploads')
    db.create_all()

@app.route('/')
def index():
    data_list = DynamicData.query.all()
    headers = []
    rows = []
    if data_list:
        headers = list(data_list[0].content.keys())
        rows = [d.content for d in data_list]
    return render_template('index.html', headers=headers, rows=rows)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        df = df.fillna('')
        for _, row in df.iterrows():
            new_data = DynamicData(content=row.to_dict())
            db.session.add(new_data)
        db.session.commit()
    return redirect(url_for('index'))

# --- 強化版：多機能グラフ表示ページ ---
@app.route('/chart')
def show_chart():
    label_col = request.args.get('label_col')
    value_cols = request.args.getlist('value_cols')
    chart_type = request.args.get('chart_type', 'bar')
    
    data_list = DynamicData.query.all()
    if not data_list or not label_col or not value_cols:
        return "データ、集計軸、または数値項目の指定が足りません。"

    # 【重要】もし数値項目の中に「集計軸」と同じ名前があれば除外する
    value_cols = [v for v in value_cols if v != label_col]
    
    # もし除外した結果、数値項目が空になったらエラーを防ぐ
    if not value_cols:
        return f"エラー：数値項目に「{label_col}」以外を選択してください。"

    df = pd.DataFrame([d.content for d in data_list])
    
    # 数値型に変換
    for col in value_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 集計処理（ここでエラーが起きていたのを、上の重複排除で回避します）
    summary = df.groupby(label_col)[value_cols].sum().reset_index()
    
    labels = summary[label_col].tolist()
    datasets = []
    for col in value_cols:
        datasets.append({
            'label': col,
            'data': summary[col].tolist()
        })

    return render_template('chart.html', 
                           labels=labels, 
                           datasets=datasets, 
                           label_name=label_col, 
                           chart_type=chart_type)
@app.route('/clear')
def clear_data():
    DynamicData.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)