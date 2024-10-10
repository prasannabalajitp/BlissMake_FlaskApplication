from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from dotenv import load_dotenv
from datetime import datetime, timezone
from AppConstants.Constants import Constants
from app import mongo
from models.Product import ProductDetail, Product
from models.User import UpdateAddres
from models.Favorite import Favorite
import re, uuid, os, pyqrcode


load_dotenv()
class BlissmakeService:

    @staticmethod
    def index_page():
        products = mongo.db.products.find({})
        product_list = list(products)

        return product_list

    @staticmethod
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

    @staticmethod
    def calculate_total_price(cart_products):
        total_price = 0
        for item in cart_products:
            price = float(item[Constants.PRODUCT_PRICE])
            quantity = int(item[Constants.QUANTITY])
            total_price += price * quantity
        return total_price

    @staticmethod
    def is_valid_email(email):
        pattern = Constants.VALID_EMAIL
        return re.match(pattern, email) is not None

    @staticmethod
    def user_exists(username):
        user_exists = mongo.db.users.find_one({Constants.USERNAME: username})
        if user_exists:
            return Constants.USER_EXISTS
        else:
            return Constants.USER_NOT_EXISTS
        
    @staticmethod
    def response_headers(response):
        response.headers[Constants.CACHE_CTRL] = Constants.CACHE_CTRL_VAL
        response.headers[Constants.PRAGMA] = Constants.PRAGMA_VAL
        response.headers[Constants.EXPIRES] = Constants.EXPIRES_VAL
        
    @staticmethod
    def get_product(prod_id):
        product = mongo.db.products.find_one({Constants.PRODUCT_ID: prod_id})
        if product:
            product_name = product[Constants.PRODUCT_NAME]
            product_img = product[Constants.PRODUCT_IMG]
            product_price = product[Constants.PRODUCT_PRICE]
            return product_name, product_img, product_price

    @staticmethod
    def get_user_address(username):
        user_data = mongo.db.users.find_one({Constants.USERNAME : username})
        if user_data:
            address = user_data.get(Constants.ADDRESS, Constants.EMPTY)
            email = user_data.get(Constants.EMAIL, Constants.EMPTY)

            return address, email
        
    @staticmethod
    def update_user_address(username, new_address):
            result = mongo.db.users.update_one({Constants.USERNAME: username}, {Constants.SET: {Constants.ADDRESS: new_address}})
            return result.acknowledged
        
    @staticmethod
    def product_detail_service(product_id):
        product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
        product_data = ProductDetail(
            product_id=product[Constants.PRODUCT_ID],
            product_name=product[Constants.PRODUCT_NAME],
            product_price=product[Constants.PRODUCT_PRICE],
            product_img=product[Constants.PRODUCT_IMG]
        ).dict()
        
        return product_data

    @staticmethod
    def get_cart_service(username):
        cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
        cart_products = cart[Constants.PRODUCTS] if cart else []
        total_price = BlissmakeService.calculate_total_price(cart_products)

        return cart_products, total_price
    
    @staticmethod
    def get_favorites(username):
        favorites = mongo.db.favorites.find_one({Constants.USERNAME: username})
        if favorites is None:
            return Constants.FAV_NOT_EXISTS
        if not favorites.get(Constants.PRODUCTS):
            return Constants.FAV_NOT_EXISTS
        favorites[Constants.ID] = str(favorites[Constants.ID])

        return favorites

    @staticmethod
    def add_to_wishlist_service(username, product_id):
        product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
        if not product:
            return Constants.PROD_NOT_FOUND
        
        user_favorites = mongo.db.favorites.find_one({
            Constants.USERNAME: username
        })
        if user_favorites:
            if any(fav_product[Constants.PRODUCT_ID] == product_id for fav_product in user_favorites[Constants.PRODUCTS]):
                return Constants.PROD_IN_WISHLIST
            mongo.db.favorites.update_one(
                {Constants.USERNAME : username},
                {Constants.PUSH: {
                Constants.PRODUCTS: ProductDetail(
                        product_id=product[Constants.PRODUCT_ID],
                        product_name=product[Constants.PRODUCT_NAME],
                        product_price=product[Constants.PRODUCT_PRICE],
                        product_img=product[Constants.PRODUCT_IMG]
                    ).dict()
                }}                
            )
            return Constants.ADDED_TO_WISHLIST
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
            )
            result = mongo.db.favorites.insert_one(favorite_data)
            favorite_data[Constants.ID] = str(result.inserted_id)
            return Constants.ADDED_TO_WISHLIST
    
    @staticmethod
    def remove_from_favorites(username, product_id):
        product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
        if not product:
            return Constants.PROD_NOT_FOUND
        user_favorites = mongo.db.favorites.find_one({Constants.USERNAME : username})
        if user_favorites:
            product_exists = any(fav_product[Constants.PRODUCT_ID] == product_id for fav_product in user_favorites[Constants.PRODUCTS])
            if product_exists:
                mongo.db.favorites.update_one(
                    {Constants.USERNAME: username},
                    {Constants.PULL: {Constants.PRODUCTS: {Constants.PRODUCT_ID: product_id}}}
                )
                return Constants.REM_FRM_WISHLIST
            return Constants.PROD_NOT_WISHLIST
        return Constants.NO_FAV_FOUND
    

    @staticmethod
    def register_service(username, email, password):    
        hashed_password = generate_password_hash(password, method=Constants.PASSWORD_HASH_METHOD)
        mongo.db.users.insert_one({
            Constants.USERNAME: username, 
            Constants.EMAIL: email, 
            Constants.PASSWORD: hashed_password
        })
        products = mongo.db.products.find({})
        product_list = list(products)

        return product_list
    
    @staticmethod
    def delete_from_cart_service(username, product_id, quantity):
        del_response = mongo.db.usercart.update_one(
            {Constants.USERNAME: username},
            {Constants.PULL: {Constants.PRODUCTS: {
                    Constants.PRODUCT_ID: product_id, 
                    Constants.QUANTITY: int(quantity)
                }}}
        )

        return del_response.acknowledged
    
    @staticmethod
    def add_to_cart_service(username, prod_id, quantity):
        product_name, product_img, product_price = BlissmakeService.get_product(prod_id=prod_id)
        new_product = Product(
                product_id=prod_id, 
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
        return Constants.ADDED_TO_CART
    
    @staticmethod
    def update_cart_quantity(prod_id, action, username):
        cart = mongo.db.usercart.find_one({Constants.USERNAME : username})
        if not cart:
            return Constants.CART_NOT_FOUND, None
        
        updated = BlissmakeService.update_product_quantity_in_cart(cart=cart, product_id=prod_id, action=action)
        if not updated:
            return Constants.PROD_NOT_FOUND
        mongo.db.usercart.update_one(
            {Constants.USERNAME: username},
            {Constants.SET: {Constants.PRODUCTS: cart[Constants.PRODUCTS]}}
        )
        cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
        cart_products = cart[Constants.PRODUCTS] if cart else []
        total_price = BlissmakeService.calculate_total_price(cart_products)
        if not cart_products:
            return Constants.CART_EMPTY, None
        return cart_products, total_price


    @staticmethod
    def get_profile(username):
        user = mongo.db.users.find_one({Constants.USERNAME : username})
        return user
    
    @staticmethod
    def update_profile_servcice(username, new_password, confirm_password, new_address, phone):
        user = mongo.db.users.find_one({Constants.USERNAME: username})
        if not user:
            return Constants.USER_NOT_EXISTS
        update_data = UpdateAddres(address=new_address, phone=phone).dict()
        if new_password and new_password == confirm_password:
            hashed_password = generate_password_hash(new_password)
            update_data[Constants.PASSWORD] = hashed_password
        elif new_password != confirm_password:
            return Constants.PWD_NOT_MATCH
        mongo.db.users.update_one({Constants.USERNAME: username}, {Constants.SET: update_data})
        return Constants.PRF_UPDATED


    @staticmethod
    def checkout(username):
        cart = mongo.db.usercart.find_one({
            Constants.USERNAME : username
        })
        if not cart:
            return Constants.CART_NOT_FOUND
        products = cart.get(Constants.PRODUCTS, [])
        total_price = BlissmakeService.calculate_total_price(products)
        return products, round(total_price,2)
    
    @staticmethod
    def admin_login(username, password):
        if Constants.ADMIN in username:
            admin_data = mongo.db.admin_credentials.find_one({Constants.USERNAME: username})
            if admin_data:
                admin_password = admin_data[Constants.PASSWORD]
                if admin_password == password:
                    products = mongo.db.products.find({})
                    product_list = list(products)
                    return product_list
                return Constants.USERNAME_PWD_WRNG
            return Constants.INVALID_ADM_PWD
    
    @staticmethod
    def user_login(username, password):
        user = mongo.db.users.find_one({Constants.USERNAME: username})
        if user:
            session[Constants.USER_ID] = str(uuid.uuid4())
            session[Constants.USERNAME] = username
            if check_password_hash(user[Constants.PASSWORD], password):
                session[Constants.USERNAME] = username
                return Constants.SUCCESS
            return Constants.INVALID_PASSWORD
        return Constants.USER_NOT_EXISTS

    @staticmethod
    def payment_qr_service(username):
        cart = mongo.db.usercart.find_one({Constants.USERNAME : username})
        if not cart:
            return Constants.CART_NOT_FOUND, None
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

        return qr_filename, total_price
    