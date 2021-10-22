# Student performance evaluation 
Developed a website to analyze and generate report of students based on the curriculum that represents student’s academic performance. We have developed the system such that, it will automatically parse data onto the database from excel file, which will in return reduce time consumption of analysis of data.

# Data preprocessing
After completing the template, proceed to the "Process data" functionality using the left navigational pane. This function will guide you through processing the prepared dataset, and allow you to update any mislabelled data. If your uploaded dataset did not include the optional Student Info sheet, you will also need to annotate all students in the cohort. From here, you may also download the compiled Student Info data to include during subsequent analyses.<br>

After completing each of the annotation steps, a summary of the dataset parameters is shown including the total number of students identified, number of tracked students in the class and number of students lacking gender annotations. It is recommended to ensure no students are lacking annotations before proceeding, as they will otherwise not contribute to the class and cohort statistics. Once satisfied with the analyses, click submit to finalise the data upload process. Optionally, you may download a clean and processed version of the dataset which can be reuploaded to repeat any subsequent analysis steps.<br>


# Student performance Analyser
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/vijeta-2000/student-permormance-evaluation/main/app.py)
Streamlit Web App to predict Student performance evaluation . 

## Pre-requisites

The project was developed using python 3.6.7 with the following packages.
- streamlit
- pandas
- numpy
- matplotlib
- seaborn
- zipp
- pillow
- numpy
- pandas
- loguru
- names
- xlrd
- xlsxwriter
- openpyxl

Installation with pip:

```bash
pip install -r requirements.txt
```

## Getting Started
Open the terminal in you machine and run the following command to access the web application in your localhost.
```bash
streamlit run app.py
```

## Files
- app.py : Streamlit App script
- requirements.txt : pre-requiste libraries for the project

## Acknowledgements
  
[Streamlit](https://www.streamlit.io/), for the open-source library for rapid prototyping.

## Made with [Python](https://www.python.org/) 

### Preview

## Home page
![dashboard Screenshot ](https://user-images.githubusercontent.com/65402647/138237115-207e0c28-df3c-4e1c-8a85-07bc574b80ee.jpg)

## UPLOAD DATASET
![Screenshot 2](https://user-images.githubusercontent.com/65402647/138237262-da5900d7-0b78-4da8-9301-917a809651af.jpg)

## Preview updated dataset
![preview updated dataset Screenshot ](https://user-images.githubusercontent.com/65402647/138237339-b79ba500-bc21-4f33-86f7-9d25353c7e1f.jpg)


## Academic analysis
![academic analysis 2Screenshot](https://user-images.githubusercontent.com/65402647/138237382-ad02b144-677a-43aa-bb48-ca174a643a28.jpg)


If you liked this repo , considering giving the repo a **star**!😊


