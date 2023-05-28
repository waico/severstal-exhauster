import os
import mlflow
import pandas as pd

from pycaret.classification import *


class SecondModel(mlflow.pyfunc.PythonModel):

    def predict(self, context, model_input):

        y_test = model_input

        X_test = pd.read_parquet('storage/X_test.parquet')
        X_test = X_test.rename(columns={'ЭКСГАУСТЕР 4. ТОК РОТОРА2':'ЭКСГАУСТЕР 4. ТОК РОТОРА 2'})
        X_test_r = X_test.rolling('60T').mean()

        X_test[y_test.columns] = 0

        for target in sorted(y_test.columns):
            tn = target.replace('/', '___')
            if os.path.exists(f'storage/models/1-1/{tn}.pkl'):
                print(target)
                
                exh_n = self.get_exhauster(target)
                features = [s for s in  X_test_r.columns if f'ЭКСГАУСТЕР {exh_n}' in s]
                X_test_r_f = self.generate_features(X_test_r, features)
                
                model = load_model(f'storage/models/1-1/{tn}', verbose=False)
                pr = predict_model(model, X_test_r_f)
                X_test[target] = pr['prediction_label']

        X_test[y_test.columns].drop(columns='DT').reset_index()
        return X_test


    def get_exhauster(self, target):
        name = target.split('_')[1]
        number = int(name[-1])
        return number


    def generate_features(self, X, features, window_diff=24):
        #
        X = X.copy()
        
        # Медианная температура и отклонения от нее
        temp_cols = [s for s in features if ('ТЕМПЕРАТУРА' in s) and (not s.startswith('Y'))]
        X['{0}. ВИБРАЦИЯ МЕДИАНА'.format(temp_cols[0].split('.')[0])] = X[temp_cols].median()
        
        temp_cols_diff = [f'{s} ОТКЛОНЕНИЕ' for s in features if 'ТЕМПЕРАТУРА' in s]
        X[temp_cols_diff] = X[temp_cols] - X[temp_cols].median()
        
        
        # Медианная вибрация и отклонения от нее
        vibr_cols = [s for s in features if 'ВИБРАЦИЯ' in s]
        X['{0}. ВИБРАЦИЯ МЕДИАНА'.format(vibr_cols[0].split('.')[0])] = X[vibr_cols].median()

        vibr_cols_diff = [f'{s} ОТКЛОНЕНИЕ' for s in features if 'ВИБРАЦИЯ' in s]
        X[vibr_cols_diff] = X[vibr_cols] - X[vibr_cols].median()
        
        return X


if __name__ == "__main__":

    second_model = SecondModel()
    mlflow.pyfunc.save_model("second_model", python_model=second_model)

