
import streamlit as st
import pandas as pd
import zipfile
import filetype
from PIL import Image
import os
from natsort import natsorted

st.set_page_config(
    page_title="S.I.C",
    page_icon="🧠",
    layout="wide"
)

def Home():
    st.write("# Welcome to S.I.C (Segmented Image Compression)")
    st.markdown(
        """
        This is a front end web-app that allows you to upload zipped image datasets and have them undergo segmentation and compression
        ** 👈 Learn more about the project and try our demo with the sidebar**
        """
    )

def Demo():

    dir_len = 100
    img_index = 0


    st.write("# Segmented Image Compression Demo 🧠")
    st.markdown(
    """
        
        ### Start by uploading your **zipped** dataset. 
        ### Use the slider to navigate through your dataset
    """
    )

    file_uploaded = st.file_uploader("Upload", type=["png","jpg","jpeg", "zip"], 
    accept_multiple_files=True,)



    if len(file_uploaded) > 0:
        for file in file_uploaded:
            # If zip file, extract contents
            if file.type == "application/x-zip-compressed":
                    
                    new_dir = "NewDir"
                    path = os.path.join(os.getcwd(), new_dir)
                    st.write("Directory Path",  path)

                    with zipfile.ZipFile(file, "r") as z:
                        z.extractall(path)

            else:
                    test=Image.open(file)
                    st.image(test)

    if len(file_uploaded) > 0:
        img_list = os.listdir(path)
        img_list = natsorted(img_list)

        dir_len = len(img_list)
        img_index = st.slider('Image Index', 1, dir_len, 1)
        st.write("Image Number ",  img_index)
        img_path = path + "\\"+   img_list[img_index - 1]

        #for img in range(len(img_list)):
        #  st.write("Image ", (img + 1) , ": ", img_list[img] )
        #C:\Users\navaa\NewDir\1.png


        col1, col2 = st.columns(2)

        cur_img =Image.open(img_path)    
        col1.header("Original Image"+ "\n" + img_path)
        col1.image(cur_img, use_column_width=True)

        col2.header("Compressed Image"+ "\n" + img_path)
        col2.image(cur_img, use_column_width=True)
            


page_names_to_funcs = {
    "Home": Home,
    "Demo": Demo,
}

st.sidebar.success("Select a page")
demo_name = st.sidebar.selectbox("", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
