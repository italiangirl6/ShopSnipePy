#!/usr/bin/env python
import configparser
import datetime
import unittest
import os
from decimal import Decimal

import pymysql
import requests
import time

from pyvirtualdisplay import Display, display
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from trollius import wait_for
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from Common.Common_BestBuy import BestBuyObjects as _bbo
from Common.Common_Paypal import PayPalObjects as _ppo
from Common.Common_GameStop import GameStopObjects as _gso
from Common.Common_Toys_r_Us import ToysRUsObjects as _truo
from Common.Common_Walmart import WalmartObjects as Walmart
from setup import cwd_dir


# TODO: Add config variables to the top
# TODO: Use or remove unused variables
# TODO: Separate the helpful functions to their own class page
# TODO: Make wait times more implicit
# TODO: pep8 warning - do not use bare except
# TODO: switch_to_window deprecation?
# TODO: extreme code clean up

class wait_for_page_load(object):
    # http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        self.old_page = self.driver.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.driver.find_element_by_tag_name('html')
        print("Page should be loaded: " + new_page + "\nOld page: " + self.old_page.id)
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded, 6900)


class driver_setup:
    cwd_dir = os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def get_driver():
        gecko_location = cwd_dir + './geckodriver'
        return webdriver.Firefox(executable_path=gecko_location)


class Init(unittest.TestCase):
    set_timeout = 9600

    def setUp(self):
        display = Display(visible=0, size=(800, 600))
        display.start()
        gecko_location = cwd_dir + './geckodriver'
        self.driver = webdriver.Firefox(executable_path=gecko_location)

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def wait_for_element_to_appear(self, how, what, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout). \
                until(EC.presence_of_element_located((how, what)))
        except NoSuchElementException as e:
            return e
        return element

    def enter_text(self, how, what, text):
        self.driver.find_element(how, what).clear()
        self.driver.find_element(how, what).send_keys(text)

    def wait_for_page_load(self, timeout=30):
        old_page = self.driver.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.driver, timeout).until(
            staleness_of(old_page)
        )

    def wait_for_text_appear(self, how, what, target_text, timeout=60, wait=1):
        for i in range(timeout):
            try:
                if target_text == self.driver.find_element(how, what).text: break
            except:
                pass
            time.sleep(wait)
        else:
            self.fail("time out")

    def wait_for_element_present(self, how, what, wait=1, timeout=60):
        for i in range(timeout):
            try:
                if self.is_element_present(how, what): break
            except:
                pass
            time.sleep(wait)
        else:
            self.fail("time out")

    def wait_for_element_not_present(self, how, what, wait=1, timeout=60):
        for i in range(timeout):
            try:
                if not self.is_element_present(how, what): break
            except:
                pass
            time.sleep(wait)
        else:
            self.fail("time out")

    def check_element_exists(self):
        try:
            element = self.driver.find_element_by_partial_link_text("Outside Europe")
            print("Element Found: " + element)
            return element
        except NoSuchElementException:
            print("Element Not Found")
            return False

    def click_element(self, locator, timeout):
        self.wait_for_element_present(locator, timeout)
        self.driver.find_element(locator).click()

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def call_db_select(self, query):
        config = configparser.ConfigParser()
        config.read(cwd_dir + '/config.ini')
        conn = pymysql.connect(host=config['Database']['db_host'],
                               user=config['Database']['db_username'],
                               password=config['Database']['db_password'],
                               db='shopsnipepy_schema')
        try:
            # cursor = conn.cursor()
            wanted_value = ''
            with conn.cursor() as cursor:
                # Read a single record
                sql_wanted_value = query
                cursor.execute(sql_wanted_value)
                wanted_value = str(cursor.fetchone()[0])
        finally:
            conn.close()
            return wanted_value

    def call_db_insert(self, query):
        # Connect to the database
        config = configparser.ConfigParser()
        config.read(cwd_dir + '/config.ini')
        conn = pymysql.connect(host=config['Database']['db_host'],
                               user=config['Database']['db_username'],
                               password=config['Database']['db_password'],
                               db='shopsnipepy_schema')

        try:
            with conn.cursor() as cursor:
                # Create a new record
                sql = query
                cursor.execute(sql)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            conn.commit()
        finally:
            conn.close()

    def test_game_stop(self):
        config = configparser.ConfigParser()
        config.read(cwd_dir + '/config.ini')
        now = datetime.datetime.now()
        current_run_time = now.isoformat().replace('T', ' ')
        print('\nRunning GameStop\nCurrent RunTime - {}'.format(current_run_time))

        driver = self.driver
        custom_timeout = 8999
        allow_purchase = 'true'

        spending_spent = self.call_db_select(query='select spent from shopsnipepy_schema.wallet')
        spending_limit = self.call_db_select(query='select willing_to_spend from shopsnipepy_schema.wallet')
        spending_spent = Decimal(spending_spent)
        spending_limit = Decimal(spending_limit)
        print('Spending Allow: {0}\nSpent: {1}'.format(spending_limit, spending_spent))

        while spending_spent < spending_limit:
            if spending_spent == spending_limit:
                print('Spending limit: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
                driver.close()
                driver.quit()
            elif spending_spent > spending_limit:
                print('Spending limit: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
                driver.close()
                driver.quit()

            driver.get(config['GameStop']['gamestop_producturl'])
            self.wait_for_page_load(timeout=custom_timeout)

            # Check if Available
            not_available = \
                self.is_element_present(By.XPATH, "//span[contains(.,'                                    Not"
                                                  " Available')]")
            print('Not Available Button Found > {}'.format(not_available))
            if not_available == True:
                not_available_text = driver.find_element(By.XPATH, "//span[contains(.,'Not Available')]").text
                if 'Not Available' in not_available_text:
                    print('Closing Scenario\n'
                          ' - Button Text: {}'.format(not_available_text))
                    driver.quit()
                    break
                else:
                    print('\nThe Not Available Button was Found but did not have Not Available pulled'
                          ' from the text?\nPulled: {}'.format(not_available_text))
            else:
                self.assertEqual("Add to Cart", driver.find_element_by_css_selector(
                    "#mainContentPlaceHolder_dynamicContent_ctl00_RepeaterRightColumnLayouts_RightColumnPlaceHolder_0_"
                    "ctl00_0_ctl00_0_StandardPlaceHolder_2_ctl00_2_rptBuyBoxes_2_lnkAddToCart_0 > span").text)

            # Logging In
            self.wait_for_element_to_appear(how=By.XPATH, what=_gso.account_status, timeout=custom_timeout)
            account_status = driver.find_element(By.XPATH, _gso.account_status).text
            print('Current Status: {}'.format(account_status))
            if account_status == 'Sign In\nYour Account':
                driver.find_element(By.XPATH, _gso.account_status).click()
                self.wait_for_page_load(timeout=custom_timeout)
                self.wait_for_page_load(timeout=custom_timeout)
                time.sleep(6)
                self.wait_for_element_to_appear(how=By.CSS_SELECTOR, what=_gso.login_status_label,
                                                timeout=custom_timeout)
                self.wait_for_element_to_appear(how=By.ID, what=_gso.login_username, timeout=custom_timeout)
                self.enter_text(how=By.ID, what=_gso.login_username, text=config['GameStop']['gamestop_username'])
                self.enter_text(how=By.ID, what=_gso.login_password, text=config['GameStop']['gamestop_password'])
                driver.find_element(By.CSS_SELECTOR, _gso.login_stay_logged_in_check_box).click()
                driver.find_element(By.CSS_SELECTOR, _gso.login_button).click()
                time.sleep(6)
                self.wait_for_page_load(timeout=custom_timeout)

            # Check Login account again
            self.wait_for_element_to_appear(how=By.XPATH, what=_gso.account_status, timeout=custom_timeout)
            account_status = driver.find_element(By.XPATH, _gso.account_status).text
            print('Current Status: {}'.format(account_status))
            if account_status == 'Sign In\nYour Account':
                driver.quit()

            # Add to cart
            # ----- Collect current window! Switch to just encase
            current_window = driver.current_window_handle
            driver.find_element(By.XPATH, _gso.item_add_to_cart).click()
            self.wait_for_text_appear(By.ID, _gso.item_checkout, 'Checkout', custom_timeout)
            item_in_cart = driver.find_element_by_id("cartCount").text
            # ERROR: Caught exception [ERROR: Unsupported command [selectWindow | null | ]]
            item_actual_price = self.is_element_present(By.CSS_SELECTOR, "li.price")
            print('Item in Cart: {0}\nActual Price: {1}'.format(item_in_cart, item_actual_price))
            self.wait_for_element_to_appear(By.ID, 'checkoutButton', custom_timeout)
            driver.find_element_by_id("checkoutButton").click()
            # self.wait_for_page_load(custom_timeout)
            time.sleep(10)
            # class = 'addToCartErrorMessage', messsage = 'The item cannot be added to the cart. \
            # 'You have exceeded the maximum purchase quantity for this item.'

            # Shopping Cart
            driver.switch_to.window(current_window)
            self.wait_for_element_to_appear(By.ID, 'Quantity', custom_timeout)
            quantity = driver.find_element(By.ID, 'Quantity')
            current_quantity = quantity.get_attribute('value')
            time.sleep(2)
            self.wait_for_page_load(custom_timeout)
            if current_quantity != 1:
                qt_elements = driver.find_elements(By.XPATH, '//*/input[@id=\'Quantity\']')
                qt_elements[1].clear()
                qt_elements[1].send_keys('1')
                driver.find_element(By.LINK_TEXT, 'Update').click()
                self.wait_for_page_load(timeout=custom_timeout)
                time.sleep(4)
            shopping_cart_sub_total = driver.find_element_by_css_selector("td.ats-subtotal").text
            print('Item in Qty: {0}\nSub Total: {1}'.format(current_quantity, shopping_cart_sub_total))
            product_price = shopping_cart_sub_total

            # Begin Payal
            driver.find_element(By.ID, _gso.checkout_paypal_button).click()
            time.sleep(7)
            url_check = driver.current_url
            if url_check == 'https://www.gamestop.com/checkout/?paypalstatus=unavailable':
                print('Paypal is not available!?\nurl_check: {}'.format(url_check))
                driver.close()
            self.wait_for_page_load(timeout=custom_timeout)
            self.wait_for_element_to_appear(how=By.CSS_SELECTOR, what='p.loader', timeout=custom_timeout)
            time.sleep(14)
            paypal_title = driver.title
            print('Paypal title: {}'.format(paypal_title))
            driver.find_element_by_link_text("Log In").click()
            time.sleep(9)
            self.wait_for_page_load(custom_timeout)
            self.wait_for_element_to_appear(By.ID, _ppo.login_email_input)
            self.enter_text(By.ID, _ppo.login_email_input, config['PayPal']['pp_username'])
            driver.find_element(By.ID, 'btnNext').click()
            self.wait_for_page_load(custom_timeout)
            self.enter_text(By.ID, _ppo.login_password_input, config['PayPal']['pp_password'])
            driver.find_element_by_id("btnLogin").click()
            for i in range(60):
                try:
                    if self.is_element_present(By.CSS_SELECTOR, "div.lockIcon"): break
                except:
                    pass
                time.sleep(1)
            else:
                self.fail("time out")
            for i in range(60):
                try:
                    if self.is_element_present(By.ID, "spinnerMessage"): break
                except:
                    pass
                time.sleep(1)
            else:
                self.fail("time out")
            self.wait_for_page_load()
            self.wait_for_page_load()
            time.sleep(13)
            driver.find_element_by_id("confirmButtonTop").click()
            self.wait_for_page_load()
            time.sleep(13)
            driver.switch_to.window(current_window)
            curret_window_title = driver.title
            print('Current Window: {}'.format(curret_window_title))

            # PayPal Place order
            if allow_purchase == 'true':
                self.wait_for_page_load()
                self.wait_for_element_to_appear(By.ID, 'shipsubmitbtn')
                driver.find_element(By.ID, 'shipsubmitbtn').click()
                for i in range(60):
                    try:
                        if "SUBMIT ORDER" == driver.find_element_by_link_text("SUBMIT ORDER").text: break
                    except:
                        pass
                    time.sleep(1)
                else:
                    self.fail("time out")
                driver.find_element_by_link_text("SUBMIT ORDER").click()
                self.wait_for_page_load()

                # Order confirmation
                self.wait_for_element_to_appear(By.CLASS_NAME, "rpt-ordernumber")
                game_stop_order_number = driver.find_element_by_class_name("rpt-ordernumber").text
                product_price = product_price.strip('$')

                # Update DB
                new_spent_value = product_price + spending_spent
                sql_cmd = 'insert into shopsnipepy_schema.purchases (' \
                          'transation_id, price, store) ' \
                          'values (\'{0}\', {1}, \'Game Stop\')' \
                    .format(game_stop_order_number, product_price, 'Game Stop')
                sql_wallet_update = 'update shopsnipepy_schema.wallet ' \
                                    'set Spent = \'{0}\'' \
                                    'where willing_to_spend = \'{1}\''.format(new_spent_value, '269')
                self.call_db_insert(query=sql_cmd)
                self.call_db_insert(query=sql_wallet_update)
                if new_spent_value > spending_limit:
                    break;
            else:
                print('Allow purchase: {}'.format(allow_purchase))
                driver.close()

    def test_walmart(self):
        config = configparser.ConfigParser()
        config.read(cwd_dir + '/config.ini')
        print('Running > WalMart')
        driver = self.driver
        custom_timeout = 9600

        # Check if purchase is allowed & spending limit allows for purchase
        allow_purchase = config['Site_Selection']['allow_purchase']
        spending_spent = self.call_db_select(query='select spent from shopsnipepy_schema.wallet')
        spending_limit = self.call_db_select(query='select willing_to_spend from shopsnipepy_schema.wallet')
        spending_spent = Decimal(spending_spent)
        spending_limit = Decimal(spending_limit)
        print('Spending Allow: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
        if spending_spent == spending_limit:
            print('Spending limit: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
            driver.close()
            driver.quit()
        elif spending_spent > spending_limit:
            print('Spending limit: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
            driver.close()
            driver.quit()


        # API Check
        use_walmart_api = config['Walmart']['walmart_apikey']
        add_to_cart_url = config['Walmart']['walmart_producturl']
        if 'none' not in use_walmart_api:
            walmart_upc = config['Walmart']['walmart_productupc']
            json_raw = requests.get(
                'http://api.walmartlabs.com/v1/items?apiKey=' + use_walmart_api + '&upc=' + walmart_upc)
            walmart_json = json_raw.json()

            print(walmart_json)
            if json_raw.content != 200:
                availability_online = ""
                for key in walmart_json['items']:
                    name = key['name'],
                    add_to_cart_url = key['addToCartUrl']
                    stock = key['stock']
                    sale_price = key['salePrice'],
                    availability = key['stock'],
                    availability_online = key['availableOnline']
                    product_url = key['productUrl']

                self.assertEqual(availability_online, bool(True), "Item not available online")

        # Navigate
        print('OK -> Item available Online!\n')
        print('Navigating to: ' + str(add_to_cart_url))
        driver.get(add_to_cart_url)

        # Handle Logging in
        self.wait_for_element_to_appear(By.LINK_TEXT, 'Hello. Sign In')
        driver.find_element_by_link_text("Hello. Sign In").click()
        self.wait_for_page_load(timeout=custom_timeout)
        self.wait_for_page_load(timeout=custom_timeout)
        self.wait_for_element_to_appear(By.NAME, 'password')
        self.wait_for_element_to_appear(By.ID, 'checkbox-0')
        self.wait_for_element_to_appear(By.NAME, 'email')
        self.enter_text(By.NAME, Walmart.email_address_input, config['Walmart']['walmart_username'])
        self.enter_text(By.NAME, Walmart.password_input, config['Walmart']['walmart_password'])
        keep_logged_in_checkbox = driver.find_element_by_id(Walmart.keep_signed_in_checkbox).get_attribute('value')
        if keep_logged_in_checkbox == 'true':
            driver.find_element_by_id(Walmart.keep_signed_in_checkbox).click()
        time.sleep(2)
        driver.find_element_by_css_selector(Walmart.sign_in_button).click()
        time.sleep(6)
        self.wait_for_page_load()

        # Assert we are not at user login landing page
        track_package_exists = self.is_element_present(By.CLASS_NAME, Walmart.tracking_truck_icon)
        if track_package_exists == 'True':
            driver.get(add_to_cart_url)
            self.wait_for_page_load()

        # Deal with Quantity
        self.wait_for_element_to_appear(By.CLASS_NAME, Walmart.quantity_dropdown)
        quantity_dropdown = Select(driver.find_elements_by_class_name(Walmart.quantity_dropdown)[0])
        can_purchase = quantity_dropdown.__sizeof__()
        quantity_dropdown.select_by_index(0)
        driver.find_elements_by_class_name(Walmart.quantity_dropdown)[0].send_keys(Keys.TAB)
        self.wait_for_element_to_appear(By.CLASS_NAME, 'spinner')
        time.sleep(4)

        # Check Zip
        zip_label = driver.find_elements(By.CLASS_NAME, 'OrderSummary-line-extension')[3]
        if config['Site_Selection']['zip_code'] not in zip_label.text:
            change_zip_link = driver.find_elements(By.XPATH, Walmart.change_zip_button)
            change_zip_link[2].click()
            self.enter_text(By.XPATH, Walmart.change_zip_input, config['Site_Selection']['zip_code'])
            zip_calculate_button = driver.find_element(By.XPATH, Walmart.change_zip_save_button)
            zip_calculate_button.click()
            self.wait_for_element_to_appear(By.CLASS_NAME, 'spinner')
            time.sleep(11)

        # Collect & Assert
        product_price = driver.find_element_by_xpath("//div[@id='cart-root-container-content-skip']/div/div/div/"
                                                     "div/div/div[3]/div/div/div/div/div/div/div/div[3]/div/div/"
                                                     "div[2]/div/div/span[2]/span").text
        product_price = product_price.replace('each', '').replace(' ', '')
        sub_total = driver.find_element_by_xpath(Walmart.sub_total_value).text
        shipping_cost = driver.find_element_by_xpath(Walmart.shipping_cost_value).text
        tax = driver.find_element_by_xpath(Walmart.tax_value).text
        total_cost = driver.find_element_by_xpath(Walmart.total_value).text
        print('\n\nProduct: {}'.format(product_price),
              '\nCan Purchase: {}'.format(can_purchase),
              '\nSubTotal: {}'.format(sub_total),
              '\nShipping: {}'.format(shipping_cost),
              '\nTax: {}'.format(tax),
              '\n----------------------',
              '\nTotal: {}'.format(total_cost))

        # Checkout
        checkout_button = driver.find_elements(By.XPATH, Walmart.checkout_button)[2]
        checkout_button.click()
        self.wait_for_page_load()
        time.sleep(4)
        for i in range(60):
            try:
                if "Shipping and pickup options" == driver.find_element_by_css_selector(
                        "span.CXO_module_heading_heading-text > span").text: break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_xpath("(//button[@type='button'])[2]").click()
        self.wait_for_page_load(custom_timeout)
        self.wait_for_page_load(custom_timeout)
        for i in range(60):
            try:
                if "Add new address" == driver.find_element_by_css_selector("h3 > button.btn-fake-link").text: break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        time.sleep(2)
        driver.find_element_by_xpath("(//button[@type='button'])[8]").click()
        self.wait_for_page_load(custom_timeout)
        time.sleep(9)
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR,
                                           "div.CXO_module_header_right > div > "
                                           "h1.CXO_module_heading_container > "
                                           "span.CXO_module_heading_heading-text > span"): break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")

        # Payment Method
        # TODO: Require a wait for some payment method to appear
        driver.find_element_by_xpath("(//button[@type='button'])[9]").click()

        # Place Order
        self.wait_for_page_load(custom_timeout)
        for i in range(60):
            try:
                if "Please review and" == driver.find_element_by_xpath("//form/div/div/span").text: break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")

        # Submit Order
        if allow_purchase == 'true':
            driver.find_element_by_xpath("(//button[@type='submit'])[2]").click()
            self.wait_for_page_load(custom_timeout)
            tracking_number = driver.find_element(By.CLASS_NAME, 'thank-you-order-id font-normal').text
            order_tracking_number = driver.find_element(By.CLASS_NAME, 'thankyou-order-id').text
            delivery_date = driver.find_element(By.CLASS_NAME, 'thankyou-delivery-date').text
            ship_to_address = self.is_element_present(By.XPATH, "//div/span[2]")
            # Update DB
            new_spent_value = product_price + spending_spent
            sql_cmd = 'insert into shopsnipepy_schema.purchases (' \
                      'transation_id, price, store) ' \
                      'values (\'{0}\', {1}, \'WalMart\')' \
                .format(order_tracking_number, product_price, 'walmart')
            sql_wallet_update = 'update shopsnipepy_schema.wallet ' \
                                'set Spent = \'{0}\'' \
                                'where willing_to_spend = \'{1}\''.format(new_spent_value, '269')
            self.call_db_insert(query=sql_cmd)
            self.call_db_insert(query=sql_wallet_update)

    def test_bestbuy(self):
        config = configparser.ConfigParser()
        config.read(cwd_dir + '/config.ini')
        now = datetime.datetime.now()
        current_run_time = now.isoformat().replace('T', ' ')
        print('\nRunning BestBuy\nCurrent RunTime - {}'.format(current_run_time))

        driver = self.driver
        custom_timeout = 90

        # Check if purchase is allowed & spending limit allows for purchase
        allow_purchase = config['Site_Selection']['allow_purchase']
        spending_spent = self.call_db_select(query='select spent from shopsnipepy_schema.wallet')
        spending_limit = self.call_db_select(query='select willing_to_spend from shopsnipepy_schema.wallet')
        spending_spent = Decimal(spending_spent)
        spending_limit = Decimal(spending_limit)
        print('Spending Allow: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
        if spending_spent == spending_limit:
            print('Spending limit: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
            driver.close()
            driver.quit()
        elif spending_spent > spending_limit:
            print('Spending limit: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
            driver.close()
            driver.quit()

        # Navigate
        driver.get(url=config['BestBuy']['bestbuy_producturl'])
        self.wait_for_page_load(timeout=custom_timeout)
        time.sleep(4)

        # Delegate Logging in if not already
        self.wait_for_text_appear(how=By.ID, what=_bbo.account_status_label, target_text='Account')
        sold_out = self.is_element_present(By.XPATH, "//button[contains(.,'Sold Out')]")
        if sold_out == True:
            print('Sold out yo')
            driver.quit()
        account_login_status = driver.find_element_by_id(_bbo.account_status_label).text
        if account_login_status == 'Account':
            driver.find_element_by_id("profileMenuWrap1").click()
            self.wait_for_text_appear(how=By.CSS_SELECTOR, what=_bbo.account_log_in_link, target_text='Sign In')
            driver.find_element(By.CSS_SELECTOR, _bbo.account_log_in_link).click()
            self.wait_for_text_appear(how=By.CSS_SELECTOR, what=_bbo.login_welcome_message,
                                      target_text='Sign In to BestBuy.com')
            self.enter_text(how=By.ID, what=_bbo.login_email_input, text=config['BestBuy']['bestbuy_username'])
            self.enter_text(how=By.ID, what=_bbo.login_password_input, text=config['BestBuy']['bestbuy_password'])
            driver.find_element(By.CSS_SELECTOR, _bbo.login_submit_button).click()
            self.wait_for_page_load(timeout=custom_timeout)
            self.wait_for_page_load(timeout=custom_timeout)
            time.sleep(11)

        # Collect Info & Add to Cart
        try:
            elem = driver.find_element(By.XPATH, "//button[contains(.,'Coming Soon')]")
            if elem.is_displayed():
                driver.quit()
        except NoSuchElementException:
            print("element was not found\nElement:{}".format(elem.text))
        product_name = driver.find_element_by_css_selector(_bbo.product_name_label).text
        product_sku = driver.find_element_by_id(_bbo.product_sku_label).text
        product_price = driver.find_element_by_css_selector(_bbo.product_price_label).text
        print('Product: {0}\nSku: {1}\nPrice: {2}\n'.
              format(product_name, product_sku, product_price))
        product_price = Decimal(product_price.strip('$'))
        driver.find_element_by_xpath(_bbo.product_add_to_cart_button).click()
        self.wait_for_page_load(timeout=custom_timeout)
        time.sleep(13)

        # Delegate if there is a suggestion popup after add to cart
        # self.wait_for_element_to_appear(By.LINK_TEXT, _bbo.popup_no_thanks_button)
        # try:
        #     self.assertTrue(self.is_element_present(By.LINK_TEXT, _bbo.popup_no_thanks_button))
        #     driver.find_element_by_link_text(_bbo.popup_no_thanks_button).click()
        # except AssertionError as e:
        #     self.verificationErrors.append(str(e))

        # Review Cart
        self.wait_for_text_appear(how=By.CLASS_NAME, what=_bbo.review_product_total_label,
                                  target_text='Product Total')
        time.sleep(4)

        # - Quantity
        qty_dropdown = Select(driver.find_element_by_css_selector(_bbo.review_quantity_dropdown))
        item_quantity_amount = qty_dropdown.first_selected_option.text
        qty_options = qty_dropdown.all_selected_options
        qty_dropdown.select_by_index(1)
        print('Purchase Quantity: {}\nCan Purchase: {}'.format(item_quantity_amount, qty_options))

        # - Shipping or Pick up
        found_radio_buttons = len(driver.find_elements(By.XPATH, _bbo.review_radio_button_li))
        if found_radio_buttons == 2:
            time.sleep(2)
            driver.find_element(By.ID, _bbo.review_radio_button_2).click()
            time.sleep(4)
        try:
            cart_shipping_to_label = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div/div/span/'
                                                                   'div/' \
                                                                   'div[3]/div/div[2]/div/div/div/div[1]/div[2]/' \
                                                                   'form/ul/li[2]/label/strong').text
        except Exception:
            cart_shipping_to_label = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div/div/'
                                                                   'span/div/div[3]/div/div[2]/div/div/div/div[1]/'
                                                                   'div[2]/form//*/span[contains(.,\'Update\')]').text
        if config['Site_Selection']['zip_code'] not in cart_shipping_to_label:
            driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[1]/div/div/'
                                         'span/div/div[3]/div/div[2]/div/div/div/div[1]/'
                                         'div[2]/form//*/'
                                         'span[contains(.,\'Update\')]').click()
            time.sleep(1)
            self.enter_text(how=By.ID, what=_bbo.review_change_zip_input, text='80229')
            driver.find_element_by_css_selector(_bbo.review_change_zip_button).click()
            self.wait_for_element_present(how=By.CSS_SELECTOR, what=_bbo.loading_spinner)
            driver.find_element_by_css_selector(_bbo.review_change_zip_close).click()
            time.sleep(9)
        try:
            self.assertTrue(self.is_element_present(By.CSS_SELECTOR, "div.listing-footer__pricing-value"))
        except AssertionError as e:
            self.verificationErrors.append(str(e))
        time.sleep(2)
        driver.find_element_by_xpath(_bbo.review_checkout_button).click()
        self.wait_for_element_present(how=By.CSS_SELECTOR, what=_bbo.next_page_spinner)
        self.wait_for_page_load()
        self.wait_for_page_load()

        # Delivery Settings
        driver.find_element(By.XPATH, _bbo.cart_checkout_button).click()
        self.wait_for_element_present(By.CSS_SELECTOR, _bbo.next_page_spinner)
        self.wait_for_page_load()
        time.sleep(7)
        self.wait_for_element_present(By.XPATH, _bbo.shipping_continue_button)
        driver.find_element(By.XPATH, _bbo.shipping_continue_button).click()
        self.wait_for_page_load()
        self.wait_for_page_load()

        # PayPal
        time.sleep(7)
        current_window = driver.current_window_handle
        checkout_paypal = self.is_element_present(By.XPATH, "//div[@id='app']/div/div/div[2]/div[3]/div/section/"
                                                            "div/div[2]/label/strong")
        print('Paypal: {}'.format(checkout_paypal))
        driver.find_element(By.XPATH, "//div[@id='app']/div/div/div[2]/div[3]/div/section/"
                                      "div/div[2]/label/strong").click()
        time.sleep(12)
        driver.find_element_by_xpath('//*/button[contains(.,\'PayPal\')]').click()
        windows_found = driver.window_handles
        driver.switch_to.window(windows_found[1])
        paypal_title = driver.title
        print('Paypal title: {}'.format(paypal_title))
        time.sleep(14)
        self.wait_for_element_present(how=By.XPATH, what='//*/a[contains(.,\'Log In\')]')
        for i in range(60):
            try:
                if "Log In" == driver.find_element_by_link_text("Log In").text: break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_link_text("Log In").click()
        time.sleep(9)
        self.wait_for_page_load(custom_timeout)
        self.wait_for_element_to_appear(By.ID, _ppo.login_email_input)
        self.enter_text(By.ID, _ppo.login_email_input, config['PayPal']['pp_username'])
        driver.find_element(By.ID, 'btnNext').click()
        self.wait_for_page_load(custom_timeout)
        self.enter_text(By.ID, _ppo.login_password_input, config['PayPal']['pp_password'])
        driver.find_element_by_id("btnLogin").click()
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "div.lockIcon"): break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        for i in range(60):
            try:
                if self.is_element_present(By.ID, "spinnerMessage"): break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        self.wait_for_page_load()
        self.wait_for_page_load()
        time.sleep(13)
        driver.find_element_by_id("confirmButtonTop").click()
        self.wait_for_page_load()
        time.sleep(13)
        driver.switch_to_window(current_window)
        curret_window_title = driver.title
        print('Current Window: {}'.format(curret_window_title))

        # PayPal Place order
        if allow_purchase == 'true':
            driver.find_element(By.XPATH, '//*/button[contains(.,\'Place\')]').click()
            self.wait_for_page_load()

            # Order confirmation
            for i in range(60):
                try:
                    if "Thank you for your order" == driver.find_element_by_css_selector("p.i18n-paragraph").text: break
                except:
                    pass
                time.sleep(1)
            else:
                self.fail("time out")
            best_buy_order_number = driver.find_element_by_xpath("//div[@id='app']/"
                                                                 "div/div/div/div[2]/section/div[2]/div[2]").text
            best_buy_order_number = best_buy_order_number.strip('Order Number: ')

            # Update DB
            new_spent_value = product_price + spending_spent
            sql_cmd = 'insert into shopsnipepy_schema.purchases (' \
                      'transation_id, price, store) ' \
                      'values (\'{0}\', {1}, \'Best Buy\')' \
                .format(best_buy_order_number, product_price, 'best buy')
            sql_wallet_update = 'update shopsnipepy_schema.wallet ' \
                                'set Spent = \'{0}\'' \
                                'where willing_to_spend = \'{1}\''.format(new_spent_value, '269')
            self.call_db_insert(query=sql_cmd)
            self.call_db_insert(query=sql_wallet_update)

        else:
            print('Allow purchase: {}'.format(allow_purchase))
            driver.close()

    def test_toys_r_us(self):
        config = configparser.ConfigParser()
        config.read(cwd_dir + '/config.ini')
        now = datetime.datetime.now()
        current_run_time = now.isoformat().replace('T', ' ')
        print('\nRunning Toys R Us\nCurrent RunTime - {}'.format(current_run_time))

        driver = self.driver
        custom_timeout = 900

        # Check if purchase is allowed & spending limit allows for purchase
        allow_purchase = config['Site_Selection']['allow_purchase']
        spending_spent = self.call_db_select(query='select spent from shopsnipepy_schema.wallet')
        spending_limit = self.call_db_select(query='select willing_to_spend from shopsnipepy_schema.wallet')
        spending_spent = Decimal(spending_spent)
        spending_limit = Decimal(spending_limit)
        print('Spending Allow: {0}\nSpent: {1}'.format(spending_limit, spending_spent))

        while spending_spent < spending_limit:
            if spending_spent == spending_limit:
                print('Spending limit: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
                driver.close()
                driver.quit()
            elif spending_spent > spending_limit:
                print('Spending limit: {0}\nSpent: {1}'.format(spending_limit, spending_spent))
                driver.close()
                driver.quit()

            # Navigate
            driver.get(config['ToysRUs']['toysrus_producturl'])
            self.wait_for_page_load(custom_timeout)
            driver.get(config['ToysRUs']['toysrus_producturl'])
            self.wait_for_page_load(custom_timeout)

            # -- Assert Has item
            add_to_cart_button = driver.find_element(By.XPATH, _truo.item_add_to_cart_button)
            try:
                self.assertEqual("add to cart", add_to_cart_button.text)
            except AssertionError as e:
                print(
                    '\n----------\nAdd to Cart Button did not exists.\nButton > {}'.format(add_to_cart_button.text))
                self.verificationErrors.append(str(e))

            self.wait_for_page_load(custom_timeout)
            self.wait_for_element_to_appear(By.CLASS_NAME, 'head_welcome_cont', custom_timeout)
            # for i in range(custom_timeout):
            #     try:
            #         if "my account" == driver.find_element_by_id("VisitorFirstNamecookieDIV").text: break
            #     except:
            #         pass
            #     time.sleep(1)
            # else:
            #     self.fail("time out")
            self.wait_for_text_appear(By.ID, 'VisitorFirstNamecookieDIV', 'my account', custom_timeout)
            time.sleep(1)
            r_icon = driver.find_element(By.CLASS_NAME, 'head_welcome_cont')
            actions = ActionChains(driver)
            actions.move_to_element(r_icon).click().perform()

            # -- Login
            self.wait_for_element_to_appear(By.LINK_TEXT, 'sign in', custom_timeout)
            driver.find_element_by_link_text("sign in").click()
            self.wait_for_element_to_appear(By.ID, _truo.login_button)
            self.wait_for_element_to_appear(By.ID, _truo.login_username_input)
            time.sleep(2)
            self.enter_text(By.ID, _truo.login_username_input, config['ToysRUs']['toysrus_username'])
            self.enter_text(By.ID, _truo.login_password_input, config['ToysRUs']['toysrus_password'])
            time.sleep(3)
            login_submit = driver.find_element(By.ID, _truo.login_submit_button)
            login_submit.click()
            error_found = self.is_element_present(By.CSS_SELECTOR, _truo.login_error_message)
            if error_found:
                print('Login Error Found >\nMessage: {}'.format(
                    driver.find_element(By.CSS_SELECTOR, _truo.login_error_message).text))
            self.wait_for_page_load(custom_timeout)
            self.wait_for_page_load(custom_timeout)
            time.sleep(6)
            self.wait_for_text_appear(By.ID, 'VisitorFirstNamecookieDIV', 'welcome, ', custom_timeout)
            self.wait_for_element_to_appear(By.ID, _truo.login_status, custom_timeout)
            login_status = driver.find_element(By.ID, _truo.login_status).text
            try:
                self.assertEqual("welcome, ", login_status)
            except AssertionError as e:
                self.verificationErrors.append(str(e))

            # -- Add to Cart
            # ERROR: Caught exception [ERROR: Unsupported command [selectWindow | null | ]]
            product_price = driver.find_element_by_css_selector("span.price").text
            print('Product Price: {}'.format(product_price))
            add_to_cart_button = driver.find_element(By.XPATH, _truo.item_add_to_cart_button)
            try:
                self.assertEqual("add to cart", add_to_cart_button.text)
            except AssertionError as e:
                print('Add to Cart Button did not exists.\nButton > {}'.format(add_to_cart_button.text))
                self.verificationErrors.append(str(e))
                driver.close()
                driver.quit()
            add_to_cart_button.click()
            for i in range(custom_timeout):
                try:
                    if self.is_element_present(By.XPATH, _truo.item_check_out_button): break
                except:
                    pass
                time.sleep(1)
            else:
                self.fail("time out")
            time.sleep(2)
            item_qty = driver.find_element(By.XPATH, "//input[@class='counter center lineItemQty']"). \
                get_attribute('value')
            while item_qty != '1':
                if item_qty == '1':
                    break;
                driver.find_element(By.XPATH, "//a[@class='decrease enabled cart']").click()
                for i in range(custom_timeout):
                    try:
                        if self.is_element_present(By.ID, _truo.item_check_out_loader): break
                    except:
                        pass
                    time.sleep(1)
                else:
                    self.fail("time out")
                time.sleep(1)
                item_qty = driver.find_element(By.XPATH, "//input[@class='counter center lineItemQty']"). \
                    get_attribute('value')
                if item_qty == '1':
                    break;
            time.sleep(4)
            current_sub_total = driver.find_element(By.XPATH, "//span[@class='line-item-value']").text
            while current_sub_total != product_price:
                if current_sub_total == product_price:
                    break
                time.sleep(10)
                current_sub_total = driver.find_element(By.XPATH, "//span[@class='line-item-value']").text
            driver.find_element(By.XPATH, "//span[contains(@class,'x-image')]").click()
            time.sleep(4)
            self.wait_for_page_load(custom_timeout)

            # -- checkout
            driver.find_element(By.XPATH, "//span[@class='sprite sprite-cart-icon']").click()
            for i in range(custom_timeout):
                try:
                    if self.is_element_present(By.XPATH, _truo.checkout_paypal_button): break
                except:
                    pass
                time.sleep(1)
            else:
                self.fail("time out")
            sub_total = driver.find_element_by_css_selector("span.order-summary-item-value").text
            shipping = driver.find_element_by_css_selector(
                "div.estimatedShipping > span.order-summary-item-value").text
            total_value = driver.find_element_by_css_selector(
                "div.order-summary-total-container > span.order-summary-item-value").text
            print('\nSub total: {0}\nShipping: {1}\nTotal: {2}'.format(sub_total, shipping, total_value))
            product_price = total_value
            current_window = driver.current_window_handle

            # PAYPAL
            time.sleep(7)
            self.wait_for_element_to_appear(By.XPATH, "//div[@onclick='initializePaypal()']", custom_timeout)
            driver.find_element_by_xpath("//div[@onclick='initializePaypal()']").click()
            time.sleep(16)
            windows_found = driver.window_handles
            driver.switch_to.window(windows_found[1])
            paypal_title = driver.title
            print('Paypal title: {}'.format(paypal_title))
            time.sleep(14)
            self.wait_for_element_present(how=By.XPATH, what='//*/a[contains(.,\'Log In\')]')
            for i in range(60):
                try:
                    if "Log In" == driver.find_element_by_link_text("Log In").text: break
                except:
                    pass
                time.sleep(1)
            else:
                self.fail("time out")
            driver.find_element_by_link_text("Log In").click()
            time.sleep(9)
            self.enter_text(By.ID, _ppo.login_email_input, config['PayPal']['pp_username'])
            driver.find_element(By.ID, 'btnNext').click()
            self.wait_for_page_load(custom_timeout)
            self.enter_text(By.ID, _ppo.login_password_input, config['PayPal']['pp_password'])
            driver.find_element_by_id("btnLogin").click()
            for i in range(60):
                try:
                    if self.is_element_present(By.CSS_SELECTOR, "div.lockIcon"): break
                except:
                    pass
                time.sleep(1)
            else:
                self.fail("time out")
            for i in range(60):
                try:
                    if self.is_element_present(By.ID, "spinnerMessage"): break
                except:
                    pass
                time.sleep(1)
            else:
                self.fail("time out")
            self.wait_for_page_load()
            self.wait_for_page_load()
            time.sleep(13)
            driver.find_element_by_id("confirmButtonTop").click()
            self.wait_for_page_load()
            time.sleep(13)
            driver.switch_to_window(current_window)
            curret_window_title = driver.title
            print('Current Window: {}'.format(curret_window_title))

            # PayPal Place order
            if allow_purchase == 'true':
                driver.find_element(By.XPATH, _truo.submit_checkout_button).click()
                self.wait_for_page_load()

                # driver.find_element_by_id("expressCheckoutWithPayPalSubmitBtn").click()
                for i in range(60):
                    try:
                        if self.is_element_present(By.CSS_SELECTOR, "img[alt=\"Processing...\"]"): break
                    except:
                        pass
                    time.sleep(1)
                else:
                    self.fail("time out")
                self.wait_for_page_load(custom_timeout)

                # Order confirmation
                time.sleep(16)
                self.wait_for_text_appear(By.CSS_SELECTOR, 'h1.checkout-order-complete-header__title',
                                          'your order is complete', custom_timeout)
                toys_r_us_order_number = driver.find_element_by_css_selector(
                    "span.checkout-order-complete-header__subheader--bold").text
                product_price = product_price.strip('$')

                # Update DB
                new_spent_value = product_price + spending_spent
                sql_cmd = 'insert into shopsnipepy_schema.purchases (' \
                          'transation_id, price, store) ' \
                          'values ({0}, {1}, \'Best Buy\')' \
                    .format(toys_r_us_order_number, product_price, 'toys r us')
                sql_wallet_update = 'update shopsnipepy_schema.wallet ' \
                                    'set Spent = \'{0}\'' \
                                    'where willing_to_spend = \'{1}\''.format(new_spent_value, '269')
                self.call_db_insert(query=sql_cmd)
                self.call_db_insert(query=sql_wallet_update)
                if new_spent_value > spending_limit:
                    break;
            else:
                print('Allow purchase: {}'.format(allow_purchase))
                driver.close()

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == '__main__':
    unittest.main()
