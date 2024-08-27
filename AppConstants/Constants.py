class Constants:
    #App.py

    SECRET_KEY = 'SECRET_KEY'
    MONGO_URI = 'MONGO_URI'
    MAIN = '__main__'

    #blissmake.py
    BLISSMAKE = 'blissmake'
    ROOT_URL = '/blissmake'

    GET = 'GET'
    POST = 'POST'
    MESSAGE = "message"
    USER = 'user'
    ERROR = 'error'
    ERROR1  = "error"

    #urls
    ROOT = '/'
    LOGIN = '/login'
    LOGOUT = '/logout/<username>'
    REGISTER = '/register'
    PROFILE = '/profile'
    HOME = '/home/<username>'
    CHECKOUT = '/checkout/<username>'
    MAIN_HOME_PAGE = '/home'
    PRODUCT_DETAIL = '/product/<product_id>/<username>'
    GET_CART = '/cart/<username>'
    DELETE_FROM_CART = '/cart/delete/<product_id>/<quantity>/<username>'
    ADD_TO_CART = '/addToCart/<product_id>/<username>'
    UPDATE_QUANTITY = '/cart/update/<product_id>/<action>/<username>'
    PAYMENT = '/payment/<username>'
    PAYMENT_QR = '/payment_qr/<username>'
    ADD_TO_WISHLIST = '/addToWishlist/<username>/<product_id>'
    GET_FAV = '/getfavorite/<username>'

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


    #Route HTML
    BLISSMAKE_INDEX = 'blissmake.index'
    BLISSMAKE_LOGIN = 'blissmake.login'
    BLISSMAKE_HOME = 'blissmake.home'
    BLISSMAKE_GETCART = 'blissmake.get_cart'
    BLISSMAKE_PROD_DETAIL = 'blissmake.product_detail'

    USERNAME = 'username'
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