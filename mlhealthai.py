import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
# from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif

class Ml:
  def __init__(self):
    pass

  def build_rf(self):
    dataset = pd.read_excel("C:\\Users\\prati\\Downloads\\patient_data_may18_v2.xlsx")
    # print(dataset.head())
    dataset = dataset[['admission', 'age', 'gender', 'HEMOGLOBIN', 'PLATELET', 'CREATININE', 'PACKED CELL VOLUME', 'MCV', 'RBC', 'MCH', 'ESR', 'SGPT', 'CALCIUM', 'ALBUMIN', 'SGOT']]
    dataset = pd.get_dummies(dataset, columns = ['gender'])
    # print(dataset.head())
    # print(dataset.dtypes)
    # dataset['HEMOGLOBIN'] = dataset['HEMOGLOBIN'].str.replace('%|.', '')
    # dataset['PACKED CELL VOLUME'] = dataset['PACKED CELL VOLUME'].str.replace('%|.', '')     
    dataset = dataset.replace('%', '', regex=True)
    # dataset = dataset.replace('/.', '', regex=True)
    dataset = dataset.replace('\n','', regex=True)
    dataset = dataset.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    dataset = dataset.applymap(lambda x: x[:-1] if isinstance(x, str) and x[-1]=="." else x)
    dataset = dataset.replace('', np.nan, regex=True)
    dataset = dataset.astype(float)
    # print(dataset.head())
    # dict_mean = {}
    cols_for_mean = ['HEMOGLOBIN', 'age', 'PLATELET', 'CREATININE', 'PACKED CELL VOLUME', 'MCV', 'RBC', 'MCH', 'RBC', 'MCH', 'ESR', 'SGPT', 'CALCIUM', 'ALBUMIN', 'SGOT']
    for col in cols_for_mean:
      tmp_df = dataset.groupby('admission', as_index=False)[col].mean()
      # dict_mean[col] = {'0':tmp_df.iloc[0,1], '1':tmp_df.iloc[1,1]}
      dataset.loc[(dataset['admission'] == 0.0) & (np.isnan(dataset[col])), col] = tmp_df.iloc[0,1]
      dataset.loc[(dataset['admission'] == 1.0) & (np.isnan(dataset[col])), col] = tmp_df.iloc[1,1]
    # print(dict_mean)
    # print(dataset.head(50))
    # return
    dataset.fillna(dataset.mean(), inplace=True)
    # print(dataset.head())
    # To calculate mean use imputer class
    # imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
    # imputer = imputer.fit(dataset)  
    # dataset = imputer.transform(dataset)
    
    X = dataset.iloc[:, 1:].values
    y = dataset.iloc[:, 0].values   
    # kbest  = SelectKBest(f_classif, k=15)
    # X_new = kbest.fit_transform(X, y)
    # cols = kbest.get_support(indices=True)
    # new_features = dataset.iloc[:,cols]
    # print(new_features)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Feature Scaling
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    classifier = RandomForestClassifier(n_estimators=50, random_state=0)
    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)

    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    target_names = ['Non-Admission', 'Admission']
    print(classification_report(y_test, y_pred, target_names=target_names))

if __name__ == "__main__":    
    # file = "C:\\Users\\prati\\Documents\\health_ai_doc\\data\\p2_txt - Copy"
    ml = Ml()
    ml.build_rf()