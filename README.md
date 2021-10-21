### Student performance evaluation 
Developed a website to analyze and generate report of students based on the curriculum that represents student’s academic performance. We have developed the system such that, it will automatically parse data onto the database from excel file, which will in return reduce time consumption of analysis of data.

###Data preprocessing
After completing the template, proceed to the "Process data" functionality using the left navigational pane. This function will guide you through processing the prepared dataset, and allow you to update any mislabelled data. If your uploaded dataset did not include the optional Student Info sheet, you will also need to annotate all students in the cohort. From here, you may also download the compiled Student Info data to include during subsequent analyses.<br>

After completing each of the annotation steps, a summary of the dataset parameters is shown including the total number of students identified, number of tracked students in the class and number of students lacking gender annotations. It is recommended to ensure no students are lacking annotations before proceeding, as they will otherwise not contribute to the class and cohort statistics. Once satisfied with the analyses, click submit to finalise the data upload process. Optionally, you may download a clean and processed version of the dataset which can be reuploaded to repeat any subsequent analysis steps.<br>


# Diabetes Prediction App [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/vijeta-2000/student-permormance-evaluation/main/app.py)
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

## Summary
This repository acts as a guide to [this blog post] where I talk about how I use Streamlit to build Machine Learning Applications quickly. Here we use a real-world example of predicting if a patient has diabetes and built a machine learning model. A Streamlit App was then built using a step-by-step approach in this project.

## Acknowledgements
  
[Streamlit](https://www.streamlit.io/), for the open-source library for rapid prototyping.



###Preview
##Home page
![dashboard Screenshot ](https://user-images.githubusercontent.com/65402647/138237115-207e0c28-df3c-4e1c-8a85-07bc574b80ee.jpg)

##UPLOAD DATASET
![Screenshot 2](https://user-images.githubusercontent.com/65402647/138237262-da5900d7-0b78-4da8-9301-917a809651af.jpg)

##Preview updated dataset
![preview updated dataset Screenshot ](https://user-images.githubusercontent.com/65402647/138237339-b79ba500-bc21-4f33-86f7-9d25353c7e1f.jpg)


##Academic analysis
![academic analysis 2Screenshot](https://user-images.githubusercontent.com/65402647/138237382-ad02b144-677a-43aa-bb48-ca174a643a28.jpg)

## To deploy the app do the following steps

Go to <a href = "https://share.streamlit.io">Streamlit Login Page</a> and create an account threre through your github login. Then you will have to request for an invite that will allow you to share your applications using Streamlit Share. You will get a confirmation mail with the invite in 48 hours.

<br>

Now you have to create a `requirements.txt` file that will let **Streamlit** know which packages you are using for your application. To do this:

1. Install pipreqs using `pip install pipreqs`.
2. Then you have to run `pipreqs <location of your project folder>`. If you have installed pipreqs in your project folder itself run `pipreqs ./`. Now wait for a minute and check whether you have a requirements.txt file in your folder. If yes, then you are good to deploy the app, else you can search for the problem solution on Google or reach out to me on <a href = "https://www.linkedin.com/in/vedanthbaliga">LinkedIn</a>

3. Now go back to the <a href="https://streamlit.io/">Streamlit</a> webiste and click **New App**
4. Choose your project repository from the dropdown menu, select either main or master and select the file that you want to deploy. In this case `app.py`.
5. Now Click deploy and wait till the processing of the app is finished.
6. Once you can see the contents of your app, you can use the URL and share it with your friends 😊

If you liked this repo and the Study Jam Webinar, considering giving the repo a **star**!
