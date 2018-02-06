from selenium.webdriver.common.by import By


class GameStopObjects:
    item_price = 'ats-prodBuy-price'
    item_add_to_cart = '//div[@class=\'buy1 ats-prodBuy-buyBoxSec\']//*/a[contains(.,\'Add to Cart\')]'
    login_username = 'username'
    login_password = 'password'
    login_stay_logged_in_check_box = 'label.btnLabel'
    login_button = 'button.ats-loginbtn'
    account_status = '//li[@id=\'hrd-greeting\']/a'
    login_status_label = '#signin > h2'
    item_checkout = 'checkoutButton'
    shopping_cart_label = '/html/body/div[1]/div[4]/div[3]/h1'
    shopping_cart_item_1_Qty = 'cartCount'
    checkout_paypal_button = 'cartpaypalbtn'
