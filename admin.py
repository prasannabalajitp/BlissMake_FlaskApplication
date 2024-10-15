from flask import Blueprint, render_template, redirect, url_for, request, session, flash, make_response
from app import mongo
from werkzeug.utils import secure_filename
from functools import wraps

from AppConstants.Constants import Constants
from services.adminservice import AdminService
from models.Product import ProductDetail
import os

UPLOAD_FOLDER = os.path.join(Constants.STATIC, Constants.IMG)
ALLOWED_EXTENSIONS = Constants.EXTENSIONS

admin = Blueprint(Constants.ADMIN, __name__, url_prefix=Constants.ADMIN_ROOT_URL)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if Constants.USERNAME not in session:
            flash("You must be logged in as an admin to access this page.", "error")
            return redirect(url_for(Constants.BLISSMAKE_LOGIN))
        return f(*args, **kwargs)
    return decorated_function

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
def edit_product(product_id, username):
    print(f'Session : {session}')
    print(f'USERNAME : {username}')
    if request.method == Constants.POST:
        product_name = request.form[Constants.PRODUCT_NAME]
        product_price = request.form[Constants.PRODUCT_PRICE]
        product_img = request.form[Constants.PRODUCT_IMG]

        response, products = AdminService.update_product_service(product_id, product_name, product_price, product_img)
        flash(response, Constants.INFO)

        return render_template(Constants.ADMIN_DASHBOARD_HTML, products=products)
    
    product = AdminService.get_product_by_id(product_id)
    admin_details = AdminService.get_all_admins()

    if admin_details:
        admin = next(iter(admin_details), {})
        username = admin.get(Constants.USERNAME)
        password = admin.get(Constants.PASSWORD)
    else:
        username, password = None, None
    
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