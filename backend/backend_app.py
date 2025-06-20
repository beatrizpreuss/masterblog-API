from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"post_id": 1, "title": "First post", "content": "This is the first post."},
    {"post_id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Retrieve blog posts, optionally sorted by title or content.

    Accepts optional query parameters to sort the list of posts by
    'title' or 'content' in ascending or descending order.

    Query Parameters:
        sort (str, optional): The field to sort by ('title' or 'content').
        direction (str, optional): Sort direction ('asc' or 'desc').

    Returns:
        Response: A JSON list of blog posts, sorted if parameters are valid.
        Tuple[Response, int]: An error message and 400 status code if query parameters are invalid.
    """
    query_sort = request.args.get("sort", "")
    query_direction = request.args.get("direction", "")

    sort_keys = {"title", "content"}
    if query_sort not in sort_keys and query_sort != "":
        return "Wrong sort value", 400
    if query_direction not in ("asc", "desc", ""):
        return "Wrong sort direction value", 400
    if query_sort in sort_keys:
        reverse = query_direction == "desc" #True if client is sorting by desc order
        sorted_posts = (sorted(POSTS, key=lambda x:x[query_sort], reverse=reverse))
        return jsonify(sorted_posts), 200

    return jsonify(POSTS), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    """Add a new blog post to the in-memory list of posts.

    Accepts a JSON payload containing 'title' and 'content' fields.
    If either field is missing or empty, returns a 400 error. On success,
    creates a new post with a unique ID and returns it.

    Request Body (application/json):
        title (str): The title of the blog post.
        content (str): The content of the blog post.

    Returns:
        Tuple[dict, int]: The newly created post and HTTP 201 status code on success.
        Tuple[str, int]: An error message and HTTP 400 status code if input is invalid.
    """
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if title == "":
        return "Title of post is missing", 400
    if content == "":
        return "Content of post is missing", 400

    post_id = max(post["post_id"] for post in POSTS) + 1 if POSTS else 1
    new_post = {"post_id": post_id, "title": title, "content": content}
    POSTS.append(new_post)
    return new_post, 201


@app.route('/api/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a blog post by its ID.

    Searches for a post with the specified ID in the in-memory post list.
    If found, deletes the post and returns a success message. If not found,
    returns a 404 error.

    Args:
        post_id (str): The ID of the post to delete (converted to int internally).

    Returns:
        Tuple[str, int]: A success message and HTTP 200 status code if the post is deleted.
        Tuple[str, int]: An error message and HTTP 404 status code if the post is not found.
    """
    for post in POSTS:
        if post["post_id"] == int(post_id):
            POSTS.remove(post)
            return f"Post with id {post_id} has been deleted successfully", 200
    return "Post not found", 404


@app.route('/api/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    """Update an existing blog post by its ID.

    Accepts a JSON payload containing optional 'title' and/or 'content' fields.
    If a post with the given ID exists, updates its data accordingly.
    Empty string values are ignored (fields remain unchanged). Returns the updated
    post data on success, or a 404 error if the post is not found.

    Args:
        post_id (str): The ID of the post to update (converted to int internally).

    Request Body (application/json):
        title (str, optional): The new title of the post. If empty or not provided, title is unchanged.
        content (str, optional): The new content of the post. If empty or not provided, content is unchanged.

    Returns:
        Tuple[dict, int]: The updated post and HTTP 200 status code if successful.
        Tuple[str, int]: An error message and HTTP 404 status code if the post is not found.
    """
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    for post in POSTS:
        if post["post_id"] == int(post_id):
            if title != "":
                post["title"] = title
            if content != "":
                post["content"] = content
            updated_post = {"post_id": post_id, "title": title, "content": content}
            return updated_post, 200
    return "Post not found", 404


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    """Search blog posts by title and/or content.

    Retrieves query parameters from the URL to filter posts by title and/or content.
    The search is case-insensitive and partial matches are allowed. If no query
    parameters are provided, all posts are returned.

    Query Parameters:
        title (str, optional): Substring to search for in post titles.
        content (str, optional): Substring to search for in post content.

    Returns:
        Tuple[Response, int]: A JSON list of matching blog posts and HTTP 200 status code.
    """
    query_title = request.args.get("title", "").lower()
    query_content = request.args.get("content", "").lower()

    query_result = []
    for post in POSTS:
        title = post.get("title", "").lower()
        content = post.get("content", "").lower()

        title_match = query_title in title if query_title else True
        content_match = query_content in content if query_content else True

        if title_match and content_match:
            query_result.append(post)

    return jsonify(query_result), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
