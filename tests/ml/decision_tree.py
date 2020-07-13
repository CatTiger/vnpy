import pandas as pd
from sklearn.datasets import load_wine, load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn import metrics
import graphviz

wine = load_wine()
# print(pd.concat([pd.DataFrame(wine.data), pd.DataFrame(wine.target)], axis=1))
xtrain, xtest, ytrain, ytest = train_test_split(wine.data, wine.target, test_size=0.3)

print('train sharp:{}'.format(xtrain.shape))

# random_state创建不同的树，选择最好的。每次分枝时，不使用全部特征，随机选取一部分特征
clf = DecisionTreeClassifier(criterion='entropy', random_state=30)
clf = clf.fit(xtrain, ytrain)
score = clf.score(xtest, ytest)

print('score:{}'.format(score))

'''
可视化
'''
feature_name = ['酒精', '苹果酸', '灰', '灰的碱性'
    , '镁', '总酚', '类黄酮', '非黄烷类酚类'
    , '花青素', '颜 色强度', '色调', 'od280/od315稀释葡萄酒', '脯氨酸']
#
# dot_data = export_graphviz(clf, feature_names=feature_name,
#                            class_names=["琴酒", "雪莉", "贝尔摩德"],
#                            filled=True, rounded=True)
# graph = graphviz.Source(dot_data)
# graph.view()

print(clf.feature_importances_)
print(*zip(feature_name, clf.feature_importances_))
