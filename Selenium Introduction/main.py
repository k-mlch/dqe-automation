import csv
import time
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SeleniumWebDriverContextManager:
    def __init__(self):
        self.driver = None

    def __enter__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()


def extract_table_to_csv(driver, output_file="table.csv"):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "table")))

    table = driver.find_element(By.XPATH, "//*[@class='table']")
    columns = table.find_elements(By.CLASS_NAME, "y-column")

    headers = []
    rows_data = []

    for column in columns:
        header = column.find_element(By.ID, "header").text
        headers.append(header)

        cells = column.find_elements(By.CLASS_NAME, "cell-text")
        values = []
        for cell in cells:
            text = cell.text
            if text != header:
                values.append(text)
        rows_data.append(values)

    rows = []
    row_count = len(rows_data[0])
    for i in range(row_count):
        row = []
        for col in rows_data:
            row.append(col[i])
        rows.append(row)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def save_screenshot(driver, index):
    filename = f"screenshot{index}.png"
    driver.save_screenshot(filename)


def extract_doughnut_data(driver):
    doughnut = driver.find_element(By.CLASS_NAME, "pielayer")
    driver.execute_script("arguments[0].scrollIntoView(true);", doughnut)
    time.sleep(0.5)
    labels = doughnut.find_elements(By.CSS_SELECTOR, "text.slicetext[data-notex='1']")

    rows = []
    for label in labels:
        tspans = label.find_elements(By.TAG_NAME, "tspan")
        if len(tspans) >= 2:
            category = tspans[0].text.strip()
            value = tspans[1].text.strip()
            rows.append([category, value])

    return rows


def save_doughnut_csv(rows, index):
    filename = f"doughnut{index}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Facility Type", "Min Average Time Spent Clinic"])
        writer.writerows(rows)


def interact_with_doughnut(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pielayer")))

    doughnut = driver.find_element(By.CLASS_NAME, "pielayer")
    driver.execute_script("arguments[0].scrollIntoView(true);", doughnut)
    time.sleep(0.5)

    save_screenshot(driver, 0)

    rows = extract_doughnut_data(driver)
    save_doughnut_csv(rows, 0)

    filter_count = len(driver.find_elements(By.CLASS_NAME, "traces"))

    for i in range(filter_count):
        filters = driver.find_elements(By.CLASS_NAME, "traces")
        filters[i].click()
        time.sleep(1)

        save_screenshot(driver, i + 1)
        rows = extract_doughnut_data(driver)
        save_doughnut_csv(rows, i + 1)


with SeleniumWebDriverContextManager() as driver:
    try:
        file_path = os.path.join(
            os.path.dirname(__file__),
            "report.html"
        )
        driver.get("file:///" + file_path.replace("\\", "/"))

        extract_table_to_csv(driver)
        interact_with_doughnut(driver)

        time.sleep(3)

    except Exception as e:
        print("Something went wrong:", e)