from flask import Blueprint, render_template, redirect, url_for, request, session, flash, make_response
from app import mongo
from werkzeug.utils import secure_filename
from AppConstants.Constants import Constants
from services.adminservice import AdminService
from models.Product import ProductDetail
import os

UPLOAD_FOLDER = os.path.join(Constants.STATIC, Constants.IMG)
ALLOWED_EXTENSIONS = Constants.EXTENSIONS

admin = Blueprint(Constants.ADMIN, __name__, url_prefix=Constants.ADMIN_ROOT_URL)

def allowed_file(filename):
    return Constants.IMG_CONDITION in filename and filename.rsplit(Constants.IMG_CONDITION, 1)[1].lower() in ALLOWED_EXTENSIONS

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
            session[Constants.USERNAME] = username
            print(f"Logged in as: {session[Constants.USERNAME]}")
            products = mongo.db.products.find({})
            product_list = list(products)

            return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list, username=username, password=password)
        else:
            flash(Constants.INVALID_ADM_PWD)
            return redirect(url_for(Constants.ADMIN_INDEX))
    return render_template(Constants.ADMIN_LOGIN_HTML)

@admin.route(Constants.ADM_RELOGIN, methods=[Constants.POST, Constants.GET])
def re_login(username, password, product_id):
    admin = mongo.db.admin_credentials.find_one({Constants.USERNAME: username})
    if username == admin[Constants.USERNAME] and password == admin[Constants.PASSWORD]:
        password = admin[Constants.PASSWORD]
        products = mongo.db.products.find({})
        product_list = list(products)

        return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list, username=username, password=password)
    else:
        return redirect(url_for(Constants.ADMIN_EDIT_PROD, product_id=product_id))

@admin.route(Constants.ADD_PRODUCT, methods=[Constants.POST])
def add_product():
    product_id = request.form[Constants.PRODUCT_ID]
    product_name = request.form[Constants.PRODUCT_NAME]
    product_price = request.form[Constants.PRODUCT_PRICE]
    product_img = request.files.get(Constants.PRODUCT_IMG)

    result, prod_list = AdminService.add_product_service(prod_id=product_id, prod_name=product_name, prod_price=product_price, prod_img=product_img, img_filename=product_img.filename)
    if result == Constants.NO_IMG_PROVIDED:
        flash(Constants.NO_IMG_PROVIDED, Constants.ERROR1)
    elif result == Constants.DB_ERROR:
        flash(result, Constants.ERROR1)
    else:
        flash(Constants.PROD_ADDED, Constants.SUCCESS)
    return render_template(Constants.ADMIN_DASHBOARD_HTML, products=prod_list)
    

@admin.route(Constants.EDIT_PRODUCT, methods=[Constants.GET, Constants.POST])
def edit_product(product_id):
    if request.method == Constants.POST:
    #     try:
    #         AdminService.update_product_service(
    #             product_id=product_id,
    #             product_name=request.form[Constants.PRODUCT_NAME],
    #             product_price=request.form[Constants.PRODUCT_PRICE],
    #             product_img=request.form[Constants.PRODUCT_IMG]
    #             )
    #         flash(Constants.PROD_UPDATED, Constants.INFO)
    #     except Exception as e:
    #         flash(Constants.ERR_UPD, Constants.ERROR1)
    
    # product = AdminService.get_all_products()
    # if not product:
    #     flash(Constants.PROD_NOT_FOUND, Constants.ERROR1)
    #     return redirect(url_for('admin.product_list'))
    # return  render_template(Constants.ADMIN_EDIT_HTML, product=product, username=username, password=password)

        mongo.db.products.update_one(
            {Constants.PRODUCT_ID: product_id},
            {Constants.SET: {
                Constants.PRODUCT_NAME: request.form[Constants.PRODUCT_NAME],
                Constants.PRODUCT_PRICE: request.form[Constants.PRODUCT_PRICE],
                Constants.PRODUCT_IMG: request.form[Constants.PRODUCT_IMG]
            }}
        )
        flash(Constants.PROD_UPDATED, Constants.INFO)
        products = mongo.db.products.find({})
        product_list = list(products)
        
        return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list)
    admin__detail = mongo.db.admin_credentials.find({})
    for admin in admin__detail:
        username = admin[Constants.USERNAME]
        password = admin[Constants.PASSWORD]
    product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
    return render_template(Constants.ADMIN_EDIT_HTML, product=product, username=username, password=password)


@admin.route(Constants.DEL_PRODCUT, methods=[Constants.GET])
def delete_product(product_id):
    result, product_list = AdminService.delete_product_service(product_id=product_id)

    if result == Constants.PROD_DEL:
        flash(Constants.PROD_DEL, Constants.SUCCESS)
    elif result == Constants.PROD_NOT_FOUND:
        flash(Constants.PROD_NOT_FOUND, Constants.ERROR1)
    else:
        flash(Constants.PROD_DEL_FAIL, Constants.ERROR1)
    
    return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list)


@admin.route(Constants.LOGOUT_ADM, methods=[Constants.GET])
def logout():
    session.clear()
    return redirect(url_for(Constants.BLISSMAKE_INDEX))