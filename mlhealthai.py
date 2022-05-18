import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report

class Ml:
  def __init__(self):
    pass

  def build_rf(self):
    dataset = pd.read_excel("C:\\Users\\prati\\Downloads\\patient_data_may18_v2.xlsx")
    print(dataset.head())
    dataset = dataset[['admission',  'age', 'HEMOGLOBIN', 'PLATELET', 'CREATININE', 'PACKED CELL VOLUME', 'MCV', 'RBC', 'MCH']]
    print(dataset.head())
    print(dataset.dtypes)
    # dataset['HEMOGLOBIN'] = dataset['HEMOGLOBIN'].str.replace('%|.', '')
    # dataset['PACKED CELL VOLUME'] = dataset['PACKED CELL VOLUME'].str.replace('%|.', '')
    dataset = dataset.replace('%', '', regex=True)
    # dataset = dataset.replace('/.', '', regex=True)
    dataset = dataset.replace('\n','', regex=True)
    dataset = dataset.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    dataset = dataset.applymap(lambda x: x[:-1] if isinstance(x, str) and x[-1]=="." else x)
    dataset = dataset.replace('', np.nan, regex=True)
    dataset = dataset.astype(float)
    print(dataset.head())
    print(dataset.groupby('admission', as_index=False)['PLATELET'].mean())
    print(dataset.groupby('admission', as_index=False)['HEMOGLOBIN'].mean())
    print(dataset.groupby('admission', as_index=False)['CREATININE'].mean())
    print(dataset.groupby('admission', as_index=False)['MCV'].mean())
    print(dataset.groupby('admission', as_index=False)['RBC'].mean())
    print(dataset.groupby('admission', as_index=False)['MCH'].mean())
    # return
    # dataset.loc[dataset["admission"] == 0.0, "PLATELET"] = 1
    dataset.fillna(dataset.mean(), inplace=True)
    print(dataset.head())
    # To calculate mean use imputer class
    # imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
    # imputer = imputer.fit(dataset)
  
    # dataset = imputer.transform(dataset)

    X = dataset.iloc[:, 1:].values
    y = dataset.iloc[:, 0].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Feature Scaling
    from sklearn.preprocessing import StandardScaler

    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    from sklearn.ensemble import RandomForestClassifier
    classifier = RandomForestClassifier(n_estimators=50, random_state=0)
    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)

    from sklearn import metrics

    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    target_names = ['0', '1']
    print(classification_report(y_test, y_pred, target_names=target_names))
if __name__ == "__main__":    
    # file = "C:\\Users\\prati\\Documents\\health_ai_doc\\data\\p2_txt - Copy"
    ml = Ml()
    ml.build_rf()