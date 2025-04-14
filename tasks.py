from robocorp.tasks import task
from robocorp import browser
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import os

from typing import Dict


@task
def open_robot_order_website():
    """" Runs the main task"""
    create_dir()
    access_the_page()
    download_csv()
    orders = get_information_from_csv()
    for order in orders:
        fill_form(order)
    archive_receipts()


def create_dir():
    dirs = [
        'output/screenshots',
        'output/receipts',
    ]

    for new_dir in dirs:
        os.makedirs(new_dir, exist_ok=True)
    
def access_the_page():
    """Access the page, and gets through the pop up"""
    browser.goto('https://robotsparebinindustries.com/#/robot-order')

def accept_violation():
    """Clicks the OK button to give away rights"""
    page = browser.page()
    page.click('button:text("OK")')


def download_csv():
    """Downloads the CSV file"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", target_file='output/orders.csv', overwrite=True)

def get_information_from_csv():
    """Open the csv output and reads"""

    # nunder,Head,Body,Legs,Address
    table = Tables()
    orders = table.read_table_from_csv('output/orders.csv')
    return orders
    

def fill_form(order: Dict):
    """Fills out the relevant parts of the form"""
    page = browser.page()
    accept_violation()
    page.select_option('#head', str(order['Head']))
    page.click(f'#id-body-{str(order['Body'])}')
    page.fill('input[placeholder="Enter the part number for the legs"]', str(order['Legs']))
    page.fill('#address', order['Address'])
    page.click("#preview")

    # Check if error exist
    while True:
        page.click('#order')
        error_message = page.locator('div.alert.alert-danger')
        if error_message.count() == 0:
            break

    pdf_file = store_receipt_as_pdf(order['Order number'])
    screenshot = screenshot_robot(order['Order number'])
    embed_screenshot_to_receipt(screenshot=screenshot, pdf_file=pdf_file )

    page.click('#order-another')

def store_receipt_as_pdf(order_number):
    """Stores the robot receipts as a pdf"""
    pdf = PDF()
    page = browser.page()
    receipt = page.locator('#receipt').inner_html()
    recepit_path = f'output/receipts/order-{order_number}_receipt.pdf'

    # Create the pdf 
    pdf.html_to_pdf(content=receipt, output_path=recepit_path)
    return recepit_path

    
def screenshot_robot(order_number):
    """Takes screenshot of something"""
    page = browser.page()
    path_to_image = f"output/screenshots/screenshot_order_{order_number}.png"

    # Convert image to pdf
    page.locator("#robot-preview-image").screenshot(path=path_to_image) 
    return path_to_image

def embed_screenshot_to_receipt(screenshot, pdf_file):
    # Add the image to the end
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, source_path=pdf_file, output_path=pdf_file)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'output/receipts_archive.zip')

