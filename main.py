from fastapi import FastAPI, Request, Form, APIRouter, Depends,File, UploadFile
from enum import Enum

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import shutil
from barcode.writer import ImageWriter

from barcode import EAN13,EAN8
from barcode.writer import ImageWriter
from io import BytesIO
import fitz

import barcode
import time
import subprocess
import json

from woocommerce import API


app = FastAPI()
Orientation = Enum("Orientation", names={"portrait":"portrait", "landscape": "landscape"})

wcapi = API(
    url="http://192.168.1.7/wordpress",
    consumer_key="ck_f74054203789fdccbdfcd52b84242ca905b78d69",
    consumer_secret="cs_0a9eb41cc56c62db8501006845982d1edcf65be6",
    version="wc/v3"
)

cat=wcapi.get("products/categories")
content=json.loads(cat.text)
cat={}
cat_reverse={}
for cc in content:
    cat[str(cc["id"])]=cc["slug"]
    cat_reverse[str(cc["slug"])]=cc["id"]

print(cat,"==========")

Modules = Enum("Modules", names=cat)


@app.post("/upload")

async def create_file(Modules: Modules = Form(...),Orientation: Orientation = Form(...),file: UploadFile = File(...)):

    # id_=cat_reverse[Modules]
    mod=str(Modules).split(".")[1]
    
    img_file_name="./code_bare/"+str(time.time()).replace(".","")+".jpeg"




    global upload_folder
    # try:
        
    upload_resume_path="upload_origin"

    upload_before_trt_path="upload_befor_trt"
    upload_trt_path="upload_trt"

    upload_odd_path="upload_odd"
    upload_even_path="upload_even"



    



    

    file_object = file.file
    filename=file.filename

    path_filename=os.path.join(os.getcwd(),upload_resume_path, filename)
    


    upload_resume = open(path_filename, 'wb+')
    shutil.copyfileobj(file_object, upload_resume)
    upload_resume.close()




    orient=str(Orientation).split(".")[1]
    title=(file.filename).split(".")[0]
    if (orient=="landscape"):
        subprocess.run(["pdfjam","--landscape","--outfile", path_filename,"--paper","a4paper",path_filename])
        document = fitz.open(path_filename)
        page = document[0]


        page_count=document.pageCount
        RegularPrice=page_count*4

        # if(page)
        # page__ = document.loadPage(0)  
        # pix = page.get_pixmap()

        # img_name1=str(time.time()).replace(".","_")+".jpg"
        # pix.save(f"/mnt/c/Bitnami/wordpress-5.8.2-0/apps/wordpress/htdocs/wp-content/uploads/photo/{img_name1}")
        # img_url="http://192.168.1.7/wordpress/wp-content/uploads/w_photo/"+img_name1

        body={"name": title,
              "type": "simple",
              "regular_price": str(RegularPrice),
              "categories": [
                {
                  "id": mod
                }
              ],
            #   "images": [
            #     {
            #       "src": img_url
            #     }
            #   ],
              
              "attributes":[{
                  "name":"pages",
                  "options":str(page_count),
                  "visible":True
                  }],
            
            }

        response=wcapi.post("products",body)


        product_id=json.loads(response.text)["id"]
        code ="{:08d}".format(int(product_id))

        with open(img_file_name, 'wb') as f:
            EAN8(str(code), writer=ImageWriter()).write(f)

        path_trt=os.path.join(os.getcwd(),upload_trt_path, str(product_id)+".pdf")
        path_odd=os.path.join(os.getcwd(),upload_odd_path, str(product_id)+".pdf")
        path_even=os.path.join(os.getcwd(),upload_even_path, str(product_id)+".pdf")
        path_before_trt_path=os.path.join(os.getcwd(),upload_before_trt_path, str(product_id)+".pdf") 




        img_rect = fitz.Rect(0, 0, 100, 50)


        page.insertImage(img_rect, filename=img_file_name)
        document.save(path_trt)
        document.close()

        upload_resume = open(path_before_trt_path, 'wb+')
        shutil.copyfileobj(file_object, upload_resume)
        upload_resume.close()

        subprocess.run(["pdftk",path_trt,"cat","1-endodd","output", path_odd])
        subprocess.run(["pdfjam","--outfile", path_odd,"--paper","a4paper",path_odd,"--angle","90"])

        subprocess.run(["pdftk",path_trt,"cat","1-endeven","output", path_even])
        subprocess.run(["pdfjam","--outfile", path_even,"--paper","a4paper",path_even,"--angle","270"])

    elif (orient=="portrait"):
        subprocess.run(["pdfjam","--outfile", path_filename,"--paper","a4paper",path_filename])

        document = fitz.open(path_filename)
        page = document[0]
        img_rect = fitz.Rect(0,760, 100, 840)
        # document = fitz.open(path_filename)
        # page = document[0]


        page_count=document.pageCount
        RegularPrice=page_count*4

        # if(page)
        # page__ = document.loadPage(0)  
        # pix = page.get_pixmap()

        # img_name1=str(time.time()).replace(".","_")+".jpg"
        # pix.save(f"/mnt/c/Bitnami/wordpress-5.8.2-0/apps/wordpress/htdocs/wp-content/uploads/photo/{img_name1}")
        # img_url="http://192.168.1.7/wordpress/wp-content/uploads/w_photo/"+img_name1

        body={"name": title,
              "type": "simple",
              "regular_price": str(RegularPrice),
              "categories": [
                {
                  "id": mod
                }
              ],
            #   "images": [
            #     {
            #       "src": img_url
            #     }
            #   ],
              
              "attributes":[{
                  "name":"pages",
                  "options":str(page_count),
                  "visible":True
                  }],
            
            }

        response=wcapi.post("products",body)

        product_id=json.loads(response.text)["id"]

        code ="{:08d}".format(int(product_id))

        with open(img_file_name, 'wb') as f:
            EAN8(str(code), writer=ImageWriter()).write(f)

        path_trt=os.path.join(os.getcwd(),upload_trt_path, str(product_id)+".pdf")
        path_odd=os.path.join(os.getcwd(),upload_odd_path, str(product_id)+".pdf")
        path_even=os.path.join(os.getcwd(),upload_even_path, str(product_id)+".pdf")
        path_before_trt_path=os.path.join(os.getcwd(),upload_before_trt_path, str(product_id)+".pdf") 




        


        page.insertImage(img_rect, filename=img_file_name)
        document.save(path_trt)
        document.close()


        upload_resume = open(path_before_trt_path, 'wb+')
        shutil.copyfileobj(file_object, upload_resume)
        upload_resume.close()


        subprocess.run(["pdftk",path_trt,"cat","1-endodd","output", path_odd])
        subprocess.run(["pdfjam","--outfile", path_odd,"--paper","a4paper",path_odd])

        subprocess.run(["pdftk",path_trt,"cat","1-endeven","output", path_even])
        subprocess.run(["pdfjam","--outfile", path_even,"--paper","a4paper",path_even])




    return "ssssss"+str(product_id)



