from scipy.sparse import csr_matrix
import pandas as pd

ratings = pd.read_csv("Ratings.csv", delimiter=';')
ratings = ratings[ratings['Rating'] > 0]  # filter out 0s

# Optional: drop infrequent users/books
user_counts = ratings['User-ID'].value_counts()
book_counts = ratings['ISBN'].value_counts()

ratings = ratings[ratings['User-ID'].isin(user_counts[user_counts >= 5].index)]
ratings = ratings[ratings['ISBN'].isin(book_counts[book_counts >= 10].index)]

# Map IDs to integer indices
user_map = {id: i for i, id in enumerate(ratings['User-ID'].unique())}
book_map = {isbn: i for i, isbn in enumerate(ratings['ISBN'].unique())}

ratings['user_index'] = ratings['User-ID'].map(user_map)
ratings['book_index'] = ratings['ISBN'].map(book_map)

# Create sparse matrix
user_book_matrix = csr_matrix((ratings['Rating'], 
                               (ratings['user_index'], ratings['book_index'])))
from sklearn.datasets import dump_svmlight_file

X = user_book_matrix
y = [0] * X.shape[0]  # placeholder y (not used)

dump_svmlight_file(X, y, 'user_book_matrix.libsvm', zero_based=True)