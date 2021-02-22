from flask import Flask, render_template, request, flash, jsonify, make_response

import redis

app = Flask(__name__)
app.secret_key = "super secret key"

r = redis.Redis(host='redis-11720.c245.us-east-1-3.ec2.cloud.redislabs.com', password='abc', port=11720)
print("conn again")
last_id = 0


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        global last_id
        req = request.form
        name = req["full_name"]
        post = req["data"]
        print(name, post)

        last = r.get("last_id")
        print("la", last)
        if last is None:
            last_id = 1
        else:
            last_id = int(last)
            last_id += 1
        r.set(f"news:name:{last_id}", name)
        r.set(f"news:post:{last_id}", post)
        r.set("last_id", last_id)
        r.lpush("post_id", last_id)
        flash("Successfully submitted the post please check it in all posts or recent posts", category='success')

    return render_template("public/home.html")


@app.route("/all")
def all_posts():
    names = r.keys(f"news:name:*")
    posts = r.keys(f"news:post:*")

    total = len(names)
    data = dict()
    i = 0
    for name_key in names:
        list = name_key.decode("utf-8").split(":")
        key_id = list[len(list) - 1]

    return render_template("all.html", posts=data)


@app.route("/latest")
def latest_posts():
    data = r.lrange("post_id", 0, 2)
    json = dict()

    for ids in data:
        json[r.get(f'news:name:{ids.decode("utf-8")}').decode("utf-8")] = r.get(
            f'news:post:{ids.decode("utf-8")}').decode("utf-8")

    return render_template("all.html", posts=json)


if __name__ == "__main__":
    app.run()
