class Constants:
    #App.py

    SECRET_KEY = 'SECRET_KEY'
    MONGO_URI = 'MONGO_URI'
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
    PROFILE = '/profile'
    HOME = '/home/<username>'
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
    


    #Route HTML
    BLISSMAKE_INDEX = 'blissmake.index'
    BLISSMAKE_LOGIN = 'blissmake.login'
    BLISSMAKE_HOME = 'blissmake.home'
    BLISSMAKE_GETCART = 'blissmake.get_cart'
    BLISSMAKE_PROD_DETAIL = 'blissmake.product_detail'
    BLISSMAKE_GET_FAV = 'blissmake.get_favorite'
    ADMIN_INDEX = 'admin.admin_index'

    USERNAME = 'username'
    EMAIL = 'email'
    PASSWORD = 'password'
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
    PASSWORD_HASH_METHOD = 'sha256'
    CART_NOT_FOUND = 'Cart Not Found'
    CART_EMPTY = "Your cart is empty!"
    PRODUCTS = 'products'
    QUANTITY = 'quantity'
    PRODUCT_PRICE = 'product_price'
    INVALID_PASSWORD = 'Invalid Username/Password'
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
    UPI_ID = 'upi_id'
    PAYEE_NAME = 'payee_name'
    TXN_NOTE = "Payment for QR"
    STRF_TIME = '%Y%m%dT%H%M%SZ'

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
