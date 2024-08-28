import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import mysql.connector
from mysql.connector import Error
import easyocr
import os
import re
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import time

# Setting the page configuration
st.set_page_config(page_title="Business Card Data Extractor", layout="wide")

# Custom CSS to add a background image to the sidebar and style the app
sidebar_styles = """
    <style>
        /* Sidebar background image */
        [data-testid="stSidebar"] {
            background-image: url("https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0");
            background-size: cover;
            background-position: center;
            color: white;  /* Change text color to white for better contrast */
        }
        /* Main content area background color */
        .main {
            background-color: #d6d8db;
        }
        /* Sidebar styles for menu and text */
        .css-1v0mbdj {
            color: white;
        }
        /* Centering the logo image */
        .center-image {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
        }
        .center-image img{
            border-radius: 100%;
        }
        /* Font styles for the entire app */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Roboto', sans-serif;
        }
    </style>
"""
st.markdown(sidebar_styles, unsafe_allow_html=True)

# database connection
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database='bizcard_data'
    )
mycursor = mydb.cursor()

absolute_path = os.path.abspath("./images/logo.JPG")

# Sidebar menu using streamlit-option-menu
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:  # This column will center the image
        st.image(absolute_path, width=70)
    # st.markdown(f'<div class="center-image"><img src="{image_logo}" width="120"></div>', unsafe_allow_html=True) #  Logo image
    st.title("BizCardX")
    page = option_menu(
        menu_title="",  # No title for the menu, using image and title instead
        options=["Home", "Upload & Extract", "Edit/Update & View", "Delet & View"],
        icons=["house", "cloud-upload", "pencil", "trash"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin-bottom": "10px",
                "color": "white",
                "--hover-color": "#0d6efd",
                "background-color": "rgba(0, 0, 0, 0.6)",
                "border-radius": "5px",
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {"background-color": "#0d6efd"},
        },
    )

# Directory to store uploaded files
temp_dir = "uploaded_files"
os.makedirs(temp_dir, exist_ok=True)
temp_file_path = os.path.join(temp_dir, "temp_card.jpg")

# Function to get card holders name from MYSQL
def Get_card_names():
    card_name_query = "SELECT card_holder_name FROM card_information"
    mycursor.execute(card_name_query)
    result = mycursor.fetchall()
    final_names = []
    for row in result:
        final_names.append(row[0])
    return final_names

 # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
def img_to_binary(file):
    # Convert image data to binary format
    with open(file, 'rb') as file:
        binaryData = file.read()
        st.write(f"Storing image of size: {len(binaryData)} bytes")
    return binaryData


# Main Application Logic
# Home page
if page == "Home":
    st.title("BizCardX - Business Card Data Extractor")
    st.write("Upload a business card image, and this app will extract the text using Optical Character Recognition (OCR).")

# Upload page
elif page == "Upload & Extract":
        tab1,tab2,tab3=st.tabs(["UPLOAD CARD","EXTRACT DATA","STORE DATA"])

        with tab1:
            st.markdown("### Upload a Business Card")
            uploaded_file = st.file_uploader("Choose an image of a business card", type=["jpg", "jpeg", "png"])

            if uploaded_file is not None:
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                # Display the uploaded card
                st.markdown("### You have uploaded the card")
                st.image(uploaded_file, width=400)
            else:
                st.write("Please Upload a Business Card!")
        with tab2:
            st.markdown("### Extract Information from the Business Card")
            # Read Image
            image = cv2.imread(temp_file_path)
            # Create instance for text detector
            reader = easyocr.Reader(['en'],gpu=False)
            # Detect text on the image
            result = reader.readtext(image)

            # Draw BBox and text - rectangular mark
            threshold = 0.25
            Raw_Data = []
            for t in result:
                Raw_Data.append(t[1])
                bbox, text, score = t
                tl,tr,br,bl = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                if score > threshold:
                    cv2.rectangle(image, tl, br,(0,255,0),4)
                    cv2.putText(image, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1.25, (255,0,0), 1)
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Create a figure and axis to display the image
            fig, ax = plt.subplots()
            ax.imshow(image_rgb)
            # # DISPLAYING THE CARD WITH HIGHLIGHTS
            col1, col2= st.columns(2)
            with col1:
                st.pyplot(fig)
            text = Raw_Data
        
            data = {
                "card_holder_name" : [],
                "designation" : [],
                "email" : [],
                "company" : [],
                "phone_number" : [],
                "website" : [],
                "area" : [],
                "city" : [],
                "pincode" : [],
                "state" : [],
                'image': img_to_binary(temp_file_path)
            }
            data["card_holder_name"].append(text[0])
            data["designation"].append(text[1])

            for i in range(2,len(text)):
                if text[i].startswith("+") or (text[i].replace("-","").isdigit() and "-" in text[i]):
                    data["phone_number"].append(text[i])
                    if len(data["phone_number"]) == 2:
                        data["phone_number"] = " & ".join(data["phone_number"])
                elif "@" in text[i]:
                    data["email"].append(text[i])
                elif re.match(r'(www\s.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|(www.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|(www.)[a-zA-Z0-9.-]+[a-zA-Z]{2,}', text[i], re.IGNORECASE):
                    if ".com" in text[i]:
                        data["website"] = text[i]
                    else:
                        data["website"] = text[i][ : 7] + "." +  text[i][7 : ]
                elif "WWW" in text[i]:
                    data["website"] = text[4] +"." + text[5]
                elif re.findall('[0-9]{6,}', text[i]):
                    data["pincode"] = text[i].split(' ' , 1)
                    if len(data["pincode"]) == 2:
                        for j in data["pincode"]:
                            if "Tamilnadu " in j or "Tamil Nadu" in j or "TamilNadu" in j:
                                data["state"] = j
                            else:
                                data["pincode"] = j
                    else:
                        data["pincode"] = text[i]
                elif re.findall('[0-9]{3}', text[i]):
                    if ",," in text[i] and ("Tamilnadu " in text[i] or "Tamil Nadu" in text[i] or "TamilNadu" in text[i] or "TamilNadu;" in text[i]):
                        data["area"] = (text[i][ : 10] + text[i][10 + 1: ]).split(',' , 2)
                    elif "Tamilnadu " in text[i] or "Tamil Nadu" in text[i] or "TamilNadu" in text[i] or "TamilNadu;" in text[i]:
                        data["area"] = text[i].split(',' , 2)
                    elif "St ," not in text[i]:
                        data["area"] = (text[6] +" " + text[11] + " " + text[7]).split(',' , 1)
                    else:
                        data["area"] = text[i].split(',' , 1)
                    if len(data["area"]) >= 2:
                        for k in data["area"]:
                            if "Tamilnadu " in k or "Tamil Nadu" in k or "TamilNadu" in k:
                                data["state"] = k
                            elif re.findall('[0-9]{3}', k):
                                data["area"] = k
                            else:
                                data["city"] = k
                else:
                    data["company"].append(text[i])
            if len(data["company"]) == 1:
                data["company"] = data["company"]
            elif len(data["company"]) == 2:
                data["company"] = " ".join(data["company"])
            else:
                data["company"] =  data["company"][2] + " " + data["company"][3]
                
            # CREATE DATAFRAME
            with col2:
                Data_df = pd.DataFrame(data) 
                st.success("### Data Extracted!")
                st.write(Data_df)
        with tab3:
            st.markdown("### STORING datas in mysql")
            if Data_df is not None and not Data_df.empty:
                mydb = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database='bizcard_data'
                    )
                mycursor = mydb.cursor()
                create_query = '''CREATE TABLE IF NOT EXISTS card_information ( card_holder_name VARCHAR(255) PRIMARY KEY,
                                                                                designation VARCHAR(255),
                                                                                email VARCHAR(255),
                                                                                company VARCHAR(255),
                                                                                phone_number VARCHAR(255),
                                                                                website VARCHAR(255),
                                                                                area VARCHAR(255),
                                                                                city VARCHAR(255),
                                                                                pincode VARCHAR(20),
                                                                                state VARCHAR(255),
                                                                                image LONGBLOB
                                                                            )'''
                mycursor.execute(create_query)
                mydb.commit()
                # Insert Values to sql table
                for _,row in Data_df.iterrows():
                    try:
                        insert_query = '''INSERT INTO card_information(card_holder_name,
                                                                        designation,
                                                                        email,
                                                                        company,
                                                                        phone_number,
                                                                        website,
                                                                        area,
                                                                        city,
                                                                        pincode,
                                                                        state,
                                                                        image) VALUES(%s, %s, %s,%s, %s,%s, %s, %s,%s, %s,%s)'''
                        data = tuple(row)
                        mycursor.execute(insert_query,data)
                        mydb.commit()
                        mycursor.close()
                        mydb.close()
                        st.success("Data uploaded to the database successfully!")
                    except mysql.connector.Error as error:
                        st.warning(f"Failed to store data in the database: {error}")
            else:
                st.warning("No data to store. Please upload and extract business card data first.")
                pass
elif page == "Edit/Update & View":
    card_names = Get_card_names()
    st.markdown("### Select the Card Holder Name to edit")
    selected_name = st.selectbox('Select Channel Name', options=card_names, index=None, placeholder="Select Name...")

    card_details_query = "SELECT card_holder_name,designation, email, company, phone_number, website, area, city, pincode, state FROM card_information WHERE card_holder_name = %s"
    mycursor.execute(card_details_query, (selected_name,))
    result1 = mycursor.fetchone()
    if selected_name is not None:
        tab1,tab2=st.tabs(["UPDATE CARD","VIEW UPDATED DATA"])
        with tab1:
            st.markdown("### Edit the Information")
            col1, col2= st.columns(2)
            with col1:
                # DISPLAYING ALL THE INFORMATION
                card_holder_name = st.text_input("Card Holder Name", result1[0])
                designation = st.text_input("Designation", result1[1])
                email = st.text_input("Email", result1[2])
                company = st.text_input("Company Name", result1[3])
                phone_number = st.text_input("Mobile Number", result1[4])
            with col2:
                website = st.text_input("Website", result1[5])
                area = st.text_input("Area", result1[6])
                city = st.text_input("City", result1[7])
                pincode = st.text_input("Pin Code", result1[8])
                state = st.text_input("State", result1[9])
            col1, col2 = st.columns([1, 1])

            # Place the button in the third column (right-aligned)
            with col2:
                if st.button("Commit changes to DB"):
                    # Update the information for the selected business card in the database
                    mycursor.execute("""UPDATE card_information SET card_holder_name=%s,
                                                            designation=%s, 
                                                            email=%s,
                                                            company=%s, phone_number=%s,
                                                            website=%s,
                                                            area=%s,
                                                            city=%s,
                                                            pincode=%s,
                                                            state=%s WHERE card_holder_name=%s """, 
                                                            (card_holder_name,
                                                            designation, 
                                                            email, 
                                                            company, 
                                                            phone_number, 
                                                            website, 
                                                            area, 
                                                            city,
                                                            pincode, 
                                                            state, 
                                                            selected_name))
                    mydb.commit()
                    st.success("New Information updated in the database successfully.")
        with tab2:
            st.markdown("### View the Updated Information")
            mycursor.execute("SELECT card_holder_name,designation, email, company, phone_number, website, area, city, pincode, state FROM card_information")
            updated_data = mycursor.fetchall()
            df_updated_data = pd.DataFrame(updated_data, 
                columns=["card_holder_name","designation","email","company","phone_number","website","area", "city","pincode","state"])
            
            styled_df = df_updated_data
            st.write(styled_df)
elif page == "Delet & View":
    tab1,tab2=st.tabs(["DELETE CARD","VIEW REMAINING DATA AFTER DELETE"])
    with tab1:
        def refresh_card_names():
            # Function to fetch the list of card holder names from the database.
            card_names = Get_card_names()
            return card_names
        def get_card_image(card_holder_name):
            get_img_query = "SELECT image FROM card_information WHERE card_holder_name = %s"
            mycursor.execute(get_img_query,(card_holder_name,))
            result = mycursor.fetchone()
            if result:
                image_data = result[0]
                # st.write(f"Retrieved image of size: {len(image_data)} bytes")
                return image_data
            else:
                return None
        card_names = Get_card_names()
        st.markdown("### Select the Card Holder Name to Delete")
        selected_name = st.selectbox('Select Channel Name', options=card_names, index=None, placeholder="Select Name...")
        if selected_name is not None:
            st.write(f"### You have selected :green[**{selected_name}'s**] card to delete")
            image_dataa = get_card_image(selected_name)
            if image_dataa is not None:
                # st.write(f"Image data size: {len(image_dataa)} bytes")
                nparr = np.frombuffer(image_dataa, np.uint8)
                # st.write(f"Array shape from buffer: {nparr.shape}")
                try:
                    # nparr = np.frombuffer(image_data, np.uint8)
                    image_return = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    # image_return = Image.open(io.BytesIO(image_data))
                    if image_return is None:
                        st.error("Failed to decode the image. The file may be corrupted.")
                    else:
                        st.image(image_return, width=300, channels='BGR' , caption=f"{selected_name}'s Business Card")
                except Exception as e:
                    st.error(f"An error occurred while processing the image: {e}")
            else:
                st.write("No image found for the selected card holder.")
            st.write("#### Are You Sure")
            if st.button("Yes,sure"):
                try:
                    card_delete_query = "DELETE FROM card_information WHERE card_holder_name = %s"
                    mycursor.execute(card_delete_query, (selected_name,))
                    mydb.commit()
                    st.success("Business card infos deleted from the database.")
                    # Delay for 2 seconds before refreshing
                    time.sleep(5)

                    # Refresh the list of card names after deletion
                    card_names = refresh_card_names()
                    # Re-render the selectbox with updated options
                    st.experimental_rerun()
                except Exception as e:
                    # Catch specific exceptions to provide better error handling and debugging
                    st.warning(f"An error occurred: {e}")
    with tab2:
        st.markdown("### View Remaining Information")
        mycursor.execute("SELECT card_holder_name,designation, email, company, phone_number, website, area, city, pincode, state FROM card_information")
        updated_data = mycursor.fetchall()
        df_updated_data = pd.DataFrame(updated_data, 
            columns=["card_holder_name","designation","email","company","phone_number","website","area", "city","pincode","state"])
        st.write(df_updated_data)
