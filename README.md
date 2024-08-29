# BizCardX - Business Card Data Extractor
## Overview
BizCardX is a Streamlit application that extracts information from business card images using Optical Character Recognition (OCR) technology. This application allows users to upload images of business cards, extract relevant details like the cardholder's name, designation, email, phone number, and more, and store this information in a MySQL database. Users can also view, edit, update, and delete stored business card data.

## Features
- 1. Home Page: Introduction and welcome message for users.
- 2. Upload & Extract: Upload a business card image and extract information using OCR.
- 3. Edit/Update & View: Edit or update extracted information and view updated data.
- 4. Delete & View: Delete a specific card's information and view remaining data

## Technologies Used
- Frontend: Streamlit, HTML/CSS for basic styling
- Backend: Python, MySQL
- Libraries:
  - easyocr for Optical Character Recognition
  - mysql-connector-python for MySQL database connection
  - Pandas for data manipulation
  - OpenCV and PIL for image processing

## Prerequisites
- Python 3.x installed on your machine
- MySQL server installed and running
- Required Python packages (listed in requirements.txt)

## Usage
1. Run the Application:
   ```bash
   streamlit run app.py
   ```
2. Navigate Through the App:
   - Home Page: Introduction and overview of the application.
   - Upload & Extract: Upload a business card image and click to extract information.
   - Edit/Update & View: Select a cardholder name to edit their details.
   - Delete & View: Select a cardholder name to delete their details from the database.

## File Structure
 ```bash
/bizcardx
│-- bizcard_dashboard.py      # Main application file
│-- requirements.txt          # List of required Python packages
│-- README.md                 # Project documentation
│-- bizcard-dataset/          # Directory to store business card images
```

## Screenshots
![image](https://github.com/user-attachments/assets/70edeb67-6c20-413f-9a9b-f566b4307f2a)

![image](https://github.com/user-attachments/assets/599330b6-d41e-4d82-af6b-4d6372cc7cb3)

![image](https://github.com/user-attachments/assets/7efd1a44-d2e5-4b15-b2ed-27821fdd3dba)

![image](https://github.com/user-attachments/assets/98b9db02-f1a6-4a27-972c-4119389002e0)

![image](https://github.com/user-attachments/assets/cbf08731-7f4b-4650-bf4a-c7da52576a58)

![image](https://github.com/user-attachments/assets/304a0b60-c81c-4c95-b957-5afff1543030)

![image](https://github.com/user-attachments/assets/e7e70f1b-66fb-4296-a6db-6937e516a005)

## Demo Video
### Click Here to view demo video
https://www.linkedin.com/posts/vijayachandrika-r-bb554023a_datascience-imageprocessing-easyocr-activity-7234845720346775552-vaqH?utm_source=share&utm_medium=member_desktop

## Contact
For any questions or support, please contact `iam.chandrika92@gmail.com `









