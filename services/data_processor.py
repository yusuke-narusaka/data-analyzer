import pandas as pd

class DataProcessor:
    @staticmethod
    def summarize_dynamic_data(data_list, target_column='数量'):
        """
        JSON形式のデータリストから、指定された列の合計を集計する。
        """
        if not data_list:
            return [], []
        
        # content(JSON)の中身を取り出してDataFrameにする
        df = pd.DataFrame([d.content for d in data_list])
        
        # 指定した列が存在し、かつ数値計算可能か確認
        if target_column in df.columns:
            # 数値に変換（変換できないものはNaNになる）
            df[target_column] = pd.to_numeric(df[target_column], errors='coerce')
            
            # カテゴリ列（もしあれば）で集計。なければ全合計。
            group_col = 'カテゴリ' if 'カテゴリ' in df.columns else None
            
            if group_col:
                summary = df.groupby(group_col)[target_column].sum().reset_index()
                return summary[group_col].tolist(), summary[target_column].tolist()
        
        return [], []