# Fullproof code to collect reviews and user data from TripAdvisor of multiplePlaces

import sys
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import time
import multiprocessing

def ignore_ssl_errors(driver, url):
    try:
        driver.get(url)
    except WebDriverException as e:
        if "SSL" in str(e):
            print(f"SSL/TLS handshake error encountered for URL: {url}. Skipping...")
        else:
            raise e

def scrape_and_append_reviews(url, destination_code):
    #User Details
    profiles_list=[]
    combined_data_list = []

    # default number of scraped pages
    num_page = 50
    
    # default path to file to store data
    path_to_file = "C:\\Users\\vishn\\Desktop\\SET1\\Reviews\\reviews_" + destination_code + ".csv"

    # open the file to save the review
    csvFile = open(path_to_file, 'a', encoding="utf-8")
    csvWriter = csv.writer(csvFile)

    column_headings = ["Date", "Title", "Review", "Destination_ID", "Name", "Username", "Location", "Joined_Date"]
    csvWriter.writerow(column_headings)

    # import the webdriver
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument('--headless')
#     chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=webdriver.ChromeOptions().add_argument('--headless'))
#     driver = webdriver.Chrome(chrome_options)
    driver.maximize_window()
    driver.get(url)

    # change the value inside the range to save more or less reviews
    for i in range(0, num_page):

        # expand the review 
        time.sleep(2)

        container = driver.find_elements("xpath","//div[contains(@data-automation, 'reviewCard')]")
        dates = driver.find_elements("xpath","//div[@class='biGQs _P pZUbB ncFvv osNWb']")

        for j in range(len(container)):
            button = container[j].find_element("xpath", ".//button//span[text()='Read more']/..")
            if button.is_displayed() and button.is_enabled():
                button.click()
            title = container[j].find_element("xpath",".//div[@class='biGQs _P fiohW qWPrE ncFvv fOtGX']/a/span").text
            review = container[j].find_element("xpath",".//div[@class='biGQs _P pZUbB KxBGd']/span[@class='yCeTE']").text.replace("\n", "  ")

            profile_link = container[j].find_element("xpath", ".//a[contains(@class, 'BMQDV')]").get_attribute("href")
            profiles_list.append(profile_link)

            if len(dates) > j:
                date = " ".join(dates[j].text.split(" ")[-2:])
            else:
                date = "Date Not Available"

            combined_data = {
                "Date": date,
                "Title": title,
                "Review": review,
                "Destination_ID": destination_code,
                "Name": "",
                "Username": "",
                "Location": "",
                "Joined_Date": ""   
            }
            combined_data_list.append(combined_data)
            

        # change the page            
        try:
            nextbutton=driver.find_element("xpath",".//a[contains(@data-smoke-attr,'pagination-next-arrow')]")
            if nextbutton.is_displayed() and nextbutton.is_enabled():
                nextbutton.click()
            else:
                print("Reached the last page.")
                break
        except NoSuchElementException:
            print("Pagination element not found. Reached the last page.")
            break


    iteration = 0
        

    for profile_url in profiles_list:
        
        iteration+=1
        
        try:
            driver.get(profile_url)
            time.sleep(2)

            try:
                intro = driver.find_element("xpath", "//div[contains(@class, 'Me Nb MD NC')]")
            except NoSuchElementException:
                intro = None
            
            loc = ""
            joined = ""
            username = ""
            name = ""
            
            if intro:
                try:
                    loc = intro.find_element("xpath", ".//span[@class='PacFI _R S4 H3 LXUOn default']").text
                except NoSuchElementException:
                    loc = ""

                try:
                    joined = intro.find_element("xpath", ".//span[@class='ECVao _R H3']").text
                except NoSuchElementException:
                    joined = ""

                try: 
                    user_info = driver.find_element("xpath", "//span[@class='ecLBS _R shSnD']")
                except NoSuchElementException:
                    user_info = None

                if user_info:
                    try:
                        username = user_info.find_element("xpath", ".//span[@class='Dsdjn _R']").text
                    except NoSuchElementException:
                        username = ""

                    try:
                        name = user_info.find_elements("xpath", ".//span[@class='JWmxy']/h1/span[@class='OUDwj b brsfY']")[0].text
                    except (IndexError, NoSuchElementException):
                        name = ""

            combined_data = combined_data_list[iteration - 1]
            combined_data["Name"] = name
            combined_data["Username"] = username
            combined_data["Location"] = loc
            combined_data["Joined_Date"] = joined

        except WebDriverException as e:
            if "SSL" in str(e):
                print(f"SSL/TLS handshake error encountered for URL: {url}. Skipping...")
                combined_data = combined_data_list[iteration - 1]
                combined_data["Name"] = ""
                combined_data["Username"] = ""
                combined_data["Location"] = ""
                combined_data["Joined_Date"] = ""
            else:
                raise e

    for data in combined_data_list:
        csvWriter.writerow([data["Date"], data["Title"], data["Review"], data["Destination_ID"], data["Name"], data["Username"], data["Location"], data["Joined_Date"]])
     
    driver.quit()