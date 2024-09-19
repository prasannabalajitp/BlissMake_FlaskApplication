from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from app import mongo
from AppConstants.Constants import Constants

admin = Blueprint('admin', __name__, url_prefix='/admin/blissmake')

@admin.route('/')
def admin_index():
    return render_template('admin_login.html')

@admin.route('/admindashboard', methods=[Constants.GET, Constants.POST])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = mongo.db.admin_credentials.find_one({'username': username})
        if admin and admin["password"] == password:
            products = mongo.db.products.find({})
            product_list = list(products)

            return render_template('admin_dashboard.html', products=product_list, username=username, password=password)
        else:
            flash("Invalid Admin/Admin Password. Please try again...")
            return redirect(url_for('admin.admin_index'))
    return render_template('admin_login.html')

@admin.route('/add_product', methods=[Constants.POST])
def add_product():

    product_id = request.form['product_id']
    product_name = request.form['product_name']
    product_price = request.form['product_price']
    product_img = request.form['product_img']
    
    mongo.db.products.insert_one({
        'product_id': product_id,
        'product_name': product_name,
        'product_price': product_price,
        'product_img': product_img
    })
    
    flash('Product added successfully!', 'success')
    products = mongo.db.products.find({})
    product_list = list(products)

    return render_template('admin_dashboard.html', products=product_list)

@admin.route('/edit_product/<product_id>', methods=[Constants.GET, Constants.POST])
def edit_product(product_id):
    if request.method == Constants.POST:
        # Update the product in the database
        mongo.db.products.update_one(
            {'product_id': product_id},
            {'$set': {
                'product_name': request.form['product_name'],
                'product_price': request.form['product_price'],
                'product_img': request.form['product_img']
            }}
        )
        flash('Product updated successfully!', 'info')
        # Fetch the updated product list after editing
        products = mongo.db.products.find({})
        product_list = list(products)
        
        return render_template('admin_dashboard.html', products=product_list)
    
    product = mongo.db.products.find_one({'product_id': product_id})
    return render_template('admin_edit_product.html', product=product)


@admin.route('/delete_product/<product_id>', methods=[Constants.GET])
def delete_product(product_id):
    # Delete the product from the database
    mongo.db.products.delete_one({'product_id': product_id})
    flash('Product deleted successfully!', 'success')

    products = mongo.db.products.find({})
    product_list = list(products)
    return render_template('admin_dashboard.html', products=product_list)


@admin.route('/logout', methods=[Constants.GET])
def logout():
    session.clear()
    return redirect(url_for('admin.admin_index'))