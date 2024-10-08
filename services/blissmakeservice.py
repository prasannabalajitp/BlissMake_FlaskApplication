from werkzeug.security import generate_password_hash, check_password_hash
from AppConstants.Constants import Constants
from app import mongo
from models.Product import ProductDetail
import re

class BlissmakeService:

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
    def product_detail_service(product_id):
        product = mongo.db.products.find_one({Constants.PRODUCT_ID: product_id})
        product_data = ProductDetail(
            product_id=product[Constants.PRODUCT_ID],
            product_name=product[Constants.PRODUCT_NAME],
            product_price=product[Constants.PRODUCT_PRICE],
            product_img=product[Constants.PRODUCT_IMG]).dict()
        
        return product_data

    @staticmethod
    def get_cart_service(username):
        cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
        cart_products = cart[Constants.PRODUCTS] if cart else []
        total_price = BlissmakeService.calculate_total_price(cart_products)

        return cart_products, total_price

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
    def home_service():
        products = mongo.db.products.find({})
        product_list = list(products)

        return product_list