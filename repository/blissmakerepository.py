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

class BlissmakeRepository:

    @staticmethod
    def get_all_products():
        products = mongo.db.products.find({})
        product_list = list(products)
        return product_list
    
    @staticmethod
    def chech_user_exists(username):
        user_exists = mongo.db.users.find_one({Constants.USERNAME : username})
        if user_exists:
            return Constants.USER_EXISTS
        else:
            return Constants.USER_NOT_EXISTS
    
    @staticmethod
    def get_products(prod_id):
        product = mongo.db.products.find_one({Constants.PRODUCT_ID: prod_id})
        if product:
            return product
        return Constants.PROD_NOT_FOUND
    
    @staticmethod
    def get_user_data(username):
        user = mongo.db.users.find_one({Constants.USERNAME : username})
        return user
    
    @staticmethod
    def get_cart(username):
        cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
        return cart
    
    @staticmethod
    def get_favorites(username):
        favorites = mongo.db.favorites.find_one({Constants.USERNAME: username})
        return favorites

    @staticmethod
    def update_address(username, address):
        update_result = mongo.db.users.update_one(
                            {Constants.USERNAME: username}, 
                            {Constants.SET: {
                                    Constants.ADDRESS: address
                                }
                            }
                        )
        return update_result.acknowledged
    
    @staticmethod
    def add_to_wishlist(username, user_favorites, product_id, product):
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
            ).dict()
            result = mongo.db.favorites.insert_one(favorite_data)
            favorite_data[Constants.ID] = str(result.inserted_id)
            return Constants.ADDED_TO_WISHLIST
        

    @staticmethod
    def remove_from_wishlist(username, user_favorites, product_id):
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
    def user_register_repository(username, email, hashed_password):
        mongo.db.users.insert_one({
            Constants.USERNAME: username, 
            Constants.EMAIL: email, 
            Constants.PASSWORD: hashed_password
        })
        products = mongo.db.products.find({})
        product_list = list(products)
        return product_list
    
    @staticmethod
    def delete_from_cart_repository(username, prod_id, quantity):
        del_response = mongo.db.usercart.update_one(
            {Constants.USERNAME: username},
            {Constants.PULL: {Constants.PRODUCTS: {
                    Constants.PRODUCT_ID: prod_id, 
                    Constants.QUANTITY: int(quantity)
                }}}
        )
        return del_response
    
    @staticmethod
    def add_to_cart_repository(username, new_product    ):
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
    def update_cart_quantity_repository(username, cart):
        mongo.db.usercart.update_one(
            {Constants.USERNAME: username},
            {Constants.SET: {Constants.PRODUCTS: cart[Constants.PRODUCTS]}}
        )
        cart = mongo.db.usercart.find_one({Constants.USERNAME: username})
        cart_products = cart[Constants.PRODUCTS] if cart else []
        if not cart_products:
            return Constants.CART_EMPTY, None
        return cart_products
    
    @staticmethod
    def update_profile_repository(username, update_data):
        result = mongo.db.users.update_one(
            {
                Constants.USERNAME: username
            }, 
            {
                Constants.SET: update_data
            })
        return result.acknowledged
        
    @staticmethod
    def checkout_repository(username):
        cart = mongo.db.usercart.find_one({
            Constants.USERNAME: username
        })
        if not cart:
            return Constants.CART_NOT_FOUND
        products = cart.get(Constants.PRODUCTS, [])
        return products
    
    @staticmethod
    def admin_login_repository(username, password):
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
    def user_login_repository(username, password):
        user = mongo.db.users.find_one({Constants.USERNAME: username})
        if user:
            session[Constants.USER_ID] = str(uuid.uuid4())
            session[Constants.USERNAME] = username
            if check_password_hash(user[Constants.PASSWORD], password):
                session[Constants.USERNAME] = username
                return Constants.SUCCESS
            return Constants.INVALID_PASSWORD
        return Constants.USER_NOT_EXISTS