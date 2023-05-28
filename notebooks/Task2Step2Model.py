from pycaret.classification import *
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import f1_score
import numpy as np

X_train = pd.read_parquet('../data/raw/X_train.parquet')
X_train.info(max_cols=2)

X_test = pd.read_parquet('../data/raw/X_test.parquet')
X_test.info(max_cols=2)

y_train = pd.read_parquet('../data/processed/y_train_fixed_M3.parquet')
y_train = y_train.astype(np.int8)
y_train.info(max_cols=2)

messages = pd.read_excel('../data/raw/messages.xlsx')
messages['target'] = 'Y_' + messages['ИМЯ_МАШИНЫ'] + '_' + messages['НАЗВАНИЕ_ТЕХ_МЕСТА']


resample_period = '60T'
X_train_r = X_train.resample(resample_period).mean()
X_train_r = X_train_r.rename(columns={'ЭКСГАУСТЕР 4. ТОК РОТОРА2':'ЭКСГАУСТЕР 4. ТОК РОТОРА 2'})

y_train_r = y_train.resample(resample_period).max()

def generate_features(X, features, window_diff=24):
    #
    X = X.copy()
    
    # Медианная температура и отклонения от нее
    temp_cols = [s for s in features if 'ТЕМПЕРАТУРА' in s]
    X['{0}. ВИБРАЦИЯ МЕДИАНА'.format(temp_cols[0].split('.')[0])] = X[temp_cols].median()
    
    temp_cols_diff = [f'{s} ОТКЛОНЕНИЕ' for s in features if 'ТЕМПЕРАТУРА' in s]
    X[temp_cols_diff] = X[temp_cols] - X[temp_cols].median()
    
    
    # Медианная вибрация и отклонения от нее
    vibr_cols = [s for s in features if 'ВИБРАЦИЯ' in s]
    X['{0}. ВИБРАЦИЯ МЕДИАНА'.format(vibr_cols[0].split('.')[0])] = X[vibr_cols].median()

    vibr_cols_diff = [f'{s} ОТКЛОНЕНИЕ' for s in features if 'ВИБРАЦИЯ' in s]
    X[vibr_cols_diff] = X[vibr_cols] - X[vibr_cols].median()
    
    return X


from sklearn.metrics import confusion_matrix
def j(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return tp / (tp + fp + fn)


for i in range(4,10):
    
    features = [s for s in  X_train_r.columns if f'ЭКСГАУСТЕР {i}' in s]
    X_train_r_f = generate_features(X_train_r, features, window_diff=24)

    targets = [s for s in  y_train_r.columns if f'№{i}' in s]
    features = [s for s in  X_train_r_f.columns if f'ЭКСГАУСТЕР {i}' in s]
    df = X_train_r_f.join(y_train_r)
    _df = df[features+targets]
    for target in targets:
        print(target)
        tn = target.replace('/', '___')
        if not os.path.exists(f'../models/task2/{tn}.pkl'):

            df_train = _df[features+[target]].copy()
            df_train = df_train[df_train[target].isin([0,2])]
            
            # window_diff = 24*14
            # diff_columns = [f'{s}_diff_{window_diff}' for s in features]
            # df_train[diff_columns] = df_train[features].diff(window_diff)
            
            N = 0.7
            train = df_train[:int(N*len(df_train))]
            test = df_train[int(N*len(df_train)):]
            if 2 not in train[target].values:
                train = pd.concat([train, test])
                exp = setup(train, target=target,
                            
                    # fold_strategy='timeseries', 
                    train_size=0.7, 
                    fold=10, 
                    session_id=42,
                    # remove_outliers=True,
                    # fix_imbalance = True,
                    verbose=-1)
                add_metric('J', name='J', score_func=j)
                model = compare_models(
                                        exclude=['svm', 'knn', 'dt', 'nb', 'dummy'], 
                                                        # include=['rf', 'lightgbm'],
                                                        sort='J', verbose=False
                )
            else:
                exp = setup(train, target=target, test_data=test,
                            
                    # fold_strategy='timeseries', 
                    train_size=0.7, 
                    fold=10, 
                    session_id=42,
                    # remove_outliers=True,
                    # fix_imbalance = True,
                    verbose=-1)
                add_metric('J', name='J', score_func=j)
                model = compare_models(
                                        exclude=['svm', 'knn', 'dt', 'nb', 'dummy'], 
                                                        # include=['rf', 'lightgbm'],
                                                        sort='J', verbose=False
                )
            
            df_pr = predict_model(model, test)
            pr = df_pr['prediction_label'].values
            pr[pr==2] = 1
            gt = df_pr[target].values 
            gt[gt==2] = 1
            try:
                j_test = j(gt, pr)
            except:
                j_test = 0
            
            df_pr_train = predict_model(model, train)
            pr = df_pr_train['prediction_label'].values
            pr[pr==2] = 1
            gt = df_pr_train[target].values 
            gt[gt==2] = 1
            try:
                j_train = j(gt, pr)
            except:
                j_train = 0
            
            
            f, ax = plt.subplots()
            (df_pr_train['prediction_label']*2).plot(alpha=0.5, ax=ax)
            (df_pr[[target]]*2).plot( ax=ax)
            (df_pr[['prediction_label' ]]*2).plot(alpha=0.2, ax=ax)
            train[target].plot(ax=ax)
            

            
            model_str = model.__str__().split('(')[0]

            starts = messages[messages['target']==target]['ДАТА_НАЧАЛА_НЕИСПРАВНОСТИ']
            ends = messages[messages['target']==target]['ДАТА_УСТРАНЕНИЯ_НЕИСПРАВНОСТИ']
            indx = messages[messages['target']==target].index
            for s, e, ind in zip(starts, ends, indx):
                if not pd.isnull(e):
                    plt.axvspan(s,e, alpha=0.3, 
                                label=messages.loc[ind]['ОПИСАНИЕ'] + ' (' + messages.loc[ind]['ДАТА_НАЧАЛА_НЕИСПРАВНОСТИ'].__str__() +' '+ messages.loc[ind]['ДАТА_УСТРАНЕНИЯ_НЕИСПРАВНОСТИ'].__str__()+ ')' , 
                                color=list(np.random.choice(range(256), size=3)/255))

            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                    fancybox=True, shadow=True, ncol=1)

            plt.title(f'{target}\nJ_train = {j_train:.2f}, J_test = {j_test:.2f}\n{model_str}')
            tn = target.replace('/', '___')
            plt.tight_layout()
            plt.savefig(f'../figs/model2/{tn}_features.png')

            final = finalize_model(model)
            save_model(final, f'../models/task2/{tn}')
