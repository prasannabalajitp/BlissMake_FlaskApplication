from flask import Blueprint, render_template, redirect, url_for, request, session, flash, make_response, jsonify
from app import mongo
from functools import wraps

from AppConstants.Constants import Constants
from services.adminservice import AdminService
import os

UPLOAD_FOLDER = os.path.join(Constants.STATIC, Constants.IMG)
ALLOWED_EXTENSIONS = Constants.EXTENSIONS

admin = Blueprint(Constants.ADMIN, __name__, url_prefix=Constants.ADMIN_ROOT_URL)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if Constants.USERNAME not in session:
            flash(Constants.ADM_NOT_LOG_IN, Constants.ERROR1)
            return redirect(url_for(Constants.BLISSMAKE_LOGIN))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return Constants.IMG_CONDITION in filename and filename.rsplit(Constants.IMG_CONDITION, 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route(Constants.ROOT)
def admin_index():
    response = make_response(render_template(Constants.ADMIN_LOGIN_HTML))
    return response

@admin.route(Constants.ADMIN_DASHBOARD, methods=[Constants.GET, Constants.POST])
def admin_login():
    if Constants.USERNAME in session:
        username = session[Constants.USERNAME]
        products = AdminService.get_all_products()
        return render_template(Constants.ADMIN_DASHBOARD_HTML, products=products, username=username)
    
    flash(Constants.LOGIN_ERR)
    return redirect(url_for(Constants.ADMIN_INDEX))

@admin.route(Constants.ADM_RELOGIN, methods=[Constants.POST, Constants.GET])
def re_login(username):
    if Constants.USER_ID in session and session.get(Constants.USERNAME) == username:
        admin_details = AdminService.get_admin_by_id(username)
        password = admin_details[Constants.PASSWORD]
        products = AdminService.get_all_products()
        product_list = list(products)
        response = make_response(render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list, username=username, password=password))
    else:
        response = make_response(render_template(Constants.LOGIN_HTML))
    return response

@admin.route(Constants.ADD_PRODUCT, methods=[Constants.POST])
def add_product():
    product_id = request.form[Constants.PRODUCT_ID]
    product_name = request.form[Constants.PRODUCT_NAME]
    product_price = request.form[Constants.PRODUCT_PRICE]
    product_img = request.files.get(Constants.PRODUCT_IMG)

    result, _ = AdminService.add_product_service(prod_id=product_id, prod_name=product_name, prod_price=product_price, prod_img=product_img, img_filename=product_img.filename)
    if result == Constants.NO_IMG_PROVIDED:
        flash(Constants.NO_IMG_PROVIDED, Constants.ERROR1)
    elif result == Constants.DB_ERROR:
        flash(result, Constants.ERROR1)
    else:
        flash(Constants.PROD_ADDED, Constants.SUCCESS)
    return redirect(url_for(Constants.ADMIN_LOGIN))


@admin.route(Constants.EDIT_PRODUCT, methods=[Constants.GET, Constants.POST])
def edit_product(product_id, username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        session[Constants.USERNAME] = username

        flash(Constants.LOGIN_ERR)
        return redirect(url_for(Constants.ADMIN_LOGIN))
    
    if request.method == Constants.POST:
        product_name = request.form[Constants.PRODUCT_NAME]
        product_price = request.form[Constants.PRODUCT_PRICE]
        product_img = request.form[Constants.PRODUCT_IMG]

        result, _ = AdminService.update_product_service(product_id, product_name, product_price, product_img)
        flash(result, Constants.INFO)

        return redirect(url_for(Constants.ADMIN_LOGIN))
    product_details = AdminService.get_product_by_id(product_id)
    return render_template(Constants.ADMIN_EDIT_HTML, product=product_details, username=username)  

@admin.route(Constants.DEL_PRODCUT, methods=[Constants.GET])
def delete_product(product_id):
    result, _ = AdminService.delete_product_service(product_id=product_id)

    if result == Constants.PROD_DEL:
        flash(Constants.PROD_DEL, Constants.SUCCESS)
    elif result == Constants.PROD_NOT_FOUND:
        flash(Constants.PROD_NOT_FOUND, Constants.ERROR1)
    else:
        flash(Constants.PROD_DEL_FAIL, Constants.ERROR1)
    
    return redirect(url_for(Constants.ADMIN_LOGIN))


@admin.route(Constants.LOGOUT, methods=[Constants.GET])
def logout(username):
    print(f'Session before logout : {session}')
    session.pop(Constants.ADMIN_USER_ID, None)
    session.pop(Constants.USERNAME, username)
    session.clear()
    print(f'Session after logout : {session}')
    return redirect(url_for(Constants.BLISSMAKE_INDEX))