import requests as req
from bs4 import BeautifulSoup as bs
import argparse
import smtplib
import re
from email.mime.text import MIMEText


def send_email(mail_username,mail_app_pass, url, product, new_price):
    
    # Email content
    subject = "Test Email from gal"
    body = f"The Product you requested to follow: {product}\nhas lowered its price below the threshhold!\n" \
           f"The new listing price is: {new_price}\n\nYou can check it out here: {url}" \
           "\n\nHave a nice day!" 

    # Create the email
    msg = MIMEText(body, "plain")  # Use "plain" for plain text emails
    msg["From"] = mail_username
    msg["To"] = mail_username
    msg["Subject"] = subject
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.set_debuglevel(1)  # Debug SMTP communication
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user=mail_username, password=mail_app_pass)
            print("Login successful!")
            server.sendmail(msg["From"], msg["To"], msg.as_string())
            print("Email sent successfully!")
   
    except Exception as e:
        print(f"An error occurred: {e}")


def extract_price_with_currency(response):
    soup = bs(response.text, "html.parser")
    price_with_currency = soup.find("span", class_="priceToPay").text.strip()
    return price_with_currency

# getting Amazon headers
def get_headers():
    
    headers =  {    
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0", 
        'Accept-Encoding': 'gzip, deflate', 
        'Accept': '*/*', 
        "Referer": "https://www.amazon.com/",
        'Connection': 'keep-alive'
    }

    return headers

def main():

    parser = argparse.ArgumentParser()
    
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--mail_username", type=str, required=True)
    parser.add_argument("--mail_app_pass", type=str, required=True)

    args = parser.parse_args()

    threshold = 100
    headers = get_headers()
    url = args.url
    response = req.get(url=url, headers=headers)

    if response.status_code == 200:
        
        price_with_currency = extract_price_with_currency(response)
        currency = price_with_currency[0]
        price_without_currency = float(price_with_currency[1:])

        product_pattern = r".+.com/([\w*\-\_\\d*]+)/.*"
        product = re.search(product_pattern, url).group(1)
        
        if price_without_currency <= threshold:
            
            print(f"Price of the product is less than {threshold} {currency} & is currently {price_with_currency}")
            send_email(args.mail_username, args.mail_app_pass, url, product, price_with_currency)
        
        else:
            print(f"Price of the product is {price_with_currency} which is more than the {currency}{threshold} threshold")
    else:
        print(f"Failed to fetch the page for scraping. Status code: {response.status_code}")


if __name__ == "__main__":
    main()


