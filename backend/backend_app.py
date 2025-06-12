from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    query_sort = request.args.get("sort", "")
    query_direction = request.args.get("direction", "")

    sort_keys = {"title", "content"}
    if query_sort not in sort_keys and query_sort != "":
        return "Wrong sort value", 400
    elif query_direction not in ("asc", "desc", ""):
        return "Wrong sort direction value", 400
    if query_sort in sort_keys:
        reverse = query_direction == "desc" #True if client is sorting by desc order
        sorted_posts = (sorted(POSTS, key=lambda x:x[query_sort], reverse=reverse))
        return jsonify(sorted_posts), 200


    return jsonify(POSTS), 200



@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if title == "":
        return "Title of post is missing", 400
    if content == "":
        return "Content of post is missing", 400

    post_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1
    new_post = {"id": post_id, "title": title, "content": content}
    POSTS.append(new_post)
    return new_post, 201


@app.route('/api/posts/<id>', methods=['DELETE'])
def delete_post(id):
    for post in POSTS:
        if post["id"] == int(id):
            POSTS.remove(post)
            return f"Post with id {id} has been deleted successfully", 200
    return "Post not found", 404


@app.route('/api/posts/<id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    for post in POSTS:
        if post["id"] == int(id):
            if title != "":
                post["title"] = title
            if content != "":
                post["content"] = content
            updated_post = {"id": id, "title": title, "content": content}
            return updated_post, 200
    return "Post not found", 404


@app.route('/api/posts/search', methods=['GET'])
def search_post():
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
