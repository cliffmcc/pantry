import flask
from flask import Flask, render_template, g, flash, request, session
from pantryDB import pantryDB

app = Flask("pantry")
# Change this key to something new before you deploy
app.secret_key = b'uI65Rtp8QseWfiU72cUh'


@app.before_request
def before_request():
    pantryDB.connectDB()


@app.after_request
def after_request(response):
    pantryDB.disconnectDB()
    return response


@app.route('/')
def home():
    g.products = pantryDB.get_products()
    return render_template("home.html")


@app.route('/foundation')
def foundation_sample():
    return render_template("foundation.html")


@app.route('/add', methods=['POST', 'GET'])
def add_item():
    if request.method == 'POST':
        upc_value = request.form['upc']
        result, last_item, message = (pantryDB.lookup_and_store_product(upc_value))
        session["add_name"] = last_item.name
        session["add_upc"] = last_item.upc
        session["add_brand"] = last_item.brand
        session["add_thumbnail"] = last_item.thumbnail
        kind = 'message' if result else 'error'
        flash(message, kind)
        return flask.redirect(flask.url_for('add_item'))
    else:
        return render_template("addItem.html")


@app.route('/remove/<product_id>')
def remove_item(product_id):
    try:
        result, message = pantryDB.remove_item(product_id)
        kind = 'message' if result else 'error'
        flash(message, kind)
    except:
        flash('Could not remove item', 'error')
    return flask.redirect(flask.url_for('home'))


@app.route('/edit/<product_upc>', methods=['POST', 'GET'])
def edit_item(product_upc):
    if request.method == 'POST':
        brand = request.form['brand']
        name = request.form['name']
        thumbnail = request.form['thumbnail']
        edit_this_product = pantryDB.Product.get(upc=product_upc)
        edit_this_product.brand = brand
        edit_this_product.name = name
        edit_this_product.thumbnail = thumbnail
        edit_this_product.save()
        flash('Item Saved', 'message')
        return flask.redirect(flask.url_for('home'))
    else:
        edit_this_product = pantryDB.Product.get(upc=product_upc)
        g.edit_product = edit_this_product
        return render_template("editItem.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0')
