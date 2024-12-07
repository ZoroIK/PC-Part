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

# Function to insert data into the database
def insert_into_database(data):
    db_config = {
        'host': 'localhost',
        'user': 'root',  # Replace with your MySQL username
        'password': 'Love@123456',  # Replace with your MySQL password
        'database': 'pc'  # Replace with your database name
    }

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Prepare insert statement
        insert_query = """
        INSERT INTO GPUs (Name, Price, Discount, WebLink)
        VALUES (%s, %s, %s, %s)
        """
        
        for _, row in data.iterrows():
            # Extract values
            name = row['Name']
            price = float(row['Sale Price'].replace('$', '').replace(',', '')) if row['Sale Price'] != 'N/A' else 0
            discount = float(row['Discount'].replace('SAVE $', '').strip()) if row['Discount'] != 'N/A' else 0
            weblink = row['Product Link'] if row['Product Link'] != 'N/A' else None

            # Check if any of the key fields are missing
            if not name or not price or not weblink:  # Ignore this row if important fields are missing
                continue
            
            # Insert values into the database
            cursor.execute(insert_query, (name, price, discount, weblink))

        # Commit the transaction
        connection.commit()
        print("Data successfully inserted into the database.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Main scraping script
url = "https://www.bestbuy.ca/en-ca/collection/graphics-cards-with-nvidia-chipset/349221?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bcategory%253AGraphics%2BCards"

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
write_csv(product_dataframe, "products_on_sale")

# Insert into the database
insert_into_database(product_dataframe)

print("Web scraping, CSV writing, and database insertion complete!")
