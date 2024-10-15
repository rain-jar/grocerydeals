import psycopg2
from playwright.sync_api import sync_playwright
import location

#Connect to PostgreSQL
connection = psycopg2.connect(
    dbname="grocery_deals",
    user="kuttoosh",
    password="pgrrn@19",
    host="localhost"
)
cursor=connection.cursor()
print(connection.get_dsn_parameters())
cursor.execute("SELECT current_database();") 
print(cursor.fetchone())
cursor.execute("SET search_path TO public;")


def scrape_deals(page) : 
    print('testing the scraping function')
    page.wait_for_selector('div.product-tile__details')
    product_containers = page.query_selector_all('div.product-tile__details') 

    # Extract data from each container
    for container in product_containers:
        product_name = container.query_selector('h3.product-tile__details__info__name').inner_text()
        original_price_elem = container.query_selector('span.selling-price-list__item__price--now-price__value')
        original_price = original_price_elem.inner_text() if original_price_elem else 'N/A'
        new_price_elem = container.query_selector('div.selling-price-list--sale')
        new_price = new_price_elem.inner_text() if new_price_elem else 'N/A'
        unitprice_elem = container.query_selector('ul.comparison-price-list')
        unitprice = unitprice_elem.inner_text() if unitprice_elem else 'NA'

         # Insert the data into PostgreSQL
        cursor.execute("""
            INSERT INTO newdeals (product_name, original_price, new_price, unitprice)
            VALUES (%s, %s, %s, %s)
        """, (product_name, original_price, new_price, unitprice))


   # print(page.title())  # Just to check if navigation is working
    connection.commit()

if __name__ == "__main__" : 
    postal_code = input("Enter the postal code: ")
    cookies_file = 'cookies.json'
    browser, page, playwright = location.navigate_to_deals(postal_code, cookies_file)
    scrape_deals(page)


# Close database connection
browser.close()
playwright.stop()
cursor.close()
connection.close()