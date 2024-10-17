from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from AppConstants.Constants import Constants
from app import mongo
from models.Product import ProductDetail, Product
from models.User import UpdateAddres
from models.User import User
from models.Favorite import Favorite
from repository.blissmakerepository import BlissmakeRepository
import re, uuid, os, pyqrcode, random, string, smtplib


load_dotenv()
class BlissmakeService:

    @staticmethod
    def index_page():
        products = BlissmakeRepository.get_all_products()
        return products

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
        user_exists = BlissmakeRepository.chech_user_exists(username=username)
        return user_exists
        
    @staticmethod
    def response_headers(response):
        response.headers[Constants.CACHE_CTRL] = Constants.CACHE_CTRL_VAL
        response.headers[Constants.PRAGMA] = Constants.PRAGMA_VAL
        response.headers[Constants.EXPIRES] = Constants.EXPIRES_VAL
        
    @staticmethod
    def get_product(prod_id):
        product = BlissmakeRepository.get_products(prod_id=prod_id)
        if product is None:
            return Constants.PROD_NOT_FOUND
        product_name = product[Constants.PRODUCT_NAME]
        product_img = product[Constants.PRODUCT_IMG]
        product_price = product[Constants.PRODUCT_PRICE]
        return product_name, product_img, product_price

    @staticmethod
    def get_user_address(username):
        user_data = BlissmakeRepository.get_user_data(username=username)
        if user_data:
            address = user_data.get(Constants.ADDRESS, Constants.EMPTY)
            email = user_data.get(Constants.EMAIL, Constants.EMPTY)

            return address, email
        
    @staticmethod
    def update_user_address(username, new_address):
            result = BlissmakeRepository.update_address(username=username, address=new_address)
            return result
        
    @staticmethod
    def product_detail_service(product_id):
        product = BlissmakeRepository.get_products(prod_id=product_id)
        product_data = ProductDetail(
            product_id=product[Constants.PRODUCT_ID],
            product_name=product[Constants.PRODUCT_NAME],
            product_price=product[Constants.PRODUCT_PRICE],
            product_img=product[Constants.PRODUCT_IMG]
        ).dict()
        
        return product_data

    @staticmethod
    def get_cart_service(username):
        cart = BlissmakeRepository.get_cart(username=username)
        cart_products = cart[Constants.PRODUCTS] if cart else []
        total_price = BlissmakeService.calculate_total_price(cart_products)

        return cart_products, total_price
    
    @staticmethod
    def get_favorites(username):
        favorites = BlissmakeRepository.get_favorites(username=username)
        if favorites is None:
            return Constants.FAV_NOT_EXISTS
        if not favorites.get(Constants.PRODUCTS):
            return Constants.FAV_NOT_EXISTS
        favorites[Constants.ID] = str(favorites[Constants.ID])

        return favorites

    @staticmethod
    def add_to_wishlist_service(username, product_id):
        product = BlissmakeRepository.get_products(prod_id=product_id)
        if not product:
            return Constants.PROD_NOT_FOUND

        user_favorites = BlissmakeRepository.get_favorites(username=username)
        result =BlissmakeRepository.add_to_wishlist(username=username, user_favorites=user_favorites, product_id=product_id, product=product)
        return result
    
    @staticmethod
    def remove_from_favorites(username, product_id):
        product = BlissmakeRepository.get_products(prod_id=product_id)
        if not product:
            return Constants.PROD_NOT_FOUND
        user_favorites = BlissmakeRepository.get_favorites(username=username)
        result = BlissmakeRepository.remove_from_wishlist(username=username, user_favorites=user_favorites, product_id=product_id)
        return result
    

    @staticmethod
    def register_service(username, email, password):
        if Constants.ADMIN in username: 
            return Constants.INVALID_USR_NAME
        hashed_password = generate_password_hash(password, method=Constants.PASSWORD_HASH_METHOD)
        reg_response = BlissmakeService.user_exists(username=username)
        if reg_response == Constants.USER_EXISTS:
            return Constants.USER_EXISTS
        else:
            result = BlissmakeRepository.user_register_repository(username=username, email=email, hashed_password=hashed_password)
            return result
    
    @staticmethod
    def delete_from_cart_service(username, product_id, quantity):
        cart = BlissmakeRepository.get_cart(username=username)
        if cart is None:
            return Constants.CART_NOT_FOUND

        del_response = BlissmakeRepository.delete_from_cart_repository(username=username, prod_id=product_id, quantity=quantity)
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
        result = BlissmakeRepository.add_to_cart_repository(username=username, new_product=new_product)
        return result
    
    @staticmethod
    def update_cart_quantity(prod_id, action, username):
        cart = BlissmakeRepository.get_cart(username=username)
        if not cart:
            return Constants.CART_NOT_FOUND, None
        
        updated = BlissmakeService.update_product_quantity_in_cart(cart=cart, product_id=prod_id, action=action)
        if not updated:
            return Constants.PROD_NOT_FOUND
        cart_products = BlissmakeRepository.update_cart_quantity_repository(username=username, cart=cart)
        if isinstance(cart_products, list):
            total_price = BlissmakeService.calculate_total_price(cart_products)
            return cart_products, total_price
        return cart_products, None


    @staticmethod
    def get_profile(username):
        user = BlissmakeRepository.get_user_data(username=username)
        return user
    
    @staticmethod
    def get_user_by_name(username):
        user = BlissmakeRepository.get_user_data(username=username)
        if not user:
            return Constants.USER_NOT_EXISTS
        return User(
            username=user[Constants.USERNAME],
            email=user[Constants.EMAIL],
            address=user.get(Constants.ADDRESS, Constants.EMPTY),
            phone=user.get(Constants.PHONE, Constants.EMPTY)
        )

    
    @staticmethod
    def update_profile_servcice(username, new_password, confirm_password, new_address, phone):
        user = BlissmakeRepository.get_user_data(username=username)
        if not user:
            return Constants.USER_NOT_EXISTS
        update_data = UpdateAddres(address=new_address, phone=phone).dict()
        if new_password and new_password == confirm_password:
            hashed_password = generate_password_hash(new_password)
            update_data[Constants.PASSWORD] = hashed_password
        elif new_password != confirm_password:
            return Constants.PWD_NOT_MATCH
        update_profile = BlissmakeRepository.update_profile_repository(username=username, update_data=update_data)
        if update_profile:
            return Constants.PRF_UPDATED


    @staticmethod
    def checkout(username):
        products = BlissmakeRepository.checkout_repository(username=username)
        total_price = BlissmakeService.calculate_total_price(products)
        return products, round(total_price,2)
    
    @staticmethod
    def admin_login(username, password):
        if Constants.ADMIN in username:
            admin_data = BlissmakeRepository.admin_login_repository(username=username, password=password)
            return admin_data
    
    @staticmethod
    def user_login(username, password):
        user = BlissmakeRepository.user_login_repository(username=username, password=password)
        return user

    @staticmethod
    def payment_qr_service(username):
        cart = BlissmakeRepository.get_cart(username=username)
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
    
    @staticmethod
    def generate_otp_service(email):
        if not email or not BlissmakeService.is_valid_email(email):
            return Constants.INVALID_EMAIL_ADDR
        
        otp = Constants.EMPTY.join(random.choices(string.ascii_letters + string.digits, k=6))
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=5)

        _ = BlissmakeRepository.generate_user_otp_repository(email=email, otp=otp, expiration_time=expiration_time)

        try:
            with smtplib.SMTP(os.getenv(Constants.MAIL_SERVER), 587) as server:
                server.starttls()
                server.login(os.getenv(Constants.MAIL_USERNAME), os.getenv(Constants.MAIL_PWD))
                subject = Constants.SUB
                body = f"Your OTP is: {otp}"
                msg = f"Subject: {subject}\n\n{body}"

                server.sendmail(os.getenv(Constants.MAIL_USERNAME), email, msg)
                return Constants.OTP_SENT
        except smtplib.SMTPException as e:
            return f"Error sending email: {str(e)}"


    @staticmethod
    def verify_otp_service(email, user_otp):
        expiration_time, otp = BlissmakeRepository.verify_otp_repository(email=email)
        current_time = datetime.now(timezone.utc)
        if current_time > expiration_time:
            return Constants.OTP_EXP
        else:
            if user_otp == otp:
                return Constants.OTP_VERIFIED
            else:
                return Constants.INVALID_OTP
                
    @staticmethod
    def reset_password_service(email, password):
        if email and password:
            hashed_password = generate_password_hash(password)  # Hash the password
            result = mongo.db.users.update_one({Constants.EMAIL: email}, {Constants.SET: {Constants.PASSWORD: hashed_password}})
            if result.modified_count > 0:
                mongo.db.otp.delete_many({Constants.EMAIL: email})  # Remove OTP after use
                print(mongo.db.users.find_one({Constants.EMAIL: email}))
                return Constants.PWD_UPDATED
            else:
                return Constants.ERR_UPDATING_PWD
        else:
            return Constants.EMAIL_PWD_REQ