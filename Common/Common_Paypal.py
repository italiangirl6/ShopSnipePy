from selenium.webdriver.common.by import By


class PayPalObjects:
    login_button = '/html/body/div[2]/div/div/div/div/div/div/div/section/div[1]/div[1]/xo-onboard-payment/' \
                            'div/div/xo-login-button/div[1]/div/div[2]/a'
    xpath_login_button = '//*/a[contains(.,\'Log In\')]'
    login_email_input = 'email'
    login_password_input = 'password'
    login_button = 'btnLogin'