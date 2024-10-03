from flask import Blueprint, request, jsonify, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from app import mongo, mail
from AppConstants.Constants import Constants
from models.Product import ProductDetail, Product
from models.Favorite import Favorite
from models.User import User
import pyqrcode, os, random, string, re, smtplib

load_dotenv()

# Define the blueprint
blissmake = Blueprint(Constants.BLISSMAKE, __name__, url_prefix=Constants.ROOT_URL)



def update_product_quantity_in_cart(cart, product_id, action):
    for item in cart.get(Constants.PRODUCTS, []):
        if item[Constants.PRODUCT_ID] == product_id:
            current_quantity = int(item[Constants.QUANTITY])
            if action == Constants.INCREASE:
                item[Constants.QUANTITY] = current_quantity + 1
            elif action == Constants.DECREASE and current_quantity > 1:
                item[Constants.QUANTITY] = current_quantity - 1
            return True
    return False

def calculate_total_price(cart_products):
    total_price = 0
    for item in cart_products:
        price = float(item[Constants.PRODUCT_PRICE])
        quantity = int(item[Constants.QUANTITY])
        total_price += price * quantity
    return total_price

def is_valid_email(email):
    pattern = Constants.VALID_EMAIL
    return re.match(pattern, email) is not None

@blissmake.route(Constants.ROOT)
def index():
    products = mongo.db.products.find({})
    product_list = list(products)
    return render_template(
        Constants.INDEX_HTML, 
        products=product_list
    )

@blissmake.route(Constants.LOGIN, methods=[Constants.GET, Constants.POST])
def login():
    return render_template(
        Constants.LOGIN_HTML
    )

@blissmake.route(Constants.GENERATE_OTP, methods=[Constants.GET, Constants.POST])
def generate_otp():
    email = request.form.get(Constants.EMAIL)
    
    if not email or not is_valid_email(email):
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

@blissmake.route(Constants.REGISTER, methods=[Constants.GET, Constants.POST])
def register():
    if request.method == Constants.POST:
        username = request.form.get(Constants.USERNAME)
        email = request.form.get(Constants.EMAIL)
        password = request.form.get(Constants.PASSWORD)

        user_exists = mongo.db.users.find_one({Constants.USERNAME: username})
        if user_exists:
            return jsonify({
                Constants.MESSAGE: Constants.USER_EXISTS
            })

        hashed_password = generate_password_hash(password, method=Constants.PASSWORD_HASH_METHOD)
        mongo.db.users.insert_one({
            Constants.USERNAME: username, 
            Constants.EMAIL: email, 
            Constants.PASSWORD: hashed_password
        })
        products = mongo.db.products.find({})
        product_list = list(products)
        return render_template(
            Constants.HOME_HTML, 
            username=username, 
            products=product_list
        )

    return render_template(
        Constants.REGISTER_HTML
    )

@blissmake.route(Constants.PROFILE_URL)
def profile(username):
    if username == Constants.GUEST:
        return render_template(Constants.LOGIN_HTML)
    if Constants.USER not in session:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))

    user = mongo.db.users.find_one({Constants.USERNAME: username})
    if Constants.ADDRESS in user and user[Constants.ADDRESS]:
        return render_template(Constants.PROFILE_HTML, username=user[Constants.USERNAME], email=user[Constants.EMAIL], address=user[Constants.ADDRESS])
    return render_template(Constants.PROFILE_HTML, username=user[Constants.USERNAME], email=user[Constants.EMAIL], address=None)


@blissmake.route(Constants.UPDATE_PROFILE, methods=[Constants.GET, Constants.POST])
def update_profile(username):
    if request.method == Constants.POST:
        new_address = request.form[Constants.ADDRESS]
        phone = request.form[Constants.PHONE]
        new_password = request.form[Constants.PASSWORD]
        confirm_password = request.form[Constants.CNF_PWD]

        user = mongo.db.users.find_one({Constants.USERNAME: username})
        if not user:
            flash(Constants.USER_NOT_EXISTS, Constants.ERROR1)
            return redirect(url_for(Constants.PROFILE, username=username))
        
        update_data = {
            "address": new_address,
            "phone": phone
        }
        if new_password and new_password == confirm_password:
            hashed_password = generate_password_hash(new_password)
            update_data[Constants.PASSWORD] = hashed_password
        elif new_password != confirm_password:
            flash(Constants.PWD_NOT_MATCH, Constants.ERROR)
            return redirect(url_for(Constants.PROFILE, username=username))
        
        mongo.db.users.update_one({Constants.USERNAME: username}, {Constants.SET: update_data})

        flash(Constants.PRF_UPDATED, Constants.SUCCESS)
        return redirect(url_for(Constants.BLISSMAKE_PROFILE, username=username))
    
    user = mongo.db.users.find_one({Constants.USERNAME: username})

    if not user:
        flash(Constants.USER_NOT_EXISTS, Constants.ERROR1)
        return redirect(url_for(Constants.PROFILE, username=username))
    
    user_data = User(
        username=user[Constants.USERNAME],
        email=user[Constants.EMAIL],
        address=user.get(Constants.ADDRESS, Constants.EMPTY),
        phone=user.get(Constants.PHONE, Constants.EMPTY)).dict()

    return render_template(Constants.PROFILE_HTML, **user_data)

@blissmake.route(Constants.HOME, methods=[Constants.POST, Constants.GET])
def home(username):
    products = mongo.db.products.find({})
    product_list = list(products)
    return render_template(
        Constants.HOME_HTML, 
        username=username, 
        products=product_list
    )

@blissmake.route(Constants.CHECKOUT)
def checkout(username):
    cart = mongo.db.usercart.find_one({
            Constants.USERNAME: username
            })
    if not cart:
        return jsonify({
            Constants.ERROR: Constants.CART_NOT_FOUND
            })
    
    products = cart.get(Constants.PRODUCTS, [])

    total_price = calculate_total_price(products)

    return render_template(
        Constants.CHECKOUT_HTML, 
        username=username, 
        products=products, 
        total_price=round(total_price, 2)
    )

@blissmake.route(Constants.MAIN_HOME_PAGE, methods=[Constants.POST])
def authenticate_user():
    if request.method == Constants.POST:
        username = request.form.get(Constants.USERNAME)
        password = request.form.get(Constants.PASSWORD)
        
        if Constants.ADMIN in username:
            admin_data = mongo.db.admin_credentials.find_one({Constants.USERNAME : username})
            admin_password = admin_data[Constants.PASSWORD]
            if admin_password == password:
                products = mongo.db.products.find({})
                product_list = list(products)
                return render_template(Constants.ADMIN_DASHBOARD_HTML, products=product_list, username=username, password=password)
            return redirect(url_for(Constants.BLISSMAKE_LOGIN, error=Constants.USERNAME_PWD_WRNG))
        user = mongo.db.users.find_one({Constants.USERNAME: username})
        if user:
            if check_password_hash(user[Constants.PASSWORD], password):
                session[Constants.USER] = username
                return redirect(url_for(
                    Constants.BLISSMAKE_HOME, 
                    username=username
                ))
                
            else:
                return redirect(url_for(
                    Constants.BLISSMAKE_LOGIN, 
                    error=Constants.INVALID_PASSWORD
                ))
        
        return redirect(url_for(
            Constants.BLISSMAKE_LOGIN, 
            error=Constants.USER_NOT_EXISTS
        ))

@blissmake.route(Constants.PROD_DET_GUEST, defaults={Constants.USERNAME: Constants.GUEST})
@blissmake.route(Constants.PRODUCT_DETAIL)
def product_detail(product_id, username):
    product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
    product_data = ProductDetail(
        product_id=product[Constants.PRODUCT_ID],
        product_name=product[Constants.PRODUCT_NAME],
        product_price=product[Constants.PRODUCT_PRICE],
        product_img=product[Constants.PRODUCT_IMG]).dict()
    
    return render_template(
        Constants.PROD_DET_HTML, 
        product=product_data, 
        username=username
    )

@blissmake.route(Constants.GET_CART, methods=[Constants.GET])
def get_cart(username):
    if username == Constants.GUEST:
        return render_template(Constants.LOGIN_HTML)
    cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
    cart_products = cart[Constants.PRODUCTS] if cart else []
    total_price = calculate_total_price(cart_products)
    if not cart_products:
        flash(Constants.CART_EMPTY, Constants.WARNING)
    
    return render_template(
        Constants.USER_CART_HTML, 
        username=username, 
        cart_products=cart_products, 
        total_price=total_price
    )

@blissmake.route(Constants.DELETE_FROM_CART, methods=[Constants.POST])
def delete_from_cart(product_id, quantity, username):
    mongo.db.usercart.update_one(
        {Constants.USERNAME: username},
        {Constants.PULL: {Constants.PRODUCTS: {
                Constants.PRODUCT_ID: product_id, 
                Constants.QUANTITY: int(quantity)
            }}}
    )

    return redirect(url_for(
        Constants.BLISSMAKE_GETCART, 
        username=username
    ))

@blissmake.route(Constants.ADD_TO_CART, methods=[Constants.POST])
def add_to_cart(product_id, username):
    if request.method == Constants.POST:
        if username == Constants.GUEST:
            return redirect(url_for(
                Constants.BLISSMAKE_LOGIN
            ))
        
        quantity = request.form.get(Constants.QUANTITY)
        product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
        product_name = product[Constants.PRODUCT_NAME]
        product_img = product[Constants.PRODUCT_IMG]
        product_price = product[Constants.PRODUCT_PRICE]
        new_product = Product(
                product_id=product_id, 
                product_name=product_name, 
                product_price=product_price, 
                product_img=product_img, 
                quantity=quantity
            ).dict()
        existing_cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
        if existing_cart:
            mongo.db.usercart.update_one(
                {Constants.USERNAME: username},
                {Constants.PUSH: {Constants.PRODUCTS: new_product}}
            )
        else:
            data = {
                Constants.USERNAME: username,
                Constants.PRODUCTS: [new_product]
            }
            mongo.db.usercart.insert_one(data)
        
        flash(Constants.ADDED_TO_CART, Constants.SUCCESS)
        return redirect(url_for(
                Constants.BLISSMAKE_PROD_DETAIL, 
                product_id=product_id, 
                username=username
            ))

@blissmake.route(Constants.UPDATE_QUANTITY, methods=[Constants.POST])
def update_quantity(product_id, action, username):
    cart = mongo.db.usercart.find_one({Constants.USERNAME: username})

    if not cart:
        flash(Constants.CART_NOT_FOUND, Constants.ERROR1)
        return redirect(url_for(Constants.BLISSMAKE_GETCART, username=username))

    updated = update_product_quantity_in_cart(cart, product_id, action)
    if not updated:
        flash(Constants.PRODUCT_NOT_FOUND, Constants.ERROR)
        return redirect(url_for(Constants.BLISSMAKE_GETCART, username=username))

    mongo.db.usercart.update_one(
        {Constants.USERNAME: username},
        {Constants.SET: {Constants.PRODUCTS: cart[Constants.PRODUCTS]}}
    )

    cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
    cart_products = cart[Constants.PRODUCTS] if cart else []
    
    total_price = calculate_total_price(cart_products)
    if not cart_products:
        flash(Constants.CART_EMPTY, Constants.WARNING)

    return render_template(
        Constants.USER_CART_HTML, 
        username=username, 
        cart_products=cart_products, 
        total_price=total_price
    )

@blissmake.route(Constants.PAYMENT, methods=[Constants.GET, Constants.POST])
def payment(username):
    cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
    cart_products = cart[Constants.PRODUCTS] if cart else []
    total_price = calculate_total_price(cart_products)

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
    user_data = mongo.db.users.find_one({Constants.USERNAME: username})
    if user_data:
        address = user_data.get(Constants.ADDRESS, Constants.EMPTY)
        email = user_data.get(Constants.EMAIL, Constants.EMPTY)
    return render_template(Constants.EDIT_ADDR_HTML, username=username, address=address, email=email)

@blissmake.route(Constants.EDIT_ADDRESS, methods=[Constants.GET, Constants.POST])
def edit_address(username):
    if request.method == Constants.POST:
        new_address = request.form[Constants.ADDRESS]
        mongo.db.users.update_one({Constants.USERNAME: username}, {Constants.SET: {Constants.ADDRESS: new_address}})
        flash(Constants.ADDR_UPDATED, Constants.SUCCESS)
        return redirect(url_for(Constants.BLISSMAKE_PAYMENT, username=username))

@blissmake.route(Constants.PAYMENT_QR, methods=[Constants.POST])
def payment_qr(username):
    cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
    if not cart:
        flash(Constants.CART_NOT_FOUND, Constants.ERROR)
        return redirect(url_for(
                Constants.BLISSMAKE_HOME, username=username
            ))
    
    total_price = calculate_total_price(cart.get(Constants.PRODUCTS, []))
    
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

@blissmake.route(Constants.GET_FAV)
def get_favorite(username):
    if username == Constants.GUEST:
        return render_template(Constants.LOGIN_HTML)
    favorites = mongo.db.favorites.find_one({Constants.USERNAME: username})
    if not favorites:
        return render_template(Constants.FAV_HTML, username=username, message=Constants.FAV_NOT_EXISTS)
    
    favorites[Constants.ID] = str(favorites[Constants.ID])
    return render_template(Constants.FAV_HTML, username=username, favorites=favorites, message=None)

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
    session.clear()
    return redirect(url_for(Constants.BLISSMAKE_INDEX))