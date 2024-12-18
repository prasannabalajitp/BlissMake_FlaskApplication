from flask import session
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from AppConstants.Constants import Constants
from repository.adminrepository import AdminRepository
import os

load_dotenv()

class AdminService:

    UPLOAD_FOLDER = os.path.join(Constants.STATIC, Constants.IMG)
    ALLOWED_EXTENSIONS = Constants.EXTENSIONS

    @staticmethod
    def response_headers(response):
        response.headers[Constants.CACHE_CTRL] = Constants.CACHE_CTRL_VAL
        response.headers[Constants.PRAGMA] = Constants.PRAGMA_VAL
        response.headers[Constants.EXPIRES] = Constants.EXPIRES_VAL

    @staticmethod
    def allowed_file(filename):
        return Constants.IMG_CONDITION in filename and filename.rsplit(Constants.IMG_CONDITION, 1)[1].lower() in AdminService.ALLOWED_EXTENSIONS

    @staticmethod
    def admin_login_service(username, password):   
        if Constants.ADMIN in username: 
            result = AdminRepository.admin_login_repository(username=username, password=password)
        return result
    
    @staticmethod
    def get_all_products():
        return AdminRepository.get_all_products()
    
    @staticmethod
    def get_all_admins():
        return AdminRepository.get_all_admins()
    
    @staticmethod
    def get_admin_by_id(username):
        return AdminRepository.get_admin(username)
    
    @staticmethod
    def get_product_by_id(product_id):
        product = AdminRepository.get_product_by_id(prod_id=product_id)
        return product
    
    @staticmethod
    def add_product_service(prod_id, prod_name, prod_price, prod_img, img_filename):
        product_list = AdminRepository.get_all_products()
        if prod_img and AdminService.allowed_file(img_filename):
            filename = secure_filename(img_filename)
            response = AdminRepository.add_product(product_id=prod_id, product_name=prod_name, product_price=prod_price, product_img=filename)
            if response == Constants.PROD_ADDED:
                prod_img.save(os.path.join(AdminService.UPLOAD_FOLDER, filename))
                product_list = AdminRepository.get_all_products()
                return response, product_list
            else:
                return Constants.DB_ERROR, product_list
        return Constants.NO_IMG_PROVIDED, product_list
    
    @staticmethod
    def update_product_service(product_id, product_name, product_price, product_img):
        update_data = {
            Constants.PRODUCT_NAME: product_name,
            Constants.PRODUCT_PRICE: product_price,
        }
        if product_img:
            update_data[Constants.PRODUCT_IMG] = product_img
        
        try:
            response = AdminRepository.update_product(product_id=product_id, update_data=update_data)
            product_list = AdminRepository.get_all_products()
            return response, product_list
        
        except ValueError as e:
            return str(e), AdminRepository.get_all_products()
        
        except Exception as e:
            return Constants.ERR_UPD, AdminRepository.get_all_products()

    @staticmethod
    def delete_product_service(product_id):
        product = AdminRepository.get_product_by_id(prod_id=product_id)
        if product:
            img_path = os.path.join(AdminService.UPLOAD_FOLDER, product[Constants.PRODUCT_IMG])

            if os.path.exists(img_path):
                os.remove(img_path)
            response = AdminRepository.delete_product(product_id)
            product_list = AdminRepository.get_all_products()

            return response, product_list
        return Constants.PROD_NOT_FOUND, AdminRepository.get_all_products()