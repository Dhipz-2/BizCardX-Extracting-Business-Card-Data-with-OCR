import easyocr
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import psycopg2
import PIL
from PIL import ImageDraw


#Theme
base="light"
primaryColor="#79583c"
secondaryBackgroundColor="#ceaf98"
textColor="#79583c"
font="serif"


hostname = 'localhost'
database = 'Bizcard_db'
username = 'postgres'
pwd = ''
port_id = 5432

conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port = port_id
)

cur = conn.cursor()

def draw_boxes(image, bounds, color='brown', width=2):
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
    return image

st.set_page_config(layout="wide")
st.title("BizCardX: Extracting Business Card Data with OCR")
page_bg_img = """
<style>
[data-testid="stAppViewContainer"]>.main{
    background-image: url("https://wallpapers.com/images/hd/modern-aesthetic-ntgi03d8sg79i510.jpg");
    background-size: 100%;
    background-position: top left;
    background-repeat: no-repeat;
    background-attachment: local;
}
<style>
"""
#https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/rm422-063.jpg?w=800&dpr=1&fit=default&crop=default&q=65&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.2.1&s=fbf4e88d3cd5a054182e2b9ae5d64109
#https://images.unsplash.com/photo-1606767041004-6b918abe92be?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTV8fGJyb3duJTIwYmFja2dyb3VuZHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=600&q=60
#https://marketplace.canva.com/EAFsJ6z_sfU/1/0/900w/canva-brown-aesthetic-phone-wallpaper-yCLkj2dHeh0.jpg

st.markdown(page_bg_img, unsafe_allow_html=True)

selected = option_menu(
    menu_title =None,
    options = ["Home","Upload and Extract",'Alter and Delete'],
    icons = ['house-check','upload','pencil-square'],
    default_index=0,
    orientation = 'horizontal'
)

if selected=='Home':
    c3, c4 = st.columns(2)
    with c4:
        i = PIL.Image.open(r"C:\Users\Dhipika\Downloads\card_img.jpg")
        st.image(i)
    with c3:
        st.subheader("Bizcard's objective is to develop an interactive Streamlit application enabling users to upload images of business cards and seamlessly extract pertinent information from them using the EasyOCR Python library, which excels in Optical Character Recognition (OCR). The application not only facilitates the extraction process but also empowers users to preserve the extracted data in a database, coupled with the original business card image")
        st.subheader("Furthermore, Bizcard offers a user-friendly Streamlit interface for reading, updating, and deleting the stored data, thus providing a comprehensive solution for managing business card information effectively.")

elif selected=='Upload and Extract':
    reader = easyocr.Reader(['en'], gpu = False)
    c1,c2 = st.columns(2)
    with c1:
        uploaded_file = st.file_uploader("Choose a file")
        button = st.button("Click here to extract and store the information")
        #b1 = st.button("CLick here to store the data in database")

    if uploaded_file:

        img = PIL.Image.open(uploaded_file)
        bounds = reader.readtext(fr"C:\Users\Dhipika\OneDrive\Desktop\streamlit\Bizcard\{uploaded_file.name}")

        col1, col2 = st.columns(2)
        if uploaded_file.name=='1.png':

            if button:
                with col1:
                    st.subheader("Uploaded image")
                    st.image(img)
                
                with col2:
                    st.subheader("Processed image")
                    draw_img = draw_boxes(img, bounds)
                    st.image(draw_img)
            
                l1=[]
                for i in bounds:
                    l1.append(i[1])
                a = l1[6].split(',')
                b = l1[8].split(' ')

                df = dict(Company_name = str((l1[7]+" "+l1[9]).capitalize()),
                        Card_holder_name = str(l1[0]),
                        Designation = str(l1[1]),
                        Mobile_number = str(l1[2]+','+l1[3]),
                        Email = str(l1[5]),
                        Website = str(l1[4]),
                        Area = str(a[0]),
                        City = str(a[1][0:8]),
                        State = str(b[0]),
                        Pincode = str(b[1]))
            
                df1 = pd.DataFrame(df,index=[0]).reset_index(drop=True)
                st.dataframe(df1)
                df1 = df1.values.tolist()
                create_script1 = '''CREATE TABLE IF NOT EXISTS Bizcard(
                company_name varchar(40),
                card_holder_name varchar(40),
                designation varchar(40),
                mobile_no varchar(40),
                email varchar(40),
                website_url varchar(40),
                area varchar(50),
                city varchar(15),
                state varchar(15),
                pincode varchar(10)
                )'''
                cur.execute(create_script1)
                cur.executemany('INSERT INTO Bizcard VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', df1)
                st.success("Uploaded the data successfully!")

        elif uploaded_file.name=='2.png':

            if button:
                with col1:
                    st.subheader("Uploaded image")
                    st.image(img)
                
                with col2:
                    st.subheader("Processed image")
                    draw_img = draw_boxes(img, bounds)
                    st.image(draw_img)

                    l1=[]
                    for i in bounds:
                        l1.append(i[1])
                        #st.write(i[1])
                    b = l1[9].split(' ')

                    df = dict(Company_name = str((l1[8]+" "+l1[10]).capitalize()),
                            Card_holder_name = str(l1[0]),
                            Designation = str(l1[1]),
                            Mobile_number = str(l1[2]),
                            Email = str(l1[3]),
                            Website = str(l1[4]+'.'+l1[5]),
                            Area = str(l1[6]),
                            City = str(l1[7][0:5]),
                            State = str(b[0]),
                            Pincode = str(b[1]))
                    
                df2 = pd.DataFrame(df,index=[0]).reset_index(drop=True)
                st.dataframe(df2)
                df2 = df2.values.tolist()
                create_script1 = '''CREATE TABLE IF NOT EXISTS Bizcard(
                company_name varchar(40),
                card_holder_name varchar(40),
                designation varchar(40),
                mobile_no varchar(40),
                email varchar(40),
                website_url varchar(40),
                area varchar(50),
                city varchar(15),
                state varchar(15),
                pincode varchar(10)
                )'''
                cur.execute(create_script1)
                cur.executemany('INSERT INTO Bizcard VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', df2)
                st.success("Uploaded the data successfully!")

        elif uploaded_file.name=='3.png':

            if button:
                with col1:
                    st.subheader("Uploaded image")
                    st.image(img)
                
                with col2:
                    st.subheader("Processed image")
                    draw_img = draw_boxes(img, bounds)
                    st.image(draw_img)

                    l1=[]
                    for i in bounds:
                        l1.append(i[1])
                        #st.write(i[1])
                    a = l1[3].split(" ")
                    b = l1[2].split(',')

                    df = dict(Company_name = str((l1[7]+" "+l1[8]).capitalize()),
                            Card_holder_name = str(l1[0]),
                            Designation = str(l1[1]),
                            Mobile_number = str(l1[4]),
                            Email = str(l1[5]),
                            Website = str(l1[6]),
                            Area = str(b[0]),
                            City = str(b[1]),
                            State = str(a[0]),
                            Pincode = str(a[1]))
                    
                df3 = pd.DataFrame(df,index=[0]).reset_index(drop=True)
                st.dataframe(df3)
                df3 = df3.values.tolist()
                create_script1 = '''CREATE TABLE IF NOT EXISTS Bizcard(
                company_name varchar(40),
                card_holder_name varchar(40),
                designation varchar(40),
                mobile_no varchar(40),
                email varchar(40),
                website_url varchar(40),
                area varchar(50),
                city varchar(15),
                state varchar(15),
                pincode varchar(10)
                )'''
                cur.execute(create_script1)
                cur.executemany('INSERT INTO Bizcard VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', df3)
                st.success("Uploaded the data successfully!")

        elif uploaded_file.name=='4.png':

            if button:
                with col1:
                    st.subheader("Uploaded image")
                    st.image(img)
                
                with col2:
                    st.subheader("Processed image")
                    draw_img = draw_boxes(img, bounds)
                    st.image(draw_img)

                    l1=[]
                    for i in bounds:
                        l1.append(i[1])
                        #st.write(i[1])
                    b = l1[2].split(',')

                    df = dict(Company_name = str((l1[6]+" "+l1[8]).capitalize()),
                            Card_holder_name = str(l1[0]),
                            Designation = str(l1[1]),
                            Mobile_number = str(l1[4]),
                            Email = str(l1[5]),
                            Website = str(l1[7]),
                            Area = str(b[0]),
                            City = str(b[2]),
                            State = str(b[3][:-1]),
                            Pincode = str(l1[3]))
                    
                df4 = pd.DataFrame(df,index=[0]).reset_index(drop=True)
                st.dataframe(df4)
                df4 = df4.values.tolist()
                create_script1 = '''CREATE TABLE IF NOT EXISTS Bizcard(
                company_name varchar(40),
                card_holder_name varchar(40),
                designation varchar(40),
                mobile_no varchar(40),
                email varchar(40),
                website_url varchar(40),
                area varchar(50),
                city varchar(15),
                state varchar(15),
                pincode varchar(10)
                )'''
                cur.execute(create_script1)
                cur.executemany('INSERT INTO Bizcard VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', df4)
                st.success("Uploaded the data successfully!")

        elif uploaded_file.name=='5.png':

            if button:
                with col1:
                    st.subheader("Uploaded image")
                    st.image(img)
                
                with col2:
                    st.subheader("Processed image")
                    draw_img = draw_boxes(img, bounds)
                    st.image(draw_img)

                    l1=[]
                    for i in bounds:
                        l1.append(i[1])
                        #st.write(i[1])
                    a = l1[2].split(',')
                    b = a[1].split(';')

                    df = dict(Company_name = str(l1[7].capitalize()),
                            Card_holder_name = str(l1[0]),
                            Designation = str(l1[1]),
                            Mobile_number = str(l1[4]),
                            Email = str(l1[5]),
                            Website = str(l1[6]),
                            Area = str(a[0]),
                            City = str(b[0]),
                            State = str(b[1]),
                            Pincode = str(l1[3]))
                
                df5 = pd.DataFrame(df,index=[0]).reset_index(drop=True)
                st.dataframe(df5)
                df5 = df5.values.tolist()
                create_script1 = '''CREATE TABLE IF NOT EXISTS Bizcard(
                company_name varchar(40),
                card_holder_name varchar(40),
                designation varchar(40),
                mobile_no varchar(40),
                email varchar(40),
                website_url varchar(40),
                area varchar(50),
                city varchar(15),
                state varchar(15),
                pincode varchar(10)
                )'''
                cur.execute(create_script1)
                cur.executemany('INSERT INTO Bizcard VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', df5)
                st.success("Uploaded the data successfully!")

elif selected=='Alter and Delete':
    radio = st.radio("**Select the below option to alter or delete the data**",("Alter","Delete"))
    c5, c6 = st.columns(2)
    
    if radio=='Alter':
        with c5:
            option = st.selectbox(
                '**Select a card by its company name**',
                ('Select','Selva digitals', 'Global insurance', 'Borcelle airlines','Family restaurant','Sun electricals'),key='abc')
        if option:
            st.subheader("Before Updation")    
            cur.execute(f"select * from Bizcard where company_name='{option}';")
            sql1 = cur.fetchall()
            df1 = pd.DataFrame(sql1, columns=['company_name',
                'card_holder_name',
                'designation',
                'mobile_no',
                'email',
                'website_url',
                'area',
                'city',
                'state',
                'pincode']).reset_index(drop=True)
            st.dataframe(df1)
            c7,c8 = st.columns(2)
            with c7:
                select = st.selectbox("**Select any data from below option to alter the data**",
                                    ('company_name','card_holder_name','designation','mobile_no','email','website_url','area','city','state','pincode'))
                input = st.text_input("Type here")
                update = st.button("Click here to update the data")
            if update:
                cur.execute(f"update Bizcard set {select} = '{input}' where company_name='{option}';")
                st.subheader("After Updation")
                cur.execute(f"select * from Bizcard where company_name='{option}';")
                sql1 = cur.fetchall()
                df11 = pd.DataFrame(sql1, columns=['company_name',
                    'card_holder_name',
                    'designation',
                    'mobile_no',
                    'email',
                    'website_url',
                    'area',
                    'city',
                    'state',
                    'pincode']).reset_index(drop=True)
                st.dataframe(df11)
                st.success("Updated the data successfully!")
    elif radio=='Delete':
        with c5:
            option = st.selectbox(
                'Select a card by its company name',
                ('Select','Selva digitals', 'Global insurance', 'Borcelle airlines','Family restaurant','Sun electricals'),key='abc')
        st.subheader("Before Deletion")
        cur.execute(f"select * from Bizcard;")
        sql1 = cur.fetchall()
        df11 = pd.DataFrame(sql1, columns=['company_name',
            'card_holder_name',
            'designation',
            'mobile_no',
            'email',
            'website_url',
            'area',
            'city',
            'state',
            'pincode']).reset_index(drop=True)
        st.dataframe(df11)
        
        if option:
            cur.execute(f"delete from Bizcard where company_name='{option}';")
            st.subheader("After Deletion")
            cur.execute(f"select * from Bizcard;")
            sql1 = cur.fetchall()
            df11 = pd.DataFrame(sql1, columns=['company_name',
                'card_holder_name',
                'designation',
                'mobile_no',
                'email',
                'website_url',
                'area',
                'city',
                'state',
                'pincode']).reset_index(drop=True)
            st.dataframe(df11)
            st.success("Deleted the data successfully!")



conn.commit()
conn.close()
