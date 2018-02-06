import sys
import os
import configparser
import pymysql


from time import sleep

cwd_dir = os.path.dirname(os.path.realpath(__file__))
spending_limit = 0

def main_menu():

    loop = True

    while loop:
        print(27 * "-", " Main Menu", 28 * "-")
        print("1) Select Sites")
        print("2) Setup Credentials & Product")
        print("3) Setup Database")
        print("4) Schedule Run Times")
        print("5) Quit")
        print(67 * "-")

        choice = input("Please select setup option [1-3]: ")

        if choice == '1':
            site_selection()
            break
        elif choice == '2':
            credential_product_setup()
            break
        elif choice == '3':
            database_setup()
            break
        elif choice == '4':
            print('Not setup')
            main_menu()
        elif choice == '5':
            sys.exit("Exiting. . .")
        else:
            print("Improper Input. . .")


def site_selection():
    print(30 * "-", "Available Sites", 20 * "-")
    print("0) All")
    print("1) Walmart")
    print("2) BestBuy")
    print("3) Target")
    print("4) Game Stop")
    print("5) Toys R Us")
    print(67 * "-")

    site_selection_loop = True
    current_sites_tmp = []
    config = configparser.ConfigParser()
    config_location = cwd_dir + '/config.ini'
    config.read(config_location)
    current_sites = config['Site_Selection']['target_sites']
    print("\nCurrent Selected Sites: %s" % current_sites)

    while site_selection_loop:
        site_selection_choice = input("Please select setup option [1-5] or [apply | reset | exit]: ")
        added_already_message = "Site is already added"
        print("\nSelected: %s" % current_sites_tmp)

        if site_selection_choice == '0':
            if 'all' not in current_sites_tmp:
                current_sites_tmp.clear()
                current_sites_tmp.append('all')
            else:
                print(added_already_message)
        elif site_selection_choice == '1':
            if 'Walmart' not in current_sites_tmp:
                current_sites_tmp.append('Walmart')
            else:
                print(added_already_message)
        elif site_selection_choice == '2':
            if 'BestBuy' not in current_sites_tmp:
                current_sites_tmp.append('BestBuy')
            else:
                print(added_already_message)
        elif site_selection_choice == '3':
            if 'Target' not in current_sites_tmp:
                current_sites_tmp.append('Target')
            else:
                print(added_already_message)
        elif site_selection_choice == '4':
            if 'GameStop' not in current_sites_tmp:
                current_sites_tmp.append('GameStop')
            else:
                print(added_already_message)
        elif site_selection_choice == '5':
            if 'ToysRUs' not in current_sites_tmp:
                current_sites_tmp.append('ToysRUs')
            else:
                print(added_already_message)
        elif site_selection_choice == 'reset':
            current_sites_tmp.clear()
        elif site_selection_choice == 'apply':
            current_sites = config['Site_Selection']['target_sites'] = ",".join(current_sites_tmp)
            config.set('Site_Selection', 'target_sites', current_sites)
            with open(config_location, 'w') as configfile:
                config.write(configfile)
            print("\nCurrent Selected Sites Applied: %s" % current_sites)
        elif site_selection_choice == 'exit':
            main_menu()


def credential_write(site):
    config = configparser.ConfigParser()
    config_location = cwd_dir + '/config.ini'
    config.read(config_location)

    cred_username = input("Please Enter Username for %s: " % site)
    cred_password = input("Please Enter Password for %s: " % site)
    cred_url = input("Please Enter Url of Product for %s (leave blank if using isbn): " % site)
    cred_isbn = input("Please Enter ISBN of Product for %s (leave blank if using url): " % site)

    config.set(site, site.lower()+'_username', cred_username)
    config.set(site, site.lower()+'_password', cred_password)
    if cred_url:
        config.set(site, site.lower()+'_producturl', cred_url)
    if cred_isbn:
        config.set(site, site.lower() + '_productisbn', cred_isbn)

    with open(config_location, 'w') as configfile:
        config.write(configfile)


def credential_product_setup():
    print('\nChecking your selected sites. . .')
    config = configparser.ConfigParser()
    config.read(cwd_dir + '/config.ini')
    current_sites = config['Site_Selection']['target_sites']
    if 'none' in current_sites:
        print('\nNo Sites have been selected, please select the sites you want to use\n')
        sleep(1.6)
        main_menu()
    else:
        print('scanning')
        current_sites = current_sites.split(',')
        for i in list(current_sites):
            credential_write(i)


def db_exists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False


def database_test_settings(host, port, username, password, spend_limit):
    # We needs to see if the Database or 2 tables for this project exists, if they do not
    # a unique error code is generated pending on what the query error will be, from this
    # the script knows what it needs to create in order to get everything setup properly
    print('\nTesting Settings. . .\nSpending Limit: %s' % spend_limit)
    try:
        db_conn = pymysql.connect(host=host, port=int(port),
                                  user=username, passwd=password,
                                  db='shopsnipepy_schema')
        try:
            # Test Wallet Table
            db_table_type = 'wallet'
            wallet_check = 'select willing_to_spend from shopsnipepy_schema.wallet;'
            with db_conn.cursor() as cursor:
                cursor.execute(wallet_check)
            db_conn.commit()

            # Test Transaction Table
            db_table_type = 'transaction'
            transactions_check = 'select transation_id from shopsnipepy_schema.purchases;'
            with db_conn.cursor() as cursor:
                cursor.execute(transactions_check)
            db_conn.commit()
        finally:
            db_conn.close()
    except Exception as e:
        print('\nConnection has failed.\nError Code: %s;\nError Content: %s;' % (e.args[0], e.args[1]))
        if e.args[0] == 1049:
            # Database does not exist, we need to create it
            database_generate(host=host, username=username, passwd=password)
        elif e.args[0] == 1146:
            # Database tables were not found, we need to create them
            db_create_tables(host, port, username, password, db_table_type)
        else:
            print('\nUnhandled exception, please email author on github for future patching')
    main_menu()


def db_create_tables(host, port, username, password, table_type):
    db_conn = pymysql.connect(host=host, port=int(port),
                                  user=username, passwd=password,
                                  db='shopsnipepy_schema')
    try:
        with db_conn.cursor() as cursor:
            if table_type == 'wallet':
                # Create the wallet table
                sql = "CREATE TABLE `wallet`(`id` int(11) NOT NULL AUTO_INCREMENT," \
                      "`willing_to_spend` int(100) COLLATE utf8_bin NOT NULL," \
                      "`spent` int(100) COLLATE utf8_bin NOT NULL," \
                      "PRIMARY KEY (`id`))" \
                      "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;"
            elif table_type == 'transaction':
                sql = "CREATE TABLE `purchases`(`id` int(11) NOT NULL AUTO_INCREMENT," \
                      "`transation_id` varchar(255) COLLATE utf8_bin NOT NULL," \
                      "`price` int(100) COLLATE utf8_bin NOT NULL," \
                      "`store` varchar(255) COLLATE utf8_bin NOT NULL," \
                      "PRIMARY KEY (`id`))" \
                      "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;"
            # Create the transaction table
            cursor.execute(sql)
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        db_conn.commit()
    finally:
        db_conn.close()
    database_test_settings(host=host, port=port, username=username, password=password, spend_limit=spending_limit)


def database_generate(host, username, passwd):
    config = configparser.ConfigParser()
    config_location = cwd_dir + '/config.ini'
    config.read(config_location)

    # If the Database does not exist, we need to create it
    try:
        db_conn = pymysql.connect(host=host, user=username, passwd=passwd)
        db_curse = db_conn.cursor()
        db_curse.execute('CREATE DATABASE shopsnipepy_schema')
        db_conn.close()
        config = config['Database']['db_port']
        database_test_settings(host=host, port=config, username=username, password=passwd, spend_limit=spending_limit)
    except Exception as e:
        print('\nFailed to create Database, be sure mysql is running and credentials are proper!')
        print('\nError Code: %s;\nError Content: %s;' % (e.args[0], e.args[1]))
        main_menu()


def database_setup():
    print('\nIf you are not sure how to set this part up - please leave this portion alone.')
    config = configparser.ConfigParser()
    config_location = cwd_dir + '/config.ini'
    config.read(config_location)
    db_list = list(config.items('Database'))
    print('\nCurrent Configuration:')
    print(*db_list, sep='\n')

    edit_db_settings = True
    while edit_db_settings:
        edit_current_db_settings = input('Edit Current Settings? [Y/N or Exit]: ')
        if edit_current_db_settings.lower() == 'y' or edit_current_db_settings.lower() == 'yes':
            print('\nPlease be sure to add a user with CRUD permissions')
            db_host = input("\nPlease Enter Host: ")
            db_port = input("\nPlease Enter Port: ")
            db_username = input("\nPlease Enter Username: ")
            db_password = input("\nPlease Enter Password: ")
            db_willing_to_spend = input('\nEnter Amount willing to Spend (No Need to Supply Currency symbol): ')
            config.set('Database', 'db_host', db_host)
            config.set('Database', 'db_port', db_port)
            config.set('Database', 'db_username', db_username)
            config.set('Database', 'db_password', db_password)
            config.set('Database', 'db_willing_to_spend', db_password)
            with open(config_location, 'w') as configfile:
                config.write(configfile)
            database_setup()
        elif edit_current_db_settings.lower() == 'n' or edit_current_db_settings.lower() == 'no':
            db_host = config['Database']['db_host']
            db_port = config['Database']['db_port']
            db_username = config['Database']['db_username']
            db_password = config['Database']['db_password']
            db_willing_to_spend = config['Database']['db_willing_to_spend']
            database_test_settings(db_host, db_port, db_username, db_password, db_willing_to_spend)
        elif edit_current_db_settings.lower() == 'exit':
            main_menu()
        else:
            print('\nCurrent Configuration:')
            print(*db_list, sep='\n')
            database_test_settings(db_host, db_port, db_username, db_password, db_willing_to_spend)
            main_menu()

    main_menu()


main_menu()
