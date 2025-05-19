import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

def load_sparse_matrix(ratings_path, books_path):
    ratings = pd.read_csv(ratings_path, delimiter=';')
    books = pd.read_csv(books_path, delimiter=';')

    ratings = ratings[ratings['Rating'] > 0]

    user_id_map = {uid: idx for idx, uid in enumerate(ratings['User-ID'].unique())}
    book_id_map = {isbn: idx for idx, isbn in enumerate(ratings['ISBN'].unique())}
    rev_user_id_map = {v: k for k, v in user_id_map.items()}
    rev_book_id_map = {v: k for k, v in book_id_map.items()}
    
    isbn_to_title = dict(zip(books['ISBN'], books['Title']))

    ratings['user_idx'] = ratings['User-ID'].map(user_id_map)
    ratings['book_idx'] = ratings['ISBN'].map(book_id_map)

    num_users = len(user_id_map)
    num_books = len(book_id_map)

    matrix = csr_matrix((ratings['Rating'], 
                         (ratings['user_idx'], ratings['book_idx'])), 
                         shape=(num_users, num_books))

    return matrix, user_id_map, rev_user_id_map, rev_book_id_map, isbn_to_title

def recommend_sparse(user_idx, matrix, sim_matrix, rev_user_map, rev_book_map, isbn_to_title, k=10, top_n=5):
    user_ratings = matrix[user_idx].toarray().flatten()
    similarities = sim_matrix[user_idx].toarray().flatten()

    similar_users = np.argsort(similarities)[-k-1:-1][::-1]  # Exclude self
    already_read = set(matrix[user_idx].nonzero()[1])
    candidate_books = set()

    for sim_user in similar_users:
        candidate_books.update(matrix[sim_user].nonzero()[1])
    candidate_books -= already_read

    estimated_ratings = {}
    for book_idx in candidate_books:
        numer = 0
        denom = 0
        for sim_user in similar_users:
            rating = matrix[sim_user, book_idx]
            if rating > 0:
                numer += similarities[sim_user] * rating
                denom += similarities[sim_user]
        if denom > 0:
            estimated_ratings[book_idx] = numer / denom

    top_books = sorted(estimated_ratings.items(), key=lambda x: x[1], reverse=True)[:top_n]

    return [{
        'User_ID': int(rev_user_map[user_idx]),
        'Book_ID': str(rev_book_map[book_idx]),
        'Book_Title': isbn_to_title.get(str(rev_book_map[book_idx]), "Unknown Title"),
        'Recommendation_Score': float(score)
    } for book_idx, score in top_books]

def generate_recommendations_sparse(ratings_path, books_path, output_path):
    matrix, user_id_map, rev_user_map, rev_book_map, isbn_to_title = load_sparse_matrix(ratings_path, books_path)
    sim_matrix = cosine_similarity(matrix, dense_output=False)

    all_results = []
    for user_idx in tqdm(range(matrix.shape[0]), desc="Generating recommendations"):
        recs = recommend_sparse(user_idx, matrix, sim_matrix, rev_user_map, rev_book_map, isbn_to_title)
        all_results.extend(recs)

    df = pd.DataFrame(all_results)
    df.to_csv(output_path, index=False)
    print(f"Done. Recommendations saved to {output_path}")

if __name__ == "__main__":
    generate_recommendations_sparse("Ratings.csv", "Books.csv", "SparseUserBookRecommendations.csv")
