from flask import Flask, request, jsonify
from flask_cors import CORS
from recommendation_engine import recommend_sparse, load_sparse_matrix
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
# import pickle # No longer needed with this approach
# import numpy as np # No longer needed directly here for loading

app = Flask(__name__)
CORS(app)

# Global variables for recommendation model data
matrix = None
sim_matrix = None
user_map = None # Added for original User-ID to internal index mapping
rev_user_map = None
rev_book_map = None
isbn_to_title = None

# CSV file paths (consider making these configurable)
RATINGS_CSV_PATH = "Ratings.csv"
BOOKS_CSV_PATH = "Books.csv"

def load_recommendation_data():
    """
    Loads all necessary data for the recommendation engine using functions
    from recommendation_engine.py.
    """
    global matrix, sim_matrix, user_map, rev_user_map, rev_book_map, isbn_to_title
    
    app.logger.info("Starting to load recommendation data using recommendation_engine.load_sparse_matrix...")

    try:
        # Load data using the function from recommendation_engine.py
        # This now returns: matrix, user_id_map, rev_user_id_map, rev_book_id_map, isbn_to_title
        loaded_data = load_sparse_matrix(RATINGS_CSV_PATH, BOOKS_CSV_PATH)
        
        matrix = loaded_data[0]
        user_map = loaded_data[1] # This is user_id_map from recommendation_engine
        rev_user_map = loaded_data[2]
        rev_book_map = loaded_data[3]
        isbn_to_title = loaded_data[4]
        
        app.logger.info(f"Successfully loaded data components from load_sparse_matrix.")
        app.logger.info(f"Matrix loaded with shape: {matrix.shape if matrix is not None else 'Not loaded'}")
        app.logger.info(f"User map loaded, size: {len(user_map) if user_map is not None else 'Not loaded'}")
        app.logger.info(f"ISBN to title map loaded, size: {len(isbn_to_title) if isbn_to_title is not None else 'Not loaded'}")

        # Calculate similarity matrix
        if matrix is not None:
            app.logger.info("Calculating similarity matrix...")
            sim_matrix = cosine_similarity(matrix, dense_output=False)
            app.logger.info(f"Similarity matrix calculated with shape: {sim_matrix.shape if sim_matrix is not None else 'Not calculated'}")
        else:
            app.logger.error("Matrix was not loaded, cannot calculate similarity matrix.")

        # --- Sanity Checks ---
        if matrix is None: app.logger.error("Matrix is None after loading.")
        if sim_matrix is None: app.logger.error("Sim_matrix is None after calculation.")
        if user_map is None: app.logger.error("User_map (user_id_map) is None.")
        if rev_user_map is None: app.logger.error("Rev_user_map is None.")
        if rev_book_map is None: app.logger.error("Rev_book_map is None.")
        if isbn_to_title is None: app.logger.error("isbn_to_title is None.")

        app.logger.info("Finished loading and preparing recommendation data.")

    except FileNotFoundError as e:
        app.logger.error(f"FileNotFoundError during data loading: {e}. Ensure '{RATINGS_CSV_PATH}' and '{BOOKS_CSV_PATH}' exist.")
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during data loading: {e}", exc_info=True)


@app.route('/recommend', methods=['GET'])
def recommend():
    global user_map # Ensure we are referring to the global user_map

    try:
        user_id_str = request.args.get('user_id')
        if user_id_str is None:
            app.logger.warning("Request received without user_id parameter.")
            return jsonify({"error": "user_id parameter is missing"}), 400
        
        try:
            original_user_id = int(user_id_str) # This is the User-ID from the CSV
        except ValueError:
            app.logger.warning(f"Invalid user_id format: '{user_id_str}'. Must be an integer.")
            return jsonify({"error": f"Invalid user_id format: '{user_id_str}'. Must be an integer."}), 400

        # Check if data is loaded
        if not all([matrix is not None, sim_matrix is not None, user_map is not None, 
                    rev_user_map is not None, rev_book_map is not None, isbn_to_title is not None]):
            app.logger.error("Recommendation data not fully loaded. Check server startup logs.")
            return jsonify({"error": "Recommendation data not available. Server configuration issue."}), 500

        # Convert original_user_id to internal user_idx
        user_idx = user_map.get(original_user_id)

        if user_idx is None:
            app.logger.info(f"User with original ID {original_user_id} not found in user_map.")
            # It's important to know if user_map is case-sensitive or if IDs are strings vs ints
            return jsonify({"error": f"User ID {original_user_id} not found."}), 404
        
        app.logger.info(f"Request for user_id: {original_user_id}, mapped to user_idx: {user_idx}")

        # Call recommend_sparse with the internal user_idx
        recs = recommend_sparse(user_idx, matrix, sim_matrix, rev_user_map, rev_book_map, isbn_to_title)
        
        if not recs:
            app.logger.info(f"No recommendations found for user_idx: {user_idx} (original ID: {original_user_id})")
        
        return jsonify(recs)

    except Exception as e:
        app.logger.error(f"An unexpected error occurred in /recommend route for user_id '{user_id_str}': {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)

    load_recommendation_data() 
    app.run(host='0.0.0.0', port=8000)
