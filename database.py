from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# どんなCSV項目でもJSONとして保存できる設計に変更
class DynamicData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_date = db.Column(db.DateTime, default=datetime.now)
    content = db.Column(db.JSON)