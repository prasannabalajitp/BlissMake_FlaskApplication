from flask import Blueprint, render_template, redirect, url_for, request, session, flash, make_response, jsonify
from app import mongo
from functools import wraps
from datetime import datetime, timezone
from Common.AnalyticClient import configure_and_generate_logs
from AppConstants.Constants import Constants
from services.adminservice import AdminService
import os

UPLOAD_FOLDER = os.path.join(Constants.STATIC, Constants.IMG)
ALLOWED_EXTENSIONS = Constants.EXTENSIONS

admin = Blueprint(Constants.ADMIN, __name__, url_prefix=Constants.ADMIN_ROOT_URL)

def log_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now(timezone.utc).isoformat()
        response = func(*args, **kwargs)
        end_time = datetime.now(timezone.utc).isoformat()
        if hasattr(response, Constants.DATA):
            username = kwargs.get(Constants.USERNAME) or request.form.get(Constants.USERNAME)
            query = kwargs.get(Constants.QUERY, None) or request.form.to_dict()
            if Constants.PASSWORD in query:
                query[Constants.PASSWORD] = Constants.MASK_PWD * len(query[Constants.PASSWORD])
            log_message = kwargs.get(Constants.LOG_MSG, None)
            response_data = log_message if log_message else str(response.data)
            configure_and_generate_logs(
                username, query, request.path, start_time, end_time,
                response_data, response.status_code, request.method,
                request.host_url, response.content_type
            )
        return response
    return wrapper


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
@log_request
def admin_index():
    response = make_response(render_template(Constants.ADMIN_LOGIN_HTML))
    return response

@admin.route(Constants.ADMIN_DASHBOARD, methods=[Constants.GET, Constants.POST])
@log_request
def admin_login():
    if Constants.USERNAME in session:
        username = session[Constants.USERNAME]
        products = AdminService.get_all_products()
        response = make_response(render_template(Constants.ADMIN_DASHBOARD_HTML, products=products, username=username))
        return response
    
    flash(Constants.LOGIN_ERR)
    response = make_response(redirect(url_for(Constants.ADMIN_INDEX)))
    return response

@admin.route(Constants.ADM_RELOGIN, methods=[Constants.POST, Constants.GET])
@log_request
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
@log_request
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
    response = make_response(redirect(url_for(Constants.ADMIN_LOGIN)))
    AdminService.response_headers(response)
    return response


@admin.route(Constants.EDIT_PRODUCT, methods=[Constants.GET, Constants.POST])
@log_request
def edit_product(product_id, username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        session[Constants.USERNAME] = username

        flash(Constants.LOGIN_ERR)
        response = make_response(redirect(url_for(Constants.ADMIN_INDEX)))
        return response
    
    if request.method == Constants.POST:
        product_name = request.form[Constants.PRODUCT_NAME]
        product_price = request.form[Constants.PRODUCT_PRICE]
        product_img = request.form[Constants.PRODUCT_IMG]

        result, _ = AdminService.update_product_service(product_id, product_name, product_price, product_img)
        flash(result, Constants.INFO)

        response = make_response(redirect(url_for(Constants.ADMIN_LOGIN)))
        return response
    product_details = AdminService.get_product_by_id(product_id)
    response = make_response(render_template(Constants.ADMIN_EDIT_HTML, product=product_details, username=username))
    return response

@admin.route(Constants.DEL_PRODCUT, methods=[Constants.GET])
@log_request
def delete_product(product_id):
    result, _ = AdminService.delete_product_service(product_id=product_id)

    if result == Constants.PROD_DEL:
        flash(Constants.PROD_DEL, Constants.SUCCESS)
    elif result == Constants.PROD_NOT_FOUND:
        flash(Constants.PROD_NOT_FOUND, Constants.ERROR1)
    else:
        flash(Constants.PROD_DEL_FAIL, Constants.ERROR1)
    
    response = make_response(redirect(url_for(Constants.ADMIN_LOGIN)))
    return response


@admin.route(Constants.LOGOUT, methods=[Constants.GET])
@log_request
def logout(username):
    session.pop(Constants.ADMIN_USER_ID, None)
    session.pop(Constants.USERNAME, username)
    session.clear()
    resonse = make_response(redirect(url_for(Constants.BLISSMAKE_INDEX)))
    return resonse