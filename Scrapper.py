import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import mysql.connector

# Function to handle location and privacy popups
def handle_popups():
    try:
        # Handle location popup ("Never Allow" button)
        location_popup = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Never Allow')]"))
        )
        location_popup.click()
        print("Location popup handled: 'Never Allow' clicked.")
    except Exception as e:
        print("No location popup found or error occurred.")

    try:
        # Handle privacy popup (close "X" button)
        privacy_popup = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close']"))
        )
        privacy_popup.click()
        print("Privacy popup handled: 'X' clicked.")
    except Exception as e:
        print("No privacy popup found or error occurred.")

# Function to click the "Show More" button
def click_button():
    try:
        # Locate the "Show More" button
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"root\"]/div/div[2]/div/div/main/div/div[1]/div[5]/div/div[3]/button"))
        )
        
        # Scroll the page until the button is in view
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(1)  # Short delay to ensure the scroll completes
        
        # Click the button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id=\"root\"]/div/div[2]/div/div/main/div/div[1]/div[5]/div/div[3]/button"))
        ).click()
        time.sleep(5)  # Wait for new content to load
    except Exception as e:
        print(f"Error clicking button: {e}")
        raise

# Function to write CSV files with a pandas DataFrame
def write_csv(dataframe, file_name):
    dataframe.to_csv(f"{file_name}.csv", index=False)

# Function to insert data into the database based on component type
def insert_into_database(data, component_type):
    db_config = {
        'host': 'localhost',
        'user': 'root',  # Replace with your MySQL username
        'password': 'Love@123456',  # Replace with your MySQL password
        'database': 'pc'  # Replace with your database name
    }

    # Map component types to their corresponding table and column names
    component_tables = {
        'gpuNv': 'GPU_Nvidia',
        'gpuAmd': 'GPU_AMD',
        'cpuInt': 'CPU_Intel',
        'cpuAmd': 'CPU_AMD',
        'motherInt': 'Motherboard_Intel',
        'motherAmd': 'Motherboard_AMD',
        'ram': 'RAM',
        'power': 'PowerSupplies',
        'ssd': 'SSD',
        'hdd': 'HDD',
        'case': 'Cases',
        'fans': 'Fans'
    }

    if component_type not in component_tables:
        print(f"Invalid component type: {component_type}")
        return

    table = component_tables[component_type]
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Step 1: Delete existing data in the table
        delete_query = f"DELETE FROM {table}"
        cursor.execute(delete_query)
        print(f"Old data from {table} deleted.")

        # Step 2: Prepare insert query
        insert_query = f"""
        INSERT INTO {table} (Name, Price, Discount, WebLink)
        VALUES (%s, %s, %s, %s)
        """

        # Step 3: Iterate through the DataFrame and insert each row
        for _, row in data.iterrows():
            name = row['Name']
            price = float(row['Sale Price'].replace('$', '').replace(',', '')) if row['Sale Price'] != 'N/A' else 0
            discount = float(row['Discount'].replace('SAVE $', '').strip()) if row['Discount'] != 'N/A' else 0
            weblink = row['Product Link'] if row['Product Link'] != 'N/A' else None

            # Check if any key fields are missing (name, price, or weblink)
            if not name or not price or not weblink:
                continue  # Skip this row if important fields are missing

            # Insert the data into the respective table
            cursor.execute(insert_query, (name, price, discount, weblink))

        # Commit the transaction
        connection.commit()
        print(f"Data successfully inserted into {table} table.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# URL list for scraping
allUrls = {
    'gpuNv': "https://www.bestbuy.ca/en-ca/collection/graphics-cards-with-nvidia-chipset/349221?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bcategory%253AGraphics%2BCards",
    'gpuAmd': "https://www.bestbuy.ca/en-ca/collection/amd-graphics-cards/442652?icmp=computing_evergreen_graphics_cards_category_listing_category_icon_shopby_amd",
    'cpuInt': "https://www.bestbuy.ca/en-ca/collection/intel-cpus/347204?icmp=computing_evergreen_cpu_category_listing_category_icon_shopby_intel",
    'cpuAmd': "https://www.bestbuy.ca/en-ca/collection/amd-cpus/347205?icmp=computing_evergreen_cpu_category_listing_category_icon_shopby_amd",
    'motherIntel': "https://www.bestbuy.ca/en-ca/collection/motherboards-for-intel-cpu/348207?icmp=computing_evergreen_motherboards_category_listing_category_icon_shopby_intel",
    'motherAmd': "https://www.bestbuy.ca/en-ca/collection/motherboards-for-amd-cpus/348208?icmp=computing_evergreen_motherboards_category_listing_category_icon_shopby_amd",
    'ram': "https://www.bestbuy.ca/en-ca/category/desktop-memory-ram/20359?icmp=computing_evergreen_pc_components_category_detail_offer_shopby_desktop_memory_ram",
    'power': "https://www.bestbuy.ca/en-ca/category/computer-power-supplies/20380?icmp=computing_evergreen_pc_components_category_detail_offer_shopby_power_supply_units",
    'ssd': "https://www.bestbuy.ca/en-ca/category/internal-ssd/17233243?icmp=omputing_20240510_internal_hard_drives_and_ssds_ssc_category_icon_internal_ssds",
    'hdd': "https://www.bestbuy.ca/en-ca/category/desktop-internal-hard-drives/20240?icmp=omputing_20240510_internal_hard_drives_and_ssds_ssc_category_icon_internal_hard_drives",
    'case': "https://www.bestbuy.ca/en-ca/category/computer-cases/30138?icmp=computing_evergreen_pc_components_category_detail_offer_shopby_pc_cases",
    'fans': "https://www.bestbuy.ca/en-ca/category/pc-fans-cooling/18637816?icmp=computing_evergreen_pc_components_category_detail_offer_shopby_pc_fans_cpu_coolers"
}
# Main scraping loop for each URL
for component, url in allUrls.items():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.set_window_size(1200, 900)

    # Handle popups
    handle_popups()

    time.sleep(5)  # Give time to load full page

    # Attempt to load all items by repeatedly clicking "Show More"
    while True:
        try:
            click_button()
            print("\"Show more\" button has been clicked")
            break
        except:
            print("No more 'Show more' button or an error occurred.")
            break

    # Once the full page with products is loaded, get the HTML data
    html = driver.page_source
    html_soup = BeautifulSoup(html, "html.parser")
    product_containers = html_soup.find_all("div", class_="style-module_col-xs-12__TFIB5")
    print(f"Found {len(product_containers)} products.")

    driver.quit()
    print("Driver has been quit")

    # Create lists to store product data
    names = []
    prices = []
    discounts = []
    links = []

    for product in product_containers:
        try:
            name = product.find("div", class_="productItemName_3IZ3c")
            names.append(name.text.strip() if name else "N/A")

            price = product.find("div", class_="style-module_salePrice__WYInP")
            prices.append(price.text.strip() if price else "N/A")

            discount = product.find("span", class_="style-module_productSaving__g7g1G")
            discounts.append(discount.text.strip() if discount else "N/A")

            link = product.find("a", class_="link_3hcyN")
            links.append(f"https://www.bestbuy.ca{link['href']}" if link and "href" in link.attrs else "N/A")

        except Exception as e:
            print(f"Error processing product: {e}")
            continue

    # Ensure all lists are of equal length
    max_length = max(len(names), len(prices), len(discounts), len(links))
    names += ["N/A"] * (max_length - len(names))
    prices += ["N/A"] * (max_length - len(prices))
    discounts += ["N/A"] * (max_length - len(discounts))
    links += ["N/A"] * (max_length - len(links))

    # Create a DataFrame
    product_dict = {
        "Name": names,
        "Sale Price": prices,
        "Discount": discounts,
        "Product Link": links
    }
    product_dataframe = pd.DataFrame(product_dict)

    # Write to CSV
    write_csv(product_dataframe, f"{component}_products_on_sale")

    # Insert into the database
    insert_into_database(product_dataframe, component)

    print(f"Web scraping, CSV writing, and database insertion for {component} complete!")
