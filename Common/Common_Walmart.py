class WalmartObjects:
    login_status_label = '/html/body/div/div/div/div/header/div/div[2]/div/div/div/div/div/div[6]/div/div/div/div[1]'
    sign_in_box = 'SignIn clearfix'
    email_address_input = 'email'
    password_input = 'password'
    keep_signed_in_checkbox = 'checkbox-0'
    sign_in_button = 'button.btn.btn-block'
    tracking_truck_icon = 'elc-icon elc-icon-truck'
    quantity_dropdown = 'select-field'
    quantity_dropdown_selection = '/html/body/div[1]/div/div/div/div/div[1]/div/div/' \
                                  'div[2]/div/div[2]/div[2]/div[2]/div[1]/div[1]/' \
                                  'div/div[9]/div[1]/div[2]/div[1]/span/span[2]/' \
                                  'div/select/option'
    add_to_cart_button = '/html/body/div[1]/div/div/div/div/div[1]/div/div/div[2]/div/' \
                         'div[2]/div[2]/div[2]/div[1]/div[1]/div/div[9]/div[1]/' \
                         'div[2]/div[2]/div/button'
    item_added_popup_model = 'modal_layout_container'
    you_just_added_label = '/html/body/div[2]/div/div[1]/div/div[2]/' \
                           'div/div/div[2]/div/div/div/div[1]/div/div[1]/div[2]/h3/span'
    estimated_total = '/html/body/div[2]/div/div[1]/div/div[2]/div/div/div[2]/' \
                      'div/div/div/div[2]/div/div/div/div[1]/div/div[4]/span[2]/span'
    checkout_button = '//*/div//*/button[contains(.,\'Check Out\')]'
    checkout_shipping_choice = '/html/body/div/div/div[1]/div/div[3]/div/' \
                               'div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div[1]/div[1]/div'
    checkout_free_pickup = '/html/body/div/div/div[1]/div/div[3]/div/' \
                           'div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div[1]/div[2]/div'
    change_zip_button = '//*/div//*/button[contains(.,\'Change\')]'
    change_zip_input = '/html/body/div/div/div[1]/div/div/div/div[1]/div[2]/' \
                       'div/div/div[1]/div/div[3]/div/div/div/div/div[1]/' \
                       'div/div/form/label/div/input'
    change_zip_save_button = '/html/body/div/div/div[1]/div/div/div/div[1]/' \
                             'div[2]/div/div/div[1]/div/div[3]/div/div/' \
                             'div/div/div[1]/div/div/form/div/div[1]/button'
    checkout_shipping_continue_button = '/html/body/div/div/div[1]/div/div[3]/div/div/' \
                                        'div/div[2]/div[2]/div/div/div/div/div/div/div[3]/button'
    checkout_shipping_first_name_input = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[3]/div[1]/' \
                                         'div[2]/div/div/div/div/div/div/div/div/div/form/div/div/div/' \
                                         'div[1]/label[1]/div/input'
    checkout_shipping_address_input = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[3]/div[1]/div[2]/' \
                                      'div/div/div/div/div/div/div/div/div/form/' \
                                      'div/div/div/div[2]/label[1]/div/input'
    checkout_shipping_last_name_input = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[3]/div[1]/' \
                                        'div[2]/div/div/div/div/div/div/div/div/div/' \
                                        'form/div/div/div/div[1]/label[2]/div/input'
    checkout_shipping_phone_input = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[3]/div[1]/' \
                                    'div[2]/div/div/div/div/div/div/div/div/div/form/div/div/div/div[1]/' \
                                    'label[3]/div/input'
    checkout_shipping_state_input = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[3]/' \
                                    'div[1]/div[2]/div/div/div/div/div/div/div/div/div/form/div/div/' \
                                    'div/div[2]/label[3]/div/input'
    checkout_shipping_zip_input = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[3]/div[1]/div[2]/div/' \
                                  'div/div/div/div/div/div/div/div/form/div/div/div/div[2]/' \
                                  'div/div[2]/label/div/input'
    checkout_shipping_continue_button = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[3]/div[1]/' \
                                        'div[2]/div/div/div/div/div/div/div/div/div/div/div[2]/button'
    checkout_step_two_label = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[3]/div[1]/div[1]/div/' \
                              'div/div/div/div/div[2]/div/h1/span/span'
    checkout_shipping_selected_address = 'address-tile-clickable'
    checkout_step_three_label = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[4]/div[1]/div[1]/' \
                                'div/div/div/div/div/div[2]/div/h1/span/span'
    checkout_payment_type_more = 'payment-option-radio-2'
    checkout_payment_type_paypal = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[4]/div[1]/div[2]/' \
                                   'div/div/div/div/div/div/div[2]/div[1]/div[1]/div/img'
    checkout_review_order_button = '/html/body/div/div/div[1]/div/div[3]/div/div/div/div[4]/div[1]/div[2]/div/' \
                                   'div/div/div/div/div/div[2]/div/div[2]/div/div/div/form/div[2]/div/button'
    sub_total_value = "//div[@id='cart-root-container-content-skip']/div/div/div/div[2]/div/div/div/div/div/span[2]"
    shipping_cost_value = "//div[@id='cart-root-container-content-skip']/div/div/div/div[2]/div/div/div/div/div[2]/" \
                          "span[2]"
    tax_value = "//div[@id='cart-root-container-content-skip']/div/div/div/div[2]/div/div/div/div/div[3]/span[2]"
    total_value = "//div[@id='cart-root-container-content-skip']/div/div/div/div[2]/div/div/div/div/div[4]/span[2]"
