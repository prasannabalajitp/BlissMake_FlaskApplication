from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app import mongo
from AppConstants.Constants import Constants

admin = Blueprint(Constants.ADMIN, __name__, url_prefix=Constants.ADMIN_ROOT_URL)

@admin.route(Constants.ROOT)
def admin_index():
    return render_template(Constants.ADMIN_LOGIN_HTML)

@admin.route(Constants.ADMIN_DASHBOARD, methods=[Constants.GET, Constants.POST])
def admin_login():
    if request.method == Constants.POST:
        username = request.form[Constants.USERNAME]
        password = request.form[Constants.PASSWORD]

        admin = mongo.db.admin_credentials.find_one({Constants.USERNAME: username})
        if admin and admin[Constants.PASSWORD] == password:
            products = mongo.db.products.find({})
            product_list = list(products)

            return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list, username=username, password=password)
        else:
            flash(Constants.INVALID_ADM_PWD)
            return redirect(url_for(Constants.ADMIN_INDEX))
    return render_template(Constants.ADMIN_LOGIN_HTML)

@admin.route(Constants.ADD_PRODUCT, methods=[Constants.POST])
def add_product():

    product_id = request.form[Constants.PRODUCT_ID]
    product_name = request.form[Constants.PRODUCT_NAME]
    product_price = request.form[Constants.PRODUCT_PRICE]
    product_img = request.form[Constants.PRODUCT_IMG]
    
    mongo.db.products.insert_one({
        'product_id': product_id,
        'product_name': product_name,
        'product_price': product_price,
        'product_img': product_img
    })
    
    flash(Constants.PROD_ADDED, Constants.SUCCESS)
    products = mongo.db.products.find({})
    product_list = list(products)

    return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list)

@admin.route(Constants.EDIT_PRODUCT, methods=[Constants.GET, Constants.POST])
def edit_product(product_id):
    if request.method == Constants.POST:
        
        mongo.db.products.update_one(
            {Constants.PRODUCT_ID: product_id},
            {Constants.SET: {
                Constants.PRODUCT_NAME: request.form[Constants.PRODUCT_NAME],
                Constants.PRODUCT_PRICE: request.form[Constants.PRODUCT_PRICE],
                Constants.PRODUCT_IMG: request.form[Constants.PRODUCT_IMG]
            }}
        )
        flash(Constants.PROD_UPDATED, Constants.INFO)
        # Fetch the updated product list after editing
        products = mongo.db.products.find({})
        product_list = list(products)
        
        return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list)
    
    product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
    return render_template(Constants.ADMIN_EDIT_HTML, product=product)


@admin.route(Constants.DEL_PRODCUT, methods=[Constants.GET])
def delete_product(product_id):
    # Delete the product from the database
    mongo.db.products.delete_one({Constants.PRODUCT_ID: product_id})
    flash(Constants.PROD_DEL, Constants.SUCCESS)

    products = mongo.db.products.find({})
    product_list = list(products)
    return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list)


@admin.route(Constants.LOGOUT_ADM, methods=[Constants.GET])
def logout():
    session.clear()
    return redirect(url_for(Constants.ADMIN_INDEX))