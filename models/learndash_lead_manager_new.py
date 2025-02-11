import requests
from requests.auth import HTTPBasicAuth


def submit_elementor_form(name, phone, email,message,subject):
    try:
        # URL of the page with the Elementor form
        form_page_url = "https://english.woocom.cc/lead-contact/"
        
        # Clean up the email to remove extra whitespace or newline characters
        email = email.strip()
        
        # Ensure email is not empty or invalid
        if not email or "@" not in email or not email.isascii():
            email = "wrong@examplexx.com"  # Fallback to default email if the provided email is invalid
        
        # Data to be submitted to the form
        form_data = {
            "your-name": name,        # Replace with actual field name and value
            "phone": phone,           # Replace with actual field name and value
            "your-email": email, # Replace with actual field name and value
            "your-message": message, # Replace with actual field name and value
            "your-subject": subject,
            "status" : "New",
            "_wpcf7": "516",
            "_wpcf7_version": "5.9.8",
            "_wpcf7_locale": "en_US",
            "_wpcf7_unit_tag": "wpcf7-f516-p517-o1",
            "_wpcf7_container_post": "517",
            "_wpcf7_posted_data_hash": "4750c6acbdbc01df1df326a85eb7222e"
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # Create a session object
        with requests.Session() as session:
            # Make a POST request to submit form data
            response = session.post(form_page_url, data=form_data, headers=headers)

            # Check if submission was successful
            if response.status_code == 200:
                print("Form submitted successfully!")
            else:
                print(f"Failed to submit form: {response.status_code}")
                print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None

def get_woocommerce_customers_with_phone(site_url, consumer_key, consumer_secret):
    # Ensure the site URL ends with a trailing slash
    if not site_url.endswith('/'):
        site_url += '/'
    
    # Define the WooCommerce customers endpoint
    customers_endpoint = f"{site_url}wp-json/wc/v3/customers"
    
    # Make a GET request with HTTP Basic Auth using WooCommerce Consumer Key and Secret
    try:
        response = requests.get(customers_endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        
        # Check if the request was successful
        if response.status_code == 200:
            customers = response.json()
            # Filter customers with phone numbers
            #customers_with_phone = [customer for customer in customers if customer.get('billing', {}).get('phone')]
            return customers
        else:
            print(f"Failed to retrieve customers: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
    return []
    
##### NEW FUNCTION
def get_woocommerce_customers_wuth_status(site_url, consumer_key, consumer_secret):
    # Ensure the site URL ends with a trailing slash
    if not site_url.endswith('/'):
        site_url += '/'
    
    # Define the WooCommerce customers endpoint
    customers_endpoint = f"{site_url}wp-json/wc/v3/customers"
    
    # Make a GET request with HTTP Basic Auth using WooCommerce Consumer Key and Secret
    try:
        response = requests.get(customers_endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Check if the request was successful
        if response.status_code == 200:
            customers = response.json()
            # mariam - filter customers based on status
             filtered_customers = [customer for customer in customers if customer.get('status') != status_to_exclude] # create a list
            return filtered_customers ##
        else:
            print(f"Failed to retrieve customers: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
    return []
    
    
def get_courses(base_url, username, app_password):
    courses_endpoint = f"{base_url}/sfwd-courses"
    
    try:
        response = requests.get(courses_endpoint, auth=HTTPBasicAuth(username, app_password))
        response.raise_for_status()  # Check for HTTP errors
        courses = response.json()    # Parse JSON response
        courses_combined = "Courses for new user:"
        
        # Print each course's title and ID
        for course in courses:
            course_id = course['id']
            course_title = course['title']['rendered']
           # print(f"Course ID: {course_id}, Course Title: {course_title}".encode('utf-8', 'ignore').decode('utf-8'))
            courses_combined += f"\nNicols courses:\nCourse ID: {course_id} Course Title: {course_title}\n"
            #print(f"Course ID: {course_id}, Course Title: {course_title}".encode('utf-8').decode('utf-8'))

        print("return")
        return courses_combined
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return ""