from flask import Blueprint, request, jsonify, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from dotenv import load_dotenv
from app import mongo
from AppConstants.Constants import Constants
from models.Product import ProductDetail, Product
import pyqrcode, os

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

@blissmake.route(Constants.REGISTER, methods=[Constants.GET, Constants.POST])
def register():
    if request.method == Constants.POST:
        username = request.form.get(Constants.USERNAME)
        password = request.form.get(Constants.PASSWORD)

        user_exists = mongo.db.users.find_one({Constants.USERNAME: username})
        if user_exists:
            return jsonify({
                Constants.MESSAGE: Constants.USER_EXISTS
            })

        hashed_password = generate_password_hash(password, method=Constants.PASSWORD_HASH_METHOD)
        mongo.db.users.insert_one({Constants.USERNAME: username, Constants.PASSWORD: hashed_password})
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

@blissmake.route(Constants.PROFILE)
def profile():
    if Constants.USER not in session:
        return redirect(url_for(Constants.BLISSMAKE_LOGIN))

    return f'Hello, {session["user"]}!'

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
        product_image=product[Constants.PRODUCT_IMG]).dict()
    
    return render_template(
        Constants.PROD_DET_HTML, 
        product=product_data, 
        username=username
    )

@blissmake.route(Constants.GET_CART, methods=[Constants.GET])
def get_cart(username):
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
        {Constants.PULL: {Constants.PRODUCTS: {Constants.PRODUCT_ID: product_id, Constants.QUANTITY: quantity}}}
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
        
        flash(Constants.ADDED_TO_CART)
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
                Constants.PRODUCTS: {
                    'product_id': product[Constants.PRODUCT_ID],
                    'product_name': product[Constants.PRODUCT_NAME],
                    'product_price': product[Constants.PRODUCT_PRICE],
                    'product_img': product[Constants.PRODUCT_IMG]
                }
            }}
        )
        flash(Constants.ADDED_TO_WISHLIST, Constants.SUCCESS)
        print(session)
    else:
        favorite_data = {
            'username': username,
            'products':[{
                'product_id': product[Constants.PRODUCT_ID],
                'product_name': product[Constants.PRODUCT_NAME],
                'product_price': product[Constants.PRODUCT_PRICE],
                'product_img': product[Constants.PRODUCT_IMG]
            }]
        }
        result = mongo.db.favorites.insert_one(favorite_data)
        favorite_data[Constants.ID] = str(result.inserted_id)
        flash(Constants.ADDED_TO_WISHLIST, Constants.SUCCESS)
        print(session)
    return redirect(url_for(Constants.BLISSMAKE_PROD_DETAIL, product_id=product_id, username=username))

@blissmake.route(Constants.GET_FAV)
def get_favorite(username):
    favorites = mongo.db.favorites.find_one({Constants.USERNAME: username})
    if not favorites:
        return render_template(Constants.FAV_HTML, username=username, message=Constants.FAV_NOT_EXISTS)
    
    favorites[Constants.ID] = str(favorites[Constants.ID])
    return render_template(Constants.FAV_HTML, username=username, favorites=favorites, message=None)

@blissmake.route(Constants.LOGOUT, methods=[Constants.GET])
def logout(username):
    session.clear()
    return redirect(url_for(Constants.BLISSMAKE_INDEX))
