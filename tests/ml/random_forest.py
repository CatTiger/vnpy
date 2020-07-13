import pandas as pd
from sklearn.datasets import load_wine, load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn import metrics

'''
调参步骤
1、{'n_estimators':60}
2、{'max_depth':13, 'min_samples_split': 110}
3、{'min_samples_leaf':20, 'min_samples_split': 120}
4、{'max_features':7}
'''

wine = load_wine()
Xtrain, Xtest, Ytrain, Ytest = train_test_split(wine.data, wine.target, test_size=0.3)

clf = DecisionTreeClassifier(random_state=0)
clf = clf.fit(Xtrain, Ytrain)
score_c = clf.score(Xtest, Ytest)

print('Tree:{}'.format(score_c))