from flask import session
from dotenv import load_dotenv
from AppConstants.Constants import Constants
from app import mongo
from models.Product import ProductDetail
from pymongo.errors import PyMongoError
import uuid

load_dotenv()

class AdminRepository:

    @staticmethod
    def get_all_products():
        products = mongo.db.products.find({})
        product_list = list(products)

        return product_list
    
    @staticmethod
    def get_all_admins():
        admin_detail = mongo.db.admin_credentials.find({})
        admins = list(admin_detail)
        return admins
    
    @staticmethod
    def get_admin(username):
        admin_detail = mongo.db.admin_credentials.find_one({Constants.USERNAME: username})
        return admin_detail
    
    @staticmethod
    def get_product_by_id(prod_id):
        return mongo.db.products.find_one({Constants.PRODUCT_ID: prod_id})

    @staticmethod
    def admin_login_repository(username, password):
        admin = mongo.db.admin_credentials.find_one({Constants.USERNAME: username})
        if admin and admin[Constants.PASSWORD] == password:
            session[Constants.USER_ID] = str(uuid.uuid4())
            session[Constants.USERNAME] = username
            print(f"Logged in as: {session[Constants.USERNAME]}")
            products = mongo.db.products.find({})
            product_list = list(products)

            return product_list
        else:
            return Constants.INVALID_ADM_PWD
        
    @staticmethod
    def add_product(product_id, product_name, product_price, product_img):
        try:
            result = mongo.db.products.insert_one(
                    ProductDetail(
                        product_id=product_id,
                        product_name=product_name,
                        product_price=product_price,
                        product_img=product_img
                    ).dict()
                )
            if result.acknowledged == True:
                return Constants.PROD_ADDED
            else:
                return Constants.NO_IMG_PROVIDED
        except Exception as e:
            print(f'Error occured : {e}')
            return Constants.DB_ERROR
    
    @staticmethod
    def delete_product(product_id):
        result = mongo.db.products.delete_one({Constants.PRODUCT_ID: product_id})
        if result.deleted_count > 0:
            return Constants.PROD_DEL
        return Constants.PROD_NOT_FOUND
    
    @staticmethod
    def update_product(product_id, update_data):
        try:
            result = mongo.db.products.update_one(
                {Constants.PRODUCT_ID: product_id},
                {Constants.SET: update_data}
            )

            if result.modified_count > 0:
                return Constants.PROD_UPDATED
            else:
                raise ValueError(Constants.PROD_NOT_FOUND)
        except PyMongoError as e:
            print(f'{Constants.DB_ERROR} : {e}')
            raise
        