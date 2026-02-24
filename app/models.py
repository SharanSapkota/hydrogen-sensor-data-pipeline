import pickle

with open('knn-model.pkl', 'rb') as knn_model_file:
    knn_model = pickle.load(knn_model_file)

with open('forest-model.pkl', 'rb') as forest_model_file:
    forest_model = pickle.load(forest_model_file)