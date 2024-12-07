import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

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

url = "https://www.bestbuy.ca/en-ca/collection/graphics-cards-with-nvidia-chipset/349221?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bcategory%253AGraphics%2BCards"

options = webdriver.ChromeOptions()
#options.add_argument("--incognito")  # Fresh start every time so no interference
# options.add_argument("--headless")  # Uncomment for headless mode (no visible browser)

driver = webdriver.Chrome(options=options)  # Initialize driver with Chrome options defined above
driver.get(url)  # Bring the browser to the URL specified above
driver.set_window_size(1200, 900)  # Set window resolution so all elements can still load on page

# Handle popups
handle_popups()

#assert "products on Sale" in driver.title  # Make sure we are on the right page before proceeding
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
#print(html)


# Parse the HTML data with BeautifulSoup for analysis and sorting
html_soup = BeautifulSoup(html, "html.parser")
#print(html_soup)
product_containers = html_soup.find_all("div", class_="style-module_col-xs-12__TFIB5")  # Find containers with product info
#print(product_containers)
print(f"Found {len(product_containers)} products.")

driver.quit()  # Close our automated browser
print("Driver has been quit")
# Create lists to store product data
names = []
prices = []
discounts = []
ratings = []
num_reviews = []
links =[]
images = []
for product in product_containers:  # Iterate through each product on the page
    try:
        # Extract product name (you can modify this part based on the actual HTML structure)
        name = product.find("div", class_="productItemName_3IZ3c")
        names.append(name.text.strip() if name else "N/A")

        # Extract price
        price = product.find("div", class_="style-module_salePrice__WYInP")
        prices.append(price.text.strip() if price else "N/A")

        # Extract discount (if available)
        discount = product.find("span", class_="style-module_productSaving__g7g1G")
        discounts.append(discount.text.strip() if discount else "N/A")

        # Extract rating
        rating = product.find("meta", attrs={"itemprop": "ratingValue"})
        ratings.append(float(rating["content"]) if rating else "N/A")

        # Extract number of reviews
        review = product.find("span", class_="style-module_reviewCountContainer__HQlM5")
        num_reviews.append(int(review.text.strip("()").split()[0]) if review else 0)

        #Extract Link
        link = product.find("a", class_="link_3hcyN")
        links.append(f"https://www.bestbuy.ca{link['href']}" if link and "href" in link.attrs else "N/A")

        # Extract Image URL
        image = product.find("img", class_="productItemImage_1en8J")
        images.append(image["src"] if image and "src" in image.attrs else "N/A")
        
    except Exception as e:
        print(f"Error processing product: {e}")
        continue 

max_length = max(len(names), len(prices), len(discounts), len(ratings), len(num_reviews))

# Fill missing values with "N/A" or 0 to ensure consistent length
names += ["N/A"] * (max_length - len(names))
prices += ["N/A"] * (max_length - len(prices))
discounts += ["N/A"] * (max_length - len(discounts))
ratings += ["N/A"] * (max_length - len(ratings))
num_reviews += [0] * (max_length - len(num_reviews))
links += ["N/A"] * (max_length - len(links))
images += ["N/A"] * (max_length - len(images))

# Create a dictionary with headers and values of product data
product_dict = {
    "Name": names,
    "Sale Price": prices,
    "Discount": discounts,
    "Rating": ratings,
    "Number of Reviews": num_reviews,
    "Product Link": links,
    "Image URL": images
}

# Create a structured DataFrame from dictionary data for easy access and use
product_dataframe = pd.DataFrame(product_dict)

# Write file to CSV for external use
write_csv(product_dataframe, "products_on_sale")
print("Web scraping and CSV file writing complete!")