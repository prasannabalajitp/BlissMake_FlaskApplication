from flask import Blueprint, request, jsonify, redirect, url_for, session, render_template, flash, make_response    
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from app import mongo, mail
from AppConstants.Constants import Constants
from models.Product import ProductDetail, Product
from models.Favorite import Favorite
from models.User import User, UpdateAddres
from services.blissmakeservice import BlissmakeService
import pyqrcode, os, random, string, re, smtplib, uuid

load_dotenv()

# Define the blueprint
blissmake = Blueprint(Constants.BLISSMAKE, __name__, url_prefix=Constants.ROOT_URL)

@blissmake.route(Constants.ROOT)
def index():
    product_list = BlissmakeService.index_page()
    response = make_response(render_template(
        Constants.INDEX_HTML, 
        products=product_list
    ))

    BlissmakeService.response_headers(response=response)
    return response


@blissmake.route(Constants.LOGIN, methods=[Constants.GET, Constants.POST])
def login():
    response = make_response(render_template(
        Constants.LOGIN_HTML
    ))

    BlissmakeService.response_headers(response=response)
    return response

@blissmake.route(Constants.HOME_PAGE, methods=[Constants.POST])
@blissmake.route(Constants.MAIN_HOME_PAGE, methods=[Constants.POST])
def authenticate_user():
    if request.method == Constants.POST:
        username = request.form.get(Constants.USERNAME)
        password = request.form.get(Constants.PASSWORD)

        if Constants.ADMIN in username:
            admin_data = BlissmakeService.admin_login(username=username, password=password)
            if admin_data == Constants.USERNAME_PWD_WRNG or Constants.INVALID_ADM_PWD:
                response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN, error=admin_data)))
                BlissmakeService.response_headers(response)
                return response
            response = make_response(render_template(Constants.ADMIN_DASHBOARD_HTML, products=admin_data, username=username, password=password))
            BlissmakeService.response_headers(response)
            return response
        else:
            user = BlissmakeService.user_login(username=username, password=password)
            if user == Constants.SUCCESS:
                response = make_response(redirect(url_for(Constants.BLISSMAKE_HOME, username=username)))
                BlissmakeService.response_headers(response)
                return response
            response = make_response(redirect(url_for(Constants.BLISSMAKE_LOGIN, error=user)))
            BlissmakeService.response_headers(response)
            return response

@blissmake.route(Constants.REGISTER, methods=[Constants.GET, Constants.POST])
def register():
    if request.method == Constants.POST:
        username = request.form.get(Constants.USERNAME)
        email = request.form.get(Constants.EMAIL)
        password = request.form.get(Constants.PASSWORD)

        reg_response = BlissmakeService.user_exists(username=username)
        if reg_response == Constants.USER_EXISTS:
            flash(Constants.USER_EXISTS, category=Constants.ERROR)
            response = make_response(render_template(Constants.REGISTER_HTML, messages=Constants.USER_EXISTS))
            BlissmakeService.response_headers(response=response)
            return response

        product_list = BlissmakeService.register_service(username=username, email=email, password=password)
        response = make_response(render_template(
            Constants.HOME_HTML, 
            username=username, 
            products=product_list
        ))
        BlissmakeService.response_headers(response=response)
        return response


    response = make_response(render_template(
        Constants.REGISTER_HTML
    ))
    BlissmakeService.response_headers(response=response)
    return response

@blissmake.route(Constants.GENERATE_OTP, methods=[Constants.GET, Constants.POST])
def generate_otp():
    email = request.form.get(Constants.EMAIL)
    
    if not email or not BlissmakeService.is_valid_email(email):
        flash(Constants.INVALID_EMAIL_ADDR, Constants.ERROR1)
        return redirect(url_for(Constants.BLISSMAKE_FORGOT_PWD))
    
    otp = Constants.EMPTY.join(random.choices(string.ascii_letters + string.digits, k=6))
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=5)

    existing_entry = mongo.db.otp.find_one({Constants.EMAIL: email})
    if existing_entry:
        mongo.db.otp.update_one(
            {Constants.EMAIL: email}, 
            {Constants.SET: {
                Constants.OTP: otp, 
                Constants.EXP_TIME: expiration_time
                }}, 
                upsert=True
        )
    else:
        mongo.db.otp.insert_one({
            Constants.EMAIL: email,
            Constants.OTP: otp,
            Constants.EXP_TIME: expiration_time
        })

    try:
        with smtplib.SMTP(os.getenv(Constants.MAIL_SERVER), 587) as server:
            server.starttls()
            server.login(os.getenv(Constants.MAIL_USERNAME), os.getenv(Constants.MAIL_PWD))
            subject = Constants.SUB
            body = f"Your OTP is: {otp}"
            msg = f"Subject: {subject}\n\n{body}"

            server.sendmail(os.getenv(Constants.MAIL_USERNAME), email, msg)
            flash(Constants.OTP_SENT, Constants.SUCCESS)
    except smtplib.SMTPException as e:
        flash(f"Error sending email: {str(e)}", Constants.ERROR1)
    return render_template(Constants.VERIFY_OTP_HTML, email=email)


@blissmake.route(Constants.FORGOT_PWD, methods=[Constants.POST, Constants.GET])
def forgot_password():
    return render_template(Constants.FORGOT_PWD_HTML)


from datetime import datetime, timezone

@blissmake.route(Constants.VERIFY_OTP, methods=[Constants.GET, Constants.POST])
def verify_otp():
    email = request.form.get(Constants.EMAIL)
    inp_otp = request.form.get(Constants.OTP)
    record = mongo.db.otp.find_one({Constants.EMAIL: email})
    if record:
        expiration_time = record[Constants.EXP_TIME].replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)

        if current_time > expiration_time:
            flash(Constants.OTP_EXP, Constants.ERROR)
            return redirect(url_for(Constants.BLISSMAKE_FORGOT_PWD))

        if record[Constants.OTP] == inp_otp:
            flash(Constants.OTP_VERIFIED, Constants.SUCCESS)
            return render_template(Constants.RESET_PWD_HTML, email=email)
        else:
            flash(Constants.INVALID_OTP, Constants.ERROR1)

    email = request.args.get(Constants.EMAIL)
    return render_template(Constants.VERIFY_OTP_HTML, email=email)


@blissmake.route(Constants.RESET_PWD, methods=[Constants.GET, Constants.POST])
def reset_password(email):
    if request.method == Constants.POST:
        new_password = request.form.get(Constants.NEW_PWD)
        if email and new_password:
            hashed_password = generate_password_hash(new_password)  # Hash the password
            result = mongo.db.users.update_one({Constants.EMAIL: email}, {Constants.SET: {Constants.PASSWORD: hashed_password}})
            if result.modified_count > 0:
                mongo.db.otp.delete_many({Constants.EMAIL: email})  # Remove OTP after use
                print(mongo.db.users.find_one({Constants.EMAIL: email}))
                flash(Constants.PWD_UPDATED, Constants.SUCCESS)
                return redirect(url_for(Constants.BLISSMAKE_LOGIN))
            else:
                flash(Constants.ERR_UPDATING_PWD, Constants.ERROR)
        else:
            flash(Constants.EMAIL_PWD_REQ, Constants.ERROR)
    return render_template(Constants.LOGIN_HTML)



@blissmake.route(Constants.PROFILE_URL)
def profile(username):
    if Constants.USER_ID not in session and session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    if username == Constants.GUEST:
        return render_template(Constants.LOGIN_HTML)

    user = BlissmakeService.get_profile(username=username)
    if Constants.ADDRESS in user and user[Constants.ADDRESS]:
        if Constants.PHONE in user:
            response = make_response(render_template(
                Constants.PROFILE_HTML, 
                username=user[Constants.USERNAME], 
                email=user[Constants.EMAIL], 
                address=user[Constants.ADDRESS], 
                phone=user[Constants.PHONE]
            ))
            BlissmakeService.response_headers(response)

            return response
        response = make_response(render_template(
            Constants.PROFILE_HTML, 
            username=user[Constants.USERNAME], 
            email=user[Constants.EMAIL], 
            address=user[Constants.ADDRESS], 
            phone=Constants.EMPTY
        ))
        BlissmakeService.response_headers(response)

        return response
    response = make_response(render_template(
        Constants.PROFILE_HTML, 
        username=user[Constants.USERNAME], 
        email=user[Constants.EMAIL], 
        address=None, 
        phone=None
    ))
    BlissmakeService.response_headers(response)

    return response


@blissmake.route(Constants.UPDATE_PROFILE, methods=[Constants.GET, Constants.POST])
def update_profile(username):
    if request.method == Constants.POST:
        new_address = request.form[Constants.ADDRESS]
        phone = request.form[Constants.PHONE]
        new_password = request.form[Constants.PASSWORD]
        confirm_password = request.form[Constants.CNF_PWD]

        user = BlissmakeService.update_profile_servcice(username=username, new_password=new_password, confirm_password=confirm_password, new_address=new_address, phone=phone)
        if user == Constants.USER_NOT_EXISTS:
            flash(Constants.USER_NOT_EXISTS, Constants.ERROR1)
            response = make_response(redirect(url_for(Constants.PROFILE, username=username)))
            BlissmakeService.response_headers(response)
            return response
        elif user == Constants.PWD_NOT_MATCH:
            flash(Constants.PWD_NOT_MATCH, Constants.ERROR)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_PROFILE, username=username)))
            BlissmakeService.response_headers(response)
            return response
        elif user == Constants.PRF_UPDATED:
            flash(Constants.PRF_UPDATED, Constants.SUCCESS)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_PROFILE, username=username)))
            BlissmakeService.response_headers(response)
            return response
    
    user = mongo.db.users.find_one({Constants.USERNAME: username})

    if not user:
        flash(Constants.USER_NOT_EXISTS, Constants.ERROR1)
        response = make_response(redirect(url_for(Constants.PROFILE, username=username)))
        BlissmakeService.response_headers(response)
        return response
    
    user_data = User(
        username=user[Constants.USERNAME],
        email=user[Constants.EMAIL],
        address=user.get(Constants.ADDRESS, Constants.EMPTY),
        phone=user.get(Constants.PHONE, Constants.EMPTY)).dict()

    response = make_response(render_template(Constants.PROFILE_HTML, **user_data))

    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.HOME, methods=[Constants.POST, Constants.GET])
def home(username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    print(f'USERNAME : {username}')

    product_list = BlissmakeService.index_page()
    response = make_response(
        render_template(
            Constants.HOME_HTML, 
            username=username, 
            products=product_list
        )
    )
    BlissmakeService.response_headers(response=response)
    return response


@blissmake.route(Constants.CHECKOUT)
def checkout(username):
    if Constants.USER_ID not in session and session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))

    cart = mongo.db.usercart.find_one({
            Constants.USERNAME: username
            })
    if not cart:
        response = jsonify({
            Constants.ERROR: Constants.CART_NOT_FOUND
            })
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
def product_detail(product_id, username):
    
    if Constants.USER_ID not in session and session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    product_data = BlissmakeService.product_detail_service(product_id=product_id)
    
    response = make_response(render_template(
                Constants.PROD_DET_HTML, 
                product=product_data, 
                username=username
            )
        )
    BlissmakeService.response_headers(response)
    return response


@blissmake.route(Constants.GET_CART, methods=[Constants.GET])
def get_cart(username):
    if username == Constants.GUEST:
        return render_template(Constants.LOGIN_HTML)
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    cart_products, total_price = BlissmakeService.get_cart_service(username=username)
    if not cart_products:
        flash(Constants.CART_EMPTY, Constants.WARNING)
        response = make_response(render_template(Constants.USER_CART_HTML, username=username))
        BlissmakeService.response_headers(response=response)
        return response
    
    response = make_response(
        render_template(
            Constants.USER_CART_HTML, 
            username=username, 
            cart_products=cart_products, 
            total_price=total_price
        ))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.GET_FAV)
def get_favorite(username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    if username == Constants.GUEST:
        return render_template(Constants.LOGIN_HTML)

    favorites = BlissmakeService.get_favorites(username=username)

    if favorites == Constants.FAV_NOT_EXISTS:
        response = make_response(render_template(Constants.FAV_HTML, username=username, message=Constants.FAV_NOT_EXISTS))
        BlissmakeService.response_headers(response)
        return response

    response = make_response(render_template(Constants.FAV_HTML, username=username, favorites=favorites, message=None))
    BlissmakeService.response_headers(response=response)

    return response

@blissmake.route(Constants.DELETE_FROM_CART, methods=[Constants.POST])
def delete_from_cart(product_id, quantity, username):

    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    delete_prod = BlissmakeService.delete_from_cart_service(username=username, product_id=product_id, quantity=quantity)
    if delete_prod == True:
        response = make_response(redirect(url_for(
            Constants.BLISSMAKE_GETCART, 
            username=username
        )))
        BlissmakeService.response_headers(response=response)
        return response

@blissmake.route(Constants.ADD_TO_CART, methods=[Constants.POST])
def add_to_cart(product_id, username):
    if request.method == Constants.POST:
        if username == Constants.GUEST:
            return redirect(url_for(Constants.BLISSMAKE_LOGIN))
        if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
            return redirect(url_for(Constants.BLISSMAKE_LOGIN))
        quantity = request.form.get(Constants.QUANTITY)
        add_cart = BlissmakeService.add_to_cart_service(username=username, prod_id=product_id, quantity=quantity)

        if add_cart == Constants.ADDED_TO_CART:
            flash(Constants.ADDED_TO_CART, Constants.SUCCESS)
            response = make_response(redirect(url_for(
                    Constants.BLISSMAKE_PROD_DETAIL, 
                    product_id=product_id, 
                    username=username
                )))
            BlissmakeService.response_headers(response=response)
            return response

@blissmake.route(Constants.UPDATE_QUANTITY, methods=[Constants.POST])
def update_quantity(product_id, action, username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
            return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    
    cart_products, total_price = BlissmakeService.update_cart_quantity(prod_id=product_id, action=action, username=username)

    if cart_products in [Constants.CART_NOT_FOUND, Constants.PROD_NOT_FOUND, Constants.CART_EMPTY]:
        flash(cart_products, Constants.ERROR1)
        response = make_response(redirect(url_for(Constants.BLISSMAKE_GETCART, username=username)))
        BlissmakeService.response_headers(response)
        return response
    response = make_response(render_template(
                                Constants.USER_CART_HTML, 
                                username=username, 
                                cart_products=cart_products, 
                                total_price=total_price
                            ))
    BlissmakeService.response_headers(response=response)
    return response

@blissmake.route(Constants.PAYMENT, methods=[Constants.GET, Constants.POST])
def payment(username):
    cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
    cart_products = cart[Constants.PRODUCTS] if cart else []
    total_price = BlissmakeService.calculate_total_price(cart_products)

    if request.method == Constants.POST:
        flash(Constants.PAYMENT_SUCCESS, Constants.SUCCESS)
        return redirect(url_for(
                Constants.BLISSMAKE_HOME, 
                username=username
            ))
    
    return render_template(
            Constants.PAYMENT_HTML, 
            username=username, 
            cart_products=cart_products, 
            total_price=total_price
        )

@blissmake.route(Constants.EDIT_ADDR, methods=[Constants.GET, Constants.POST])
def edit_address_page(username):
    if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
            return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    address, email = BlissmakeService.get_user_address(username=username)
    response = make_response(render_template(
        Constants.EDIT_ADDR_HTML, 
        username=username,
         address=address, 
         email=email
    ))
    BlissmakeService.response_headers(response)
    return response

@blissmake.route(Constants.EDIT_ADDRESS, methods=[Constants.GET, Constants.POST])
def edit_address(username):
    if request.method == Constants.POST:
        if Constants.USER_ID not in session or session.get(Constants.USERNAME) != username:
            return redirect(url_for(Constants.BLISSMAKE_LOGIN))
        new_address = request.form[Constants.ADDRESS]
        result = BlissmakeService.update_user_address(username=username, new_address=new_address)
        if result == True:
            flash(Constants.ADDR_UPDATED, Constants.SUCCESS)
            response = make_response(redirect(url_for(Constants.BLISSMAKE_PAYMENT, username=username)))
            BlissmakeService.response_headers(response)
            return response

@blissmake.route(Constants.PAYMENT_QR, methods=[Constants.POST])
def payment_qr(username):
    cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
    if not cart:
        flash(Constants.CART_NOT_FOUND, Constants.ERROR)
        return redirect(url_for(
                Constants.BLISSMAKE_HOME, username=username
            ))
    
    total_price = BlissmakeService.calculate_total_price(cart.get(Constants.PRODUCTS, []))
    
    upi_id = os.getenv(Constants.UPI_ID)
    payee_name = os.getenv(Constants.PAYEE_NAME)
    amount = round(total_price, 2)
    transaction_note = Constants.TXN_NOTE

    upi_url = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount}&cu=INR&tn={transaction_note}"

    time = datetime.now(timezone.utc).strftime(Constants.STRF_TIME)
    qr = pyqrcode.create(upi_url)
    qr_filename = f'static/qr/payment_qr_{username}_{time}.png'
    qr.png(qr_filename, scale=8)

    return render_template(
            Constants.QR_PAYMENT_HTML, 
            username=username, 
            qr_image=qr_filename, 
            total_price=round(total_price)
        )

@blissmake.route(Constants.ADD_TO_WISHLIST, methods=[Constants.POST, Constants.GET])
def add_to_wishlist(username, product_id):
    if username == Constants.GUEST:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    
    product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
    if not product:
        flash(Constants.PROD_NOT_FOUND, Constants.ERROR)
        return redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username))
    
    user_favorites = mongo.db.favorites.find_one({
        Constants.USERNAME: username,
    })
    if user_favorites:
        if any(fav_product[Constants.PRODUCT_ID] == product_id for fav_product in user_favorites[Constants.PRODUCTS]):
            flash(Constants.PROD_IN_WISHLIST, Constants.INFO)
            return redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username))
        
        mongo.db.favorites.update_one(
            {Constants.USERNAME: username},
            {Constants.PUSH: {
                Constants.PRODUCTS: ProductDetail(
                    product_id=product[Constants.PRODUCT_ID],
                    product_name=product[Constants.PRODUCT_NAME],
                    product_price=product[Constants.PRODUCT_PRICE],
                    product_img=product[Constants.PRODUCT_IMG]
                ).dict()
            }}
        )
        flash(Constants.ADDED_TO_WISHLIST, Constants.SUCCESS)
    else:
        data = ProductDetail(
            product_id=product[Constants.PRODUCT_ID],
            product_name=product[Constants.PRODUCT_NAME],
            product_price=product[Constants.PRODUCT_PRICE],
            product_img=product[Constants.PRODUCT_IMG]
        ).dict()

        favorite_data = Favorite(
            username=username,
            products=[data]
        ).dict()
        
        result = mongo.db.favorites.insert_one(favorite_data)
        favorite_data[Constants.ID] = str(result.inserted_id)
        flash(Constants.ADDED_TO_WISHLIST, Constants.SUCCESS)
    return redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username))



@blissmake.route(Constants.REMOVE_FAV, methods=[Constants.POST])
def remove_favorite(username, product_id):
    if username == Constants.GUEST:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))
    
    product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
    if not product:
        flash(Constants.PROD_NOT_FOUND, Constants.ERROR)
        return redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username))
    
    user_favorites = mongo.db.favorites.find_one({Constants.USERNAME: username})
    if user_favorites:
        product_exist = any(fav_product[Constants.PRODUCT_ID] == product_id for fav_product in user_favorites[Constants.PRODUCTS])
        if product_exist:
            mongo.db.favorites.update_one(
                {Constants.USERNAME: username},
                {Constants.PULL: {Constants.PRODUCTS: {Constants.PRODUCT_ID: product_id}}}
            )
            flash(Constants.REM_FRM_WISHLIST, Constants.SUCCESS)
        else:
            flash(Constants.PROD_NOT_WISHLIST, Constants.INFO)
    else:
        flash(Constants.NO_FAV_FOUND, Constants.INFO)
    
    return redirect(url_for(Constants.BLISSMAKE_GET_FAV, username=username))

@blissmake.route(Constants.LOGOUT, methods=[Constants.GET])
def logout(username):
    print(f'Session before logout : {session}')
    
    session.pop(Constants.USER_ID, None)
    session.pop(Constants.USERNAME, username)
    session.clear()
    print(f'session after logout : {session}')
    return redirect(url_for(Constants.BLISSMAKE_INDEX))