from flask import Blueprint, request, jsonify, redirect, url_for, session, render_template, flash, make_response
from datetime import datetime, timezone
from dotenv import load_dotenv
from functools import wraps
from app import mongo, mail
from AppConstants.Constants import Constants
from services.blissmakeservice import BlissmakeService
from services.adminservice import AdminService
from Common.AnalyticClient import configure_and_generate_logs

load_dotenv()

# Define the blueprint
blissmake = Blueprint(Constants.BLISSMAKE, __name__, url_prefix=Constants.ROOT_URL)

def add_response_headers(func):
    @wraps
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        BlissmakeService.response_headers(response)
        return response
    return wrapper

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

@blissmake.route(Constants.ROOT)
@log_request
def index():
    product_list = BlissmakeService.index_page()
    response = make_response(render_template(Constants.INDEX_HTML, products=product_list))
    return response

@blissmake.route(Constants.LOGIN, methods=[Constants.GET, Constants.POST])
@log_request
def login_page():
    response = make_response(render_template(Constants.LOGIN_HTML))
    BlissmakeService.response_headers(response=response)
    return response

@blissmake.route(Constants.HOME, methods=[Constants.POST, Constants.GET])
@log_request
def home(username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    product_list = BlissmakeService.index_page()
    response = make_response(render_template(Constants.HOME_HTML, username=username, products=product_list))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.HOME_PAGE, methods=[Constants.POST])
@blissmake.route(Constants.MAIN_HOME_PAGE, methods=[Constants.POST])
@log_request
def authenticate_user():
    if request.method == Constants.POST:
        username = request.form.get(Constants.USERNAME)
        password = request.form.get(Constants.PASSWORD)

        query = request.form.to_dict()
        query[Constants.PASSWORD] = Constants.MASK_PWD * len(password)
        if Constants.ADMIN in username:
            admin_data = AdminService.admin_login_service(username=username, password=password)
            response = (make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN, error=admin_data))) 
                        if admin_data == Constants.INVALID_ADM_PWD 
                        else make_response(render_template(Constants.ADMIN_DASHBOARD_HTML, products=admin_data, username=username, password=password)))
            AdminService.response_headers(response)
        else:
            user = BlissmakeService.user_login(username=username, password=password)
            response_map = {
                Constants.SUCCESS: (200, make_response(redirect(url_for(Constants.BLISSMAKE_HOME, username=username)))),
                Constants.INVALID_PASSWORD: (401, make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN, error=Constants.INVALID_PASSWORD)))),
                Constants.USER_NOT_EXISTS: (404, make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN, error=Constants.USER_NOT_EXISTS)))),
            }
            _, response = response_map.get(user, (500, make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN, error=Constants.RESPONSE_INT_SER_ERR)))))
            BlissmakeService.response_headers(response)
        return response

@blissmake.route(Constants.REGISTER, methods=[Constants.GET, Constants.POST])
@log_request
def register():
    query = request.form.to_dict() if request.method == Constants.POST else {}
    if request.method == Constants.POST:
        username = query.get(Constants.USERNAME)
        email = query.get(Constants.EMAIL)
        password = query.get(Constants.PASSWORD)
        query[Constants.PASSWORD] = Constants.MASK_PWD * len(password)

        product_list = BlissmakeService.register_service(username=username, email=email, password=password)
        if product_list in [Constants.INVALID_USR_NAME, Constants.USER_EXISTS]:
            flash(product_list, category=Constants.ERROR)
            response = make_response(render_template(Constants.REGISTER_HTML, messages=product_list))
            BlissmakeService.response_headers(response=response)
            return response
        response = make_response(redirect(url_for(Constants.BLISSMAKE_HOME, username=username)))
        BlissmakeService.response_headers(response)
        return response    
    response = make_response(render_template(Constants.REGISTER_HTML))
    BlissmakeService.response_headers(response=response)
    return response

@blissmake.route(Constants.GENERATE_OTP, methods=[Constants.GET, Constants.POST])
@log_request
def generate_otp():
    email = request.form.get(Constants.EMAIL)
    gen_otp_response = BlissmakeService.generate_otp_service(email=email)
    if gen_otp_response == Constants.INVALID_EMAIL_ADDR:
        flash(Constants.INVALID_EMAIL_ADDR, Constants.ERROR1)
        return redirect(url_for(Constants.BLISSMAKE_FORGOT_PWD)) 
    elif gen_otp_response == Constants.OTP_SENT:
        flash(Constants.OTP_SENT, Constants.SUCCESS)
        return render_template(Constants.VERIFY_OTP_HTML, email=email) 
    else:
        flash(gen_otp_response, Constants.ERROR1)
        return render_template(Constants.VERIFY_OTP_HTML, email=email)

@blissmake.route(Constants.FORGOT_PWD, methods=[Constants.POST, Constants.GET])
@log_request
def forgot_password():
    return render_template(Constants.FORGOT_PWD_HTML)

@blissmake.route(Constants.VERIFY_OTP, methods=[Constants.GET, Constants.POST])
@log_request
def verify_otp():
    email = request.form.get(Constants.EMAIL)
    inp_otp = request.form.get(Constants.OTP)
    result = BlissmakeService.verify_otp_service(email=email, user_otp=inp_otp)
    if result == Constants.OTP_EXP:
        flash(Constants.OTP_EXP, Constants.ERROR)
        return redirect(url_for(Constants.BLISSMAKE_FORGOT_PWD)) 
    elif result == Constants.OTP_VERIFIED:
        flash(Constants.OTP_VERIFIED, Constants.SUCCESS)
        return render_template(Constants.RESET_PWD_HTML, email=email)
    else:
        flash(result, Constants.ERROR)
        return render_template(render_template(Constants.VERIFY_OTP_HTML, email=email))

@blissmake.route(Constants.RESET_PWD, methods=[Constants.GET, Constants.POST])
@log_request
def reset_password(email):
    if request.method == Constants.POST:
        new_password = request.form.get(Constants.NEW_PWD)
        result = BlissmakeService.reset_password_service(email=email, password=new_password)
        if result == Constants.PWD_UPDATED:
            flash(result, Constants.SUCCESS)
        elif result == Constants.ERR_UPDATING_PWD:
            flash(result, Constants.ERROR)
        else:
            flash(result, Constants.ERROR)
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
        return response

@blissmake.route(Constants.PROFILE_URL)
@log_request
def profile(username):
    if (Constants.USER_ID not in session and session.get(Constants.USERNAME) != username) or username == Constants.GUEST:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
        return response
    user = BlissmakeService.get_profile(username)
    address = user.get(Constants.ADDRESS, None)
    phone = user.get(Constants.PHONE, Constants.EMPTY) if address else None
    response = make_response(render_template(Constants.PROFILE_HTML, username=user[Constants.USERNAME],  email=user[Constants.EMAIL], address=address, phone=phone)) 
    BlissmakeService.response_headers(response)    
    return response

@blissmake.route(Constants.UPDATE_PROFILE, methods=[Constants.GET, Constants.POST])
@log_request
def update_profile(username):
    if (Constants.USER_ID not in session and session.get(Constants.USERNAME) != username) or username == Constants.GUEST:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
        return response
    if request.method == Constants.POST:
        new_address = request.form[Constants.ADDRESS]
        phone = request.form[Constants.PHONE]
        new_password = request.form[Constants.PASSWORD]
        confirm_password = request.form[Constants.CNF_PWD]      
        user = BlissmakeService.update_profile_servcice(username=username, new_password=new_password, confirm_password=confirm_password, new_address=new_address, phone=phone)       
        if user in [Constants.USER_NOT_EXISTS, Constants.PWD_NOT_MATCH, Constants.PRF_UPDATED]:
            if user == Constants.USER_NOT_EXISTS:
                flash(Constants.USER_NOT_EXISTS, Constants.ERROR1)
            elif user == Constants.PWD_NOT_MATCH:
                flash(Constants.PWD_NOT_MATCH, Constants.ERROR)
            else:
                flash(Constants.PRF_UPDATED, Constants.SUCCESS)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_PROFILE, username=username)))
            BlissmakeService.response_headers(response)
            return response
    user = BlissmakeService.get_user_by_name(username)
    if user == Constants.USER_NOT_EXISTS:
        flash(Constants.USER_NOT_EXISTS, Constants.ERROR1)
        response = make_response(redirect(url_for(Constants.PROFILE, username=username)))
        BlissmakeService.response_headers(response)
        return response  
    user_data = user.dict()
    response = make_response(render_template(Constants.PROFILE_HTML, **user_data))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.CHECKOUT)
@log_request
def checkout(username):
    if Constants.USER_ID not in session and session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
    if not cart:
        response = jsonify({Constants.ERROR: Constants.CART_NOT_FOUND})
        BlissmakeService.response_headers(response=response)
        return response 
    products = cart.get(Constants.PRODUCTS, [])
    total_price = BlissmakeService.calculate_total_price(products)
    response = make_response(render_template(
        Constants.CHECKOUT_HTML, 
        username=username, 
        products=products, 
        total_price=round(total_price, 2)
    ))
    BlissmakeService.response_headers(response=response)
    return response

@blissmake.route(Constants.PROD_DET_GUEST, defaults={Constants.USERNAME: Constants.GUEST})
@blissmake.route(Constants.PRODUCT_DETAIL)
@log_request
def product_detail(product_id, username):
    if Constants.USER_ID not in session and session.get(Constants.USERNAME) != username:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))

    else:
        product_data = BlissmakeService.product_detail_service(product_id=product_id)
        response = make_response(render_template(Constants.PROD_DET_HTML, product=product_data, username=username))
    BlissmakeService.response_headers(response) 
    return response

@blissmake.route(Constants.GET_CART, methods=[Constants.GET])
@log_request
def get_cart(username):
    if username == Constants.GUEST:
        response = make_response(render_template(Constants.LOGIN_HTML))
    elif Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        cart_products, total_price = BlissmakeService.get_cart_service(username=username)
        if not cart_products:
            flash(Constants.CART_EMPTY, Constants.WARNING)
        response = make_response(render_template(
            Constants.USER_CART_HTML,
            username=username,
            cart_products=cart_products if Constants.CRT_PROD in locals() else None,
            total_price=total_price if Constants.TOT_PRI in locals() else None
        ))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.GET_FAV)
@log_request
def get_favorite(username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username or username == Constants.GUEST:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        favorites = BlissmakeService.get_favorites(username=username)
        if favorites == Constants.FAV_NOT_EXISTS:
            flash(favorites, Constants.ERROR)
            response = make_response(render_template(Constants.FAV_HTML, username=username, messages=favorites, category=Constants.ERROR))
        else:
            response = make_response(render_template(Constants.FAV_HTML, username=username, favorites=favorites, message=None))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.DELETE_FROM_CART, methods=[Constants.POST])
@log_request
def delete_from_cart(product_id, quantity, username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        delete_prod = BlissmakeService.delete_from_cart_service(username=username, product_id=product_id, quantity=quantity)
        if delete_prod:
            if delete_prod == Constants.CART_NOT_FOUND:
                flash(Constants.CART_NOT_FOUND, Constants.ERROR)
            else:
                flash(Constants.REM_CART, Constants.SUCCESS)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_GETCART, username=username)))   
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.ADD_TO_CART, methods=[Constants.POST])
@log_request
def add_to_cart(product_id, username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username or username == Constants.GUEST:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        quantity = request.form.get(Constants.QUANTITY)
        add_cart = BlissmakeService.add_to_cart_service(username=username, prod_id=product_id, quantity=quantity)
        if add_cart == Constants.ADDED_TO_CART:
            flash(Constants.ADDED_TO_CART, Constants.SUCCESS)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username)))
        else:
            response = make_response(redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username)))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.UPDATE_QUANTITY, methods=[Constants.POST])
@log_request
def update_quantity(product_id, action, username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        cart_products, _ = BlissmakeService.update_cart_quantity(prod_id=product_id, action=action, username=username)
        if cart_products in [Constants.CART_NOT_FOUND, Constants.PROD_NOT_FOUND, Constants.CART_EMPTY]:
            flash(cart_products, Constants.ERROR1)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_GETCART, username=username)))
        else:
            response = make_response(redirect(url_for(Constants.BLISSMAKE_GETCART, username=username)))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.PAYMENT, methods=[Constants.GET, Constants.POST])
@log_request
def payment(username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        cart_products, total_price = BlissmakeService.get_cart_service(username=username)
        if request.method == Constants.POST:
            flash(Constants.PAYMENT_SUCCESS, Constants.SUCCESS)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_HOME, username=username)))
        else:
            response = make_response(render_template(Constants.PAYMENT_HTML, username=username, cart_products=cart_products, total_price=total_price))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.EDIT_ADDR, methods=[Constants.GET, Constants.POST])
@log_request
def edit_address_page(username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        address, email = BlissmakeService.get_user_address(username=username)
        response = make_response(render_template(Constants.EDIT_ADDR_HTML, username=username, address=address, email=email))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.EDIT_ADDRESS, methods=[Constants.GET, Constants.POST])
@log_request
def edit_address(username):
    if request.method == Constants.POST:
        if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
            response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
        else:
            new_address = request.form[Constants.ADDRESS]
            result = BlissmakeService.update_user_address(username=username, new_address=new_address)
            if result:
                flash(Constants.ADDR_UPDATED, Constants.SUCCESS)
                response = make_response(redirect(url_for(Constants.BLISSMAKE_PAYMENT, username=username)))
            else:
                response = make_response(redirect(url_for(Constants.BLISSMAKE_PAYMENT, username=username)))  
        BlissmakeService.response_headers(response)
        return response

@blissmake.route(Constants.PAYMENT_QR, methods=[Constants.POST])
@log_request
def payment_qr(username):
    if request.method == Constants.POST:
        if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
            response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
            BlissmakeService.response_headers(response)
            return response   
    qr_filename, total_price = BlissmakeService.payment_qr_service(username=username)
    if qr_filename == Constants.CART_NOT_FOUND:
        flash(Constants.CART_NOT_FOUND, Constants.ERROR)
        response = make_response(redirect(url_for(Constants.BLISSMAKE_HOME, username=username)))
    else:
        response = make_response(render_template(Constants.QR_PAYMENT_HTML, username=username, qr_image=qr_filename, total_price=total_price))  
    BlissmakeService.response_headers(response)
    return response


@blissmake.route(Constants.ADD_TO_WISHLIST, methods=[Constants.POST, Constants.GET])
@log_request
def add_to_wishlist(username, product_id):
    if username == Constants.GUEST or Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        favorites = BlissmakeService.add_to_wishlist_service(username=username, product_id=product_id)
        if favorites in [Constants.PROD_IN_WISHLIST, Constants.PROD_NOT_FOUND]:
            if favorites == Constants.PROD_IN_WISHLIST:
                flash(favorites, Constants.INFO)
            else:
                flash(favorites, Constants.ERROR)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username)))
        else:
            flash(favorites,Constants.SUCCESS)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username)))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.REMOVE_FAV, methods=[Constants.POST])
@log_request
def remove_favorite(username, product_id):
    if username == Constants.GUEST or Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN)))
    else:
        user_favorites = BlissmakeService.remove_from_favorites(username=username, product_id=product_id)
        if user_favorites == Constants.PROD_NOT_FOUND:
            flash(Constants.PROD_NOT_FOUND, Constants.ERROR)
        elif user_favorites in [Constants.PROD_NOT_WISHLIST, Constants.NO_FAV_FOUND]:
            flash(user_favorites, Constants.INFO)
        else:
            flash(user_favorites, Constants.SUCCESS)
        response = make_response(redirect(url_for(Constants.BLISSMAKE_GET_FAV, username=username)))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.LOGOUT, methods=[Constants.GET])
@log_request
def logout(username):
    session.pop(Constants.USER_ID, None)
    session.pop(Constants.USERNAME, username)
    session.clear()
    response = make_response(redirect(url_for(Constants.BLISSMAKE_INDEX)))
    BlissmakeService.response_headers(response)
    return response