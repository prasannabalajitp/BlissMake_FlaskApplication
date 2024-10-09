class Constants:
    #App.py

    SECRET_KEY = 'SECRET_KEY'
    MONGO_URI = 'MONGO_URI'
    MAIL_SERVER = 'MAIL_SERVER'
    MAIL_USERNAME = 'MAIL_USERNAME'
    MAIL_PWD = 'MAIL_PASSWORD'
    MAIN = '__main__'

    #blissmake.py
    BLISSMAKE = 'blissmake'
    ROOT_URL = '/blissmake'

    #admin.py
    ADMIN = 'admin'
    ADMIN_ROOT_URL = '/admin/blissmake'

    GET = 'GET'
    POST = 'POST'
    MESSAGE = "message"
    USER = 'user'
    ERROR = 'error'
    ERROR1  = "error"
    INFO = 'info'

    #urls
    ROOT = '/'
    LOGIN = '/login'
    LOGOUT_ADM = '/logout'
    LOGOUT = '/logout/<username>'
    REGISTER = '/register'
    PROFILE_URL = '/profile/<username>'
    HOME = '/home/<username>'
    HOME_PAGE = '/home/<username>/<password>'
    CHECKOUT = '/checkout/<username>'
    MAIN_HOME_PAGE = '/home'
    PROD_DET_GUEST = '/product/<product_id>/'
    PRODUCT_DETAIL = '/product/<product_id>/<username>'
    GET_CART = '/cart/<username>'
    DELETE_FROM_CART = '/cart/delete/<product_id>/<quantity>/<username>'
    ADD_TO_CART = '/addToCart/<product_id>/<username>'
    UPDATE_QUANTITY = '/cart/update/<product_id>/<action>/<username>'
    PAYMENT = '/payment/<username>'
    PAYMENT_QR = '/payment_qr/<username>'
    ADD_TO_WISHLIST = '/addToWishlist/<username>/<product_id>'
    GET_FAV = '/getfavorite/<username>'
    REMOVE_FAV = '/remove_favorite/<username>/<product_id>'
    ADMIN_DASHBOARD = '/admindashboard'
    ADD_PRODUCT = '/add_product'
    EDIT_PRODUCT = '/edit_product/<product_id>'
    DEL_PRODCUT = '/delete_product/<product_id>'
    UPDATE_PROFILE = '/updateprofile/<username>'
    GENERATE_OTP = '/blissmake/generate_otp'
    FORGOT_PWD = '/forgotpassword'
    VERIFY_OTP = '/blissmake/verify_otp'
    RESET_PWD = '/reset_password/<email>'
    EDIT_ADDR = '/editaddress/<username>'
    EDIT_ADDRESS = '/edit_address/<username>'
    ADM_RELOGIN = '/home/<username>/<password>/<product_id>'

    #HTML
    INDEX_HTML = 'index.html'
    LOGIN_HTML = 'login.html'
    REGISTER_HTML = 'register.html'
    HOME_HTML = 'home.html'
    CHECKOUT_HTML = 'checkout.html'
    PROD_DET_HTML = 'product_detail.html'
    USER_CART_HTML = 'user_cart.html'
    PAYMENT_HTML = 'payment.html'
    QR_PAYMENT_HTML = 'payment_qr.html'
    FAV_HTML = 'favorites.html'
    ADMIN_LOGIN_HTML = 'admin_login.html'
    ADMIN_DASHBOARD_HTML = 'admin_dashboard.html'
    ADMIN_EDIT_HTML = 'admin_edit_product.html'
    PROFILE_HTML = 'profile.html'
    VERIFY_OTP_HTML = 'verify_otp.html'
    FORGOT_PWD_HTML = 'forgot_password.html'
    RESET_PWD_HTML = 'reset_password.html'
    EDIT_ADDR_HTML = 'edit_address.html'


    #Route HTML
    BLISSMAKE_INDEX = 'blissmake.index'
    BLISSMAKE_LOGIN = 'blissmake.login'
    BLISSMAKE_HOME = 'blissmake.home'
    BLISSMAKE_GETCART = 'blissmake.get_cart'
    BLISSMAKE_PROD_DETAIL = 'blissmake.product_detail'
    BLISSMAKE_GET_FAV = 'blissmake.get_favorite'
    ADMIN_INDEX = 'admin.admin_index'
    ADMIN_EDIT_PROD = 'admin.edit_product'
    BLISSMAKE_PROFILE = 'blissmake.profile'
    BLISSMAKE_FORGOT_PWD = 'blissmake.forgot_password'
    BLISSMAKE_PAYMENT = 'blissmake.payment'

    EMPTY = ''
    USERNAME = 'username'
    EMAIL = 'email'
    PASSWORD = 'password'
    NEW_PWD = 'new_password'
    ADDRESS = 'address'
    PHONE = 'phone'
    CNF_PWD = 'confirm_password'
    PROFILE = 'profile'
    OTP = 'otp'
    EXP_TIME = "expiration_time"
    SUB = "Your OTP Code"
    USERNAME_PWD_WRNG = 'Username / Password is wrong!'
    USER_EXISTS = "User Already Exists!"
    USER_NOT_EXISTS = 'User Not Exists'
    ADDED_TO_CART = 'Added to Cart Successfully'
    CART_UPDATED = "Cart updated successfully!"
    PAYMENT_SUCCESS = 'Payment Processed successfully'
    PROD_NOT_FOUND = "Product Not Found"
    PROD_EXISTS = "Product Already Exists in Cart"
    PROD_ADD_WISHLIST = "Product added to wishlist"
    FAV_NOT_EXISTS = 'Favorites Not Exists!'
    PROD_IN_WISHLIST = 'Product already in Wishlist'
    ADDED_TO_WISHLIST = 'Product added to Wishlist'
    REM_FRM_WISHLIST = 'Removed From Wishlist'
    PROD_NOT_WISHLIST = 'Product Not in Wishlist'
    NO_FAV_FOUND = 'No Favorites Found'
    INVALID_ADM_PWD = "Invalid Admin/Admin Password. Please try again..."
    PROD_ADDED = 'Product added successfully!'
    PROD_UPDATED = 'Product updated successfully!'
    PROD_DEL = 'Product deleted successfully!'
    PWD_NOT_MATCH = "Passwords do not match!"
    PRF_UPDATED = "Profile updated successfully!"
    OTP_SENT = "OTP sent successfully!"
    OTP_VERIFIED = "OTP verified successfully"
    PWD_UPDATED = 'Your password has been updated!'
    ERR_UPDATING_PWD = 'Error updating password. Please try again'
    EMAIL_PWD_REQ = 'Email and new password are required.'
    ADDR_UPDATED = 'Address Updated Successfully'
    PASSWORD_HASH_METHOD = 'sha256'
    CART_NOT_FOUND = 'Cart Not Found'
    CART_EMPTY = "Your cart is empty!"
    OTP_EXP = "OTP Expired"
    PRODUCTS = 'products'
    QUANTITY = 'quantity'
    PRODUCT_PRICE = 'product_price'
    INVALID_PASSWORD = 'Invalid Password'
    INVALID_EMAIL_ADDR = "Invalid email address."
    INVALID_OTP = "Invalid OTP."
    PRODUCT_ID = 'product_id'
    PRODUCT_ID_1 = 'product id'
    PRODUCT_NAME = "product_name"
    PRODUCT_PRICE = "product_price"
    PRODUCT_IMG = "product_img"
    PRODUCTS = "products"
    GUEST = 'guest'
    WARNING = "warning"
    PULL = '$pull'
    PUSH = '$push'
    SET = '$set'
    ID = '_id'
    INCREASE = 'increase'
    DECREASE = 'decrease'
    SUCCESS = "success"
    FAILURE = "failure"
    UPI_ID = 'UPI_ID'
    PAYEE_NAME = 'PAYEE_NAME'
    TXN_NOTE = "Payment for QR"
    STRF_TIME = '%Y%m%dT%H%M%SZ'
    VALID_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    CACHE_CTRL = "Cache-Control"
    CACHE_CTRL_VAL = "no-cache, no-store, must-revalidate"
    PRAGMA = "Pragma"
    PRAGMA_VAL = "no-cache"
    EXPIRES = "Expires"
    EXPIRES_VAL = "0"

    #AnalyticClient.py
    INTERCEPTION_KEY = "interception"
    INTERCEPTION = 'HTT_INBOUND'
    USER_ID = 'user_id'
    REQUEST = 'request'
    RESPONSE = 'response'
    HTTP_STATUS_CODE = 'httpStatusCode'
    HTTP_STATUS = 'httpStatus'
    HEADERS = 'headers'
    DATA = 'data'
    HTTP_METHOD_KEY = 'httpMethod'
    HTTP_HEADERS = "httpHeaders"
    CONTENT_TYPE_KEY = "content-type"
    CONTENT_LENGTH_KEY = "content-length"
    DATE = "date"
    ACCEPT = "Accept"
    HOST = "host"

    CONTENT_TYPE = "application/json"
    ACCEPT_TYPE = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    CONNECTION_KEY = "Connection"
    CONNECTION = "keep-alive"
    ACCEPT_LANGUAGE_KEY = "Accept-Language"
    ACCEPT_LANGUAGE = "en-US,en;q=0.9"
    START_TIME = "start time"
    END_TIME = "end time"
    RESPONSE_TIME = "response time"
    RESPONSE_OK = "OK"
    RESPONSE_INT_SER_ERR = "INTERNAL SERVER ERROR"
    RESPONSE_BAD_REQ = "BAD REQUEST"
