# scripts/fit.py

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from category_encoders import CatBoostEncoder
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from catboost import CatBoostClassifier
from sqlalchemy import create_engine
from sklearn.linear_model import LogisticRegression
import os
import yaml
import os
import joblib
import pickle

# обучение модели
def fit_model():
	# Прочитайте файл с гиперпараметрами params.yaml
    with open('params.yaml', 'r') as fd:
            params = yaml.safe_load(fd)
	# загрузите результат предыдущего шага: inital_data.csv
    data = pd.read_csv('data/initial_data.csv')
	# реализуйте основную логику шага с использованием гиперпараметров
    username = 'mle_20240325_f5ecb5f812'
    password = '63b50333a1394482b115682aef9b9473'
    host = 'rc1b-uh7kdmcx67eomesf.mdb.yandexcloud.net'
    port = '6432'
    db = 'playground_mle_20240325_f5ecb5f812'
    conn = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db}', connect_args={'sslmode':'require'})

    # обучение модели
    cat_features = data.select_dtypes(include='object')
    potential_binary_features = cat_features.nunique() == 2

    binary_cat_features = cat_features[potential_binary_features[potential_binary_features].index]
    other_cat_features = cat_features[potential_binary_features[~potential_binary_features].index]
    num_features = data.select_dtypes(['float'])

    preprocessor = ColumnTransformer(
        [
        ('binary', OneHotEncoder(drop=params['one_hot_drop']), binary_cat_features.columns.tolist()),
        ('cat', OneHotEncoder(drop=params['one_hot_drop']), other_cat_features.columns.tolist()),
        ('num', StandardScaler(), num_features.columns.tolist())
        ],
        remainder='drop',
        verbose_feature_names_out=False
    )

    model = LogisticRegression(C = params['c'], penalty = params['penalty'])

    pipeline = Pipeline(
        [
            ('preprocessor', preprocessor),
            ('model', model)
        ]
    )
    pipeline.fit(data, data[params['target_col']]) 
    conn.dispose()
	# сохраните обученную модель в models/fitted_model.pkl
    os.makedirs('models', exist_ok=True)
    with open("models/fitted_model.pkl", "wb") as f:
        pickle.dump(pipeline, f)
        
if __name__ == '__main__':
	fit_model()