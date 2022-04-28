import os, re
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from collections import defaultdict
import src.hierarchical_axes as ha
import zipfile
import io
from PIL import Image


from src import SessionState  # Assuming SessionState.py lives on this folder

# remove uploader warning
st.set_option('deprecation.showfileUploaderEncoding', False)

# get states from this session, to enable button functionality
state = SessionState.get()

# Download a single file and make its content available as a string.
def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/streamlit/demo-self-driving/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """

    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    
    # some strings <-> bytes conversions necessary here
    if isinstance(object_to_download, bytes):
        b64 = base64.b64encode(object_to_download).decode()
    else:
        b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def df_to_excel_bytes(df_dict):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for sheet_name, df in df_dict.items():
        df.to_excel(writer, sheet_name=sheet_name)
    writer.save()
    return output.getvalue()


def upload_dataset():

    data_file = st.file_uploader("To begin, please upload your prepared dataset.",type=['xlsx', 'xls'])
    if data_file is None:
        return False    

    data = pd.read_excel(data_file, sheet_name=None, engine='openpyxl')
    state.data_path = data_file

    return data    


def validate_data(data):
    

    # -----Capture sheetnames, assign data type, year, info-----
    data_preview = st.beta_expander("Preview uploaded dataset", expanded=False)
    with data_preview:       
        sheet_name = st.selectbox("Select sheet to preview.", list(data.keys()))
        st.dataframe(data[sheet_name].dropna(how='all'))

    # -----Check extracted year, grade, task info is correct-----
    sheet_names = data.keys()

    # Categorise sheet names, extract important info
    sheet_types = defaultdict(list)
    for sheet_name in sheet_names:
        if 'wellbeing' in sheet_name.lower():
            sheet_types['wellbeing'].append(sheet_name)
        elif 'grades' in sheet_name.lower():
            sheet_types['grades'].append(sheet_name)
        elif 'student info' in sheet_name.lower():
            student_info = data[sheet_name]
        elif 'students to track' in sheet_name.lower():
            students_to_track = data[sheet_name]
        else:
            sheet_types['unknown'].append(sheet_name)

    students_to_annotate = []
    if 'grades' in sheet_types:
        grade_validation = st.beta_expander("Validate academic score labels", expanded=False)
        with grade_validation:
        # present validation options
            st.markdown('The following sheetnames were detected to contain academic scores. \nPlease confirm the extracted metadata about each set of task scores:')
            task_names = []
            for sheet_name in sheet_types['grades']:
                students_to_annotate.append(data[sheet_name][['Student Id', 'Surname', 'First Name']])
                st.write(f'**{sheet_name}**')
                col1, col2, col3 = st.beta_columns(3)
                _, year = [x.strip('') for x in sheet_name.split(' ')]
                year = col1.text_input(f"Year", year, key=f'{sheet_name}_year')
                task_cols = [col for col in data[sheet_name].keys() if 'task' in col.lower()]
                for task in task_cols:
                    task_number = col2.text_input(f"Task number", task.split(' ')[1], key=f'{year}_{task}_number')
                    task_maximum = col3.text_input(f"Task maximum", task.split('/')[-1], key=f'{year}_{task}_max')
                    data[sheet_name].rename(columns={task: f'Task {task_number} total / {task_maximum}'}, inplace=True)
                    task_names.append([f'Grades {year}', year, f'Task {task_number} total / {task_maximum}', task_number, task_maximum])
                data[f'Grades {year}'] = data.pop(sheet_name)
            task_names = pd.DataFrame(task_names, columns=['Sheet name', 'Year', 'Column name', 'Task number', 'Maximum score'])
        # compile students from all task sheets for annotation
        students_to_annotate = pd.concat(students_to_annotate).drop_duplicates()

        # -----check for student info, assigned tracked students-----
        Gender_assignment = st.beta_expander("Assign student identifiers", expanded=False)
        with Gender_assignment:
            # prepare data
            students_to_annotate['Full Name'] = students_to_annotate['First Name'] + ' ' + students_to_annotate['Surname']
            Genders = {}
            if 'student info' in [x.lower() for x in sheet_names]:
                # if student info sheet exists, collect existing Gender annotations
                Genders = data['Student Info'].copy().dropna(how='all')
                Genders = dict(Genders[['Student Id', 'Gender']].values)

            students_to_track = []
            trackers = {}
            if 'Students to Track' in sheet_names:
                data['Students to Track']['Full Name'] = data['Students to Track']['First Name'] + ' ' + data['Students to Track']['Surname']
                for student in data['Students to Track']['Student Id'].tolist():
                    students_to_track.append(student)

            # Collect annotations
            st.markdown('Please confirm all student Gender annotations, and select which students to track using the left checkbox')
            col1, col2, col3 = st.beta_columns([2, 0.5, 0.5])
            for index, student in students_to_annotate.drop_duplicates().iterrows():
                student_id = student['Student Id']
                if student_id in students_to_track:
                    tracked = col1.checkbox(f"{student['Full Name']}", value=True, key=f'{student_id}_track')
                else:
                    tracked = col1.checkbox(f"{student['Full Name']}", value=False, key=f'{student_id}_track')
                trackers[student_id] = 1 if tracked else 0
                if student_id in Genders:
                    if Genders[student_id] == 'M':
                        m = True
                        f = False
                    elif Genders[student_id] == 'F':
                        m = False
                        f = True
                else:
                    m = False
                    f = False
                Gender_M = col2.checkbox('M', value=m, key=f'{student_id}_M')
                Gender_F = col3.checkbox('F', value=f, key=f'{student_id}_F')
                if Gender_M:
                    Genders[student_id] = 'M'
                if Gender_F:
                    Genders[student_id] = 'F'

            students_to_annotate['Gender'] = students_to_annotate['Student Id'].map(Genders)
            students_to_annotate['tracked'] = students_to_annotate['Student Id'].map(trackers)

            data['Student Info'] = students_to_annotate

    if 'wellbeing' in sheet_types:
        wellbeing_validation = st.beta_expander("Validate wellbeing labels", expanded=False)
        with wellbeing_validation:
            st.markdown('The following sheetnames were detected to contain wellbeing scores:')
            st.write(', '.join(sheet_types['wellbeing']))
            for sheet_name in sheet_types['wellbeing']:
                students_to_annotate.append(data[sheet_name][['Student Id', 'Surname', 'First Name']])

            wellbeing = []
            for sheet in sheet_types['wellbeing']:
                df = data[sheet].copy()
                df.dropna(inplace=True, how='all')
                df['year'] = int(sheet.split(' ')[-1])
                wellbeing.append(df)
            wellbeing = pd.concat(wellbeing)
            st.dataframe(wellbeing)

            data['wb_summary'] = wellbeing

    summary = st.beta_expander("Dataset Summary & Download", expanded=True)
    with summary:
        if 'unknown' in sheet_types:
            st.markdown('**The following sheetnames were not recognised and were not be processed**:')
            st.write(f"*{', '.join(sheet_types['unknown'])}*")

        # preview student info
        st.markdown(f"**Total number of students**: {len(data['Student Info'])}")
        st.markdown(f"**Number of tracked students**: {len(data['Student Info'][data['Student Info']['tracked'] == 1])}")
        st.markdown(f"**Students with unknown gender**: {len(data['Student Info'][data['Student Info']['Gender'].isnull()])}")

        if 'grades' in sheet_types:
            # preview task info
            data['task_names'] = task_names
            st.markdown("**Academic score summary**")
            st.dataframe(task_names[['Year', 'Task number', 'Maximum score']])

        col1, col2 = st.beta_columns(2)
        if col1.button("Download compiled dataset"):
            tmp_download_link = download_link(df_to_excel_bytes(data), 'compiled_data.xlsx', 'Click here to download!')
            col1.markdown(tmp_download_link, unsafe_allow_html=True)

        if col2.button('Download Student Information'):
            tmp_download_link = download_link(data['Student Info'], 'student_info.csv', 'Click here to download!')
            col2.markdown(tmp_download_link, unsafe_allow_html=True)

    return data


def summarise_dataset(data):
    # get all task columns, if not % scale to 100
    task_names = data['task_names']
    task_names['Maximum score'] = task_names['Maximum score'].astype(int)
    task_data = []
    for sheet_name, dataframe in task_names.groupby(['Sheet name']):
        year_data = data[sheet_name].copy()
        for col_name, df in dataframe.groupby(['Column name']):
            if df['Maximum score'].tolist()[0] != 100:
                year_data[col_name] = year_data[col_name] / df['Maximum score'].tolist()[0] * 100
            year_data[col_name] = year_data[col_name].astype(float)
            year_data.rename(columns={col_name: f"Task {df['Task number'].tolist()[0]}"}, inplace=True)
        year_data['Year'] = df['Year'].astype(int).tolist()[0]
        task_data.append(year_data)
    
    tasks = pd.concat(task_data)
    tasks = pd.melt(
        tasks, 
        id_vars=['Student Id', 'First Name', 'Surname', 'Year'],
        value_vars=[col for col in tasks.columns.tolist() if 'Task' in col],
        var_name='Task',
        value_name='score'
    )
    tasks['Task'] = tasks['Task'].str.split(' ').str[-1].astype(int)
    tasks['Full Name'] = tasks['First Name'] + ' ' + tasks['Surname']
    # get student_info and apply Gender, tracked ids
    student_info = data['Student Info']
    tasks['Gender'] = tasks['Student Id'].map(dict(student_info[['Student Id', 'Gender']].values))
    tasks['Tracked'] = tasks['Student Id'].map(dict(student_info[['Student Id', 'tracked']].values))
    
    data['task_summary'] = tasks

    # summarise wellbeing data
    wellbeing = data['wb_summary']
    
    id_cols = ['Student Id', 'Surname', 'First Name', 'year', 'Term']

    wellbeing = pd.melt(
        wellbeing, 
        id_vars=id_cols, 
        value_vars=['Whole School', 'Negatives English', 'Positives English'],
        var_name='type', 
        value_name='count')

    wellbeing.dropna(subset=['count'], inplace=True)
    wellbeing['Full Name'] = wellbeing['First Name'] + ' ' + wellbeing['Surname']

    type_labels = {0: 'Whole School', 1: 'Positives English', 2: 'Negatives English'}
    wellbeing['type_order'] = wellbeing['type'].map({v: k for k, v in type_labels.items()})

    type_keys = [tuple(key) for key in wellbeing[['year', 'type_order']].sort_values(['type_order', 'year'], ascending=True).drop_duplicates().values.tolist()]
    type_order = dict(zip(type_keys, np.arange(0, len(type_keys))))

    term_keys = [tuple(key) for key in wellbeing[['year', 'Term']].sort_values(['year', 'Term'], ascending=True).drop_duplicates().values.tolist()]
    term_order = dict(zip(term_keys, np.arange(0, len(term_keys))))

    wellbeing['type_position'] = [tuple(x) for x in wellbeing[['year', 'type_order']].values]
    wellbeing['type_position'] = wellbeing['type_position'].map(type_order)
    wellbeing['term_order'] = [tuple(x) for x in wellbeing[['year', 'Term']].values]
    wellbeing['term_order'] = wellbeing['term_order'].map(term_order)

    data['wb_summary'] = wellbeing

    state.data = data

    return data


def zip_images(figures):
    """Saves collection of images to zip file in memory, returns zipfile object for later download.

    Parameters
    ----------
    figures : [dict]
        Dictionary mapping figure_name: figure object.
    """    
    memory_zip = io.BytesIO()
    zf = zipfile.ZipFile(memory_zip, mode="w")
    for fig_name, fig in figures.items():
        buf = io.BytesIO()
        fig.savefig(buf)
        plt.close(fig)
        img_name = f'{fig_name}.png'
        zf.writestr(img_name, buf.getvalue())
    zf.close()
    
    return zf, memory_zip
    

def zip_download(memory_zip, filename):
    # find beginning of file
    memory_zip.seek(0)
    #read the data
    data = memory_zip.read()
    tmp_download_link = download_link(data, f'{filename}.zip', 'Click here to download!')

    return tmp_download_link


def insert_new_line(num=1):
    return [
        st.text("") for i in range(num)
    ]



def generate_introduction():
    st.markdown("# Welcome to the ")
    image = Image.open('utilities/banner.png')
    st.image(image)

    template = pd.read_excel('utilities/template.xlsx', sheet_name=None, engine='openpyxl')
    example = pd.read_excel('utilities/example_data.xlsx', sheet_name=None, engine='openpyxl')
    
    template_link = download_link(df_to_excel_bytes(template), 'template.xlsx', 'template document')
    example_link = download_link(df_to_excel_bytes(template), 'example_data.xlsx', 'example dataset')

    st.markdown(
    f"""
    The PEARS platform provides a set of simple analysis tools to investigate student performance and wellbeing metrics. The outputs are designed to provide a holistic overview of a student's performance compared to their peers.

    ## Instructions

    """)
    getting_started = st.beta_expander("Getting started", expanded=False)
    with getting_started:
        st.markdown(
        f"""
        To get started, it is necessary to compile raw data from students of interest which needs to be preformatted according to the {template_link}. Detailed instructions on preparing the dataset for upload are contained within the template, and should be followed to ensure proper processing of your dataset.

        Alternatively, to explore the app functionality on a fictitious dataset you may download the {example_link} for use in all subsequent steps.
        """, unsafe_allow_html=True)

    process_data_instructions = st.beta_expander("Data preprocessing", expanded=False)
    with process_data_instructions:
        st.markdown(
        f"""
        After completing the template, proceed to the "Process data" functionality using the left navigational pane. This function will guide you through processing the prepared dataset, and allow you to update any mislabelled data. If your uploaded dataset did not include the optional Student Info sheet, you will also need to annotate all students in the cohort. From here, you may also download the compiled Student Info data to include during subsequent analyses. 
        
        After completing each of the annotation steps, a summary of the dataset parameters is shown including the total number of students identified, number of tracked students in the class and number of students lacking gender annotations. It is recommended to ensure no students are lacking annotations before proceeding, as they will otherwise not contribute to the class and cohort statistics. Once satisfied with the analyses, click submit to finalise the data upload process. Optionally, you may download a clean and processed version of the dataset which can be reuploaded to repeat any subsequent analysis steps.
        """, unsafe_allow_html=True)

    analysis_instructions = st.beta_expander("Analysis", expanded=False)
    with analysis_instructions:
        st.markdown(
        f"""
        After preparing the metrics dataset, you may then proceed to the reporting phases. Separate pages are provided to analyse the Grades and Wellbeing datasets, which can be accessed via the navigation pane. If, at any time, you wish to add additional students to the 'tracked' class, you may return to the "Process data" screen and update the Student Identifiers pane by selecting the checkbox next to the student of interest. To assess their metrics, proceed to the Grades or Wellbeing analyses tabs and repeat the plotting processes.
        """, unsafe_allow_html=True)

    download_instructions = st.beta_expander("Download summary graphs", expanded=False)
    with download_instructions:
        st.markdown(
        f"""
        Finally, once satisfied with the plot preview you may proceed to generate the relevant graphs for all tracked students by clicking the "Generate all individual student plots" button. Once completed, a second button will appear to generate the download file, and finally a download link will appear next to this button. Clicking the download link will download the plots as a ".zip" folder, which can be unzipped using standard extraction tools for Windows, Mac or Linux.
        """, unsafe_allow_html=True)

    troubleshooting = st.beta_expander("Troubleshooting", expanded=False)
    with troubleshooting:
        st.markdown(
        f"""
        Most errors are the result of inconsistencies in the data format provided compared to that required by the app. If you receive an error message during the upload or graphing processes, please carefully check the dataset you have provided to ensure it matches the template directions. You can also test the overall app functionality using the {example_link}.  In the event of an unresolvable error, please proceed to the contact page via the left navigation pane to submit a report. Please include as much information as possible, including which part of the analysis process you arrived at the error and any details of the error message itself.

        """, unsafe_allow_html=True)

    contact = st.beta_expander("Contact", expanded=False)
    with contact:
        st.markdown(
        f"""
        To get in touch with the PEARS team, please proceed to the contact page via the left navigation pane. 
        """)

    insert_new_line(num=5)

    st.markdown(
    f"""
    <small>*Disclaimer: the data collected and generated by this platform are not stored or retained, however no guarantee is provided on the end-to-end security of any uploaded or downloaded information. In addition, the information generated here is provided on an “as is” basis with no guarantees of completeness, accuracy, or usefulness. Any action you take as a result of this information is done so at your own risk.*</small>
        
            """, unsafe_allow_html=True
        )
    



# Streamlit encourages well-structured code, like starting execution in a main() function.
def main():

    # Set app title and icon for browser tab
    favicon = Image.open('utilities/icon.png')
    st.set_page_config(page_title='PEARS', page_icon = favicon, layout = 'wide', initial_sidebar_state = 'auto')

    st.markdown(
            f"""
    <style>
        .reportview-container .main .block-container{{
            max-width: 2000px;
            padding-top: 1rem;
            padding-right: 10rem;
            padding-left: 10rem;
            padding-bottom: 10rem;
        }}
    </style>
    """,
            unsafe_allow_html=True,
        )


    logo_box = st.sidebar.empty()
    app_mode = st.sidebar.selectbox("Choose functionality:",
        ["Home", "Prepare dataset", "Academic performance analysis", "Wellbeing analysis", 'Contact'])

    if not hasattr(state, 'data_processed'):
        state.data_processed = False
    
    if app_mode == 'Home':
        generate_introduction()

    
    if app_mode == 'Prepare dataset':
        logo_box.image(Image.open('utilities/banner.png'))
        # st.markdown("# Student Performance Analysis Platform")
        if not hasattr(state, 'data'):
            data = upload_dataset()
        else:
            data = state.data
        if data:
            data = validate_data(data)
            state.data_processed = True
        if st.button('Submit'):
            data = summarise_dataset(data)
            state.data = data
            st.subheader("Congratulations! Your data has been compiled. You may now proceed to the analysis panes using the navigation bar to the left.")
    

    elif app_mode == "Academic performance analysis":
        logo_box.image(Image.open('utilities/banner.png'))
        if state.data_processed:
            grade_plots = run_grades()

        else:
            st.sidebar.markdown("To begin, you must validate your prepared dataset. \n Please select 'Prepare data'.")


    
    elif app_mode == "Wellbeing analysis":
        logo_box.image(Image.open('utilities/banner.png'))
        if state.data_processed:
            welbeing_plots = run_wellbeing()

        else:
            st.sidebar.markdown("To begin, you must validate your prepared dataset. \n Please select 'Prepare data'.")

    elif app_mode == "Contact":
        logo_box.image(Image.open('utilities/banner.png'))
        # Added typeform from https://admin.typeform.com/form/v5tPfvch/results
        st.components.v1.html('<div class="typeform-widget" data-url="https://form.typeform.com/to/v5tPfvch?typeform-medium=embed-snippet" data-transparency="50" data-hide-headers="true" data-hide-footer="true" style="width: 100%; height: 500px;"></div> <script> (function() { var qs,js,q,s,d=document, gi=d.getElementById, ce=d.createElement, gt=d.getElementsByTagName, id="typef_orm", b="https://embed.typeform.com/"; if(!gi.call(d,id)) { js=ce.call(d,"script"); js.id=id; js.src=b+"embed.js"; q=gt.call(d,"script")[0]; q.parentNode.insertBefore(js,q) } })() </script>', height=750, width=750)



# -----------------------Define main pages-----------------------

def run_grades():
    grades_figures = {}

    # read in df
    cohort = state.data['task_summary'].dropna(subset=['score'])

    task_keys = [tuple(key) for key in cohort[['Year', 'Task']].sort_values(['Year', 'Task'], ascending=True).drop_duplicates().values.tolist()]
    task_order = dict(zip(task_keys, np.arange(0, len(task_keys))))

    cohort['task_order'] = [tuple(key) for key in cohort[['Year', 'Task']].values]
    cohort['task_order'] = cohort['task_order'].map(task_order)

    # Collect info for specific groups
    class_students = cohort[cohort['Tracked'] == 1].copy()
    students_to_track = dict(class_students[['Full Name', 'Student Id']].values)
    male_cohort = cohort[cohort['Gender'] == 'M'].copy()


    # -----------------------------Plot class only-----------------------------
    st.subheader("Class scores")
    col1, col2 = st.beta_columns(2)
    col1.markdown("This graph displays the average task score for all tracked students (line) +/- the [standard deviation](https://en.wikipedia.org/wiki/Standard_deviation) (band).")
    class_color = col1.color_picker('To select a new class color:', value='#800080')

    fig = plot_class_grades(cohort, task_order, class_color=class_color)
    col2.pyplot(fig)
    grades_figures[f'Class_average'] = fig
    plt.close(fig)

    # ---------------------Plot class average versus cohort---------------------
    st.subheader("Class compared to cohort")
    col1, col2 = st.beta_columns(2)
    col1.markdown("This graph displays the average task score for all tracked students compared to the entire cohort.")
    cohort_color = col1.color_picker('To select a new cohort color:', value='#ff8c00')

    fig = plot_class_v_cohort_grades(cohort, task_order, untracked_color=cohort_color, tracked_color=class_color)
    col2.pyplot(fig)
    grades_figures['Class_v_Cohort'] = fig
    plt.close(fig)

    # ----------------------Plot male_v_female for cohort----------------------
    st.subheader("Cohort gender comparison")
    col1, col2 = st.beta_columns(2)
    col1.markdown("This graph displays the average task score for males versus females from the entire cohort.")
    male_color = col1.color_picker('To select a new male color:', value='#0652ff')
    female_color = col1.color_picker('To select a new female color:', value='#fe01b1')

    fig = plot_gender_grades(cohort, task_order, female_color=female_color, male_color=male_color)
    grades_figures['Gender'] = fig
    col2.pyplot(fig)
    plt.close(fig)

    # ----------------Preview individual student plots----------------
    st.subheader("Preview individual student comparisons")
    st.markdown("This graph displays an individual student's score compared to the male and class averages.")
    student = st.selectbox('Please select a student to preview:', list(students_to_track.keys()))


    col1, col2, col3 = st.beta_columns([3, 3, 1])
    student_color = col3.color_picker('To select a new student color:', value='#601ef9')
    student_df = cohort[cohort['Student Id'] == students_to_track[student]]
    if len(student_df) < 1:
        st.markdown(f'{student} not found.')
    else:
        name = student_df['Full Name'].unique()[0]
        
        fig = plot_student_vs_collection_grades(student_df, student_label=name, collection_df=male_cohort, collection_label='Average Male', task_order=task_order, collection_color=cohort_color, student_color=student_color)
        col1.pyplot(fig)
        plt.close(fig)

        fig = plot_student_vs_collection_grades(student_df, student_label=name, collection_df=class_students, collection_label='Class Average', task_order=task_order, collection_color=class_color, student_color=student_color)
        col2.pyplot(fig)
        plt.close(fig)

    # -----------------------Prepare plots for download-----------------------
    st.subheader("Prepare plots for download")
    st.markdown("Once satisfied with the color and plot combinations above, click below to generate plots for all tracked students. Once completed, click the 'Download plots' button to generate a download link.")
    col1, col2 = st.beta_columns(2)
    if col1.button('Generate all individual student plots'):
        for student in students_to_track.values():
            student_df = cohort[cohort['Student Id'] == student]
            if len(student_df) < 1:
                continue
            name = student_df['Full Name'].unique()[0]
            
            fig = plot_student_vs_collection_grades(student_df, student_label=name, collection_df=male_cohort, collection_label='Average Male', task_order=task_order, collection_color=cohort_color, student_color='#601ef9')
            grades_figures[f'{name}_v_males'] = fig
            plt.close(fig)

            fig = plot_student_vs_collection_grades(student_df, student_label=name, collection_df=class_students, collection_label='Class Average', task_order=task_order, collection_color=class_color, student_color='#601ef9')
            grades_figures[f'{name}_v_class'] = fig
            plt.close(fig)
        state.grades_figures = grades_figures
    if hasattr(state, 'grades_figures'):
        col2.markdown(f'{int((len(state.grades_figures.keys()) - 3) / 2)} student plots successfully generated.')
        if col1.button('Download plots'):
            zf, memory_zip = zip_images(state.grades_figures)
            tmp_download_link = zip_download(memory_zip, filename='academic_scores')
            col2.markdown(tmp_download_link, unsafe_allow_html=True)

    return grades_figures


def run_wellbeing():

    wellbeing_figures = {}

    # read in df
    wellbeing = state.data['wb_summary'].copy()

    # prepare order info
    type_labels = {0: 'Whole School', 1: 'Positives English', 2: 'Negatives English'}
    type_invert = {v: k for k, v in type_labels.items()}

    type_keys = [tuple(key) for key in wellbeing[['year', 'type_order']].sort_values(['type_order', 'year'], ascending=True).drop_duplicates().values.tolist()]
    type_order = dict(zip(type_keys, np.arange(0, len(type_keys))))

    term_keys = [tuple(key) for key in wellbeing[['year', 'Term']].sort_values(['year', 'Term'], ascending=True).drop_duplicates().values.tolist()]
    term_order = dict(zip(term_keys, np.arange(0, len(term_keys))))

    # ---------generate class summary---------
    source = wellbeing.copy().groupby(['year', 'Term', 'type', 'type_position']).sum()['count'].reset_index()
    source = pd.pivot_table(source, values='count', columns=['type_position'], index='Term')

    st.subheader("Class Summary")
    st.markdown("This graph displays the sum of all incidences across each year, broken down by term.")

    col1, col2, col3, col4 = st.beta_columns(4)
    term_1_color = col1.color_picker('Select term 1 color:', value='#a082b0')
    term_2_color = col2.color_picker('Select term 2 color:', value='#744d8a')
    term_3_color = col3.color_picker('Select term 3 color:', value='#765b85')
    term_4_color = col4.color_picker('Select term 4 color:', value='#44175c')
    colours = [term_1_color, term_2_color, term_3_color, term_4_color]

    fig, ax = plt.subplots()
    source.T.plot(kind='bar', stacked=True, ax=ax, color=colours)
    ha.make_wellbeing_class_pretty(ax, type_order, type_labels)
    wellbeing_figures['whole_class'] = fig
    st.pyplot(fig)
    plt.close(fig)

    # ----------------Preview individual student plots----------------
    st.subheader("Preview individual student history")
    st.markdown("This graph displays the sum of all incidences across each year, broken down by term.")

    student = st.selectbox('Please select a student to preview:', wellbeing['Full Name'].unique().tolist())

    col1, col2, col3 = st.beta_columns(3)
    ws_color = col1.color_picker('Select Whole School color:', value='#3e51cf')
    pos_color = col2.color_picker('Select Positives color:', value='#1c8c00')
    neg_color = col3.color_picker('Select Negatives color:', value='#c7323e')
    palette = {'Whole School': ws_color, 'Positives English': pos_color, 'Negatives English': neg_color}

    student_df = wellbeing[wellbeing['Full Name'] == student]
    if len(student_df) < 1:
        st.markdown(f'{student} not found.')
    else:      
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=student_df, x='term_order', y='count', hue='type', palette=palette, linewidth=5)
        ha.make_wellbeing_student_pretty(ax, term_order, student)
        st.pyplot(fig)
        plt.close(fig)

    # -------------Plot all students -------------
    st.subheader("Prepare plots for download")
    st.markdown("Once satisfied with the color and plot combinations above, click below to generate plots for all tracked students. Once completed, click the 'Download plots' button to generate a download link.")

    col1, col2 = st.beta_columns(2)
    if col1.button('Generate all individual student plots'):
        for student, df in wellbeing.groupby('Full Name'):
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.lineplot(data=df, x='term_order', y='count', hue='type', palette=palette, linewidth=5)
            ha.make_wellbeing_student_pretty(ax, term_order, student)
            wellbeing_figures[f'{student}'] = fig
            plt.close(fig)
        state.wellbeing_figures = wellbeing_figures

    if hasattr(state, 'wellbeing_figures'):
        col2.markdown(f"{len(state.wellbeing_figures.keys()) - 1} student plots successfully generated.")
        if col1.button('Download plots'):
            zf, memory_zip = zip_images(state.wellbeing_figures)
            tmp_download_link = zip_download(memory_zip, filename='wellbeing')
            col2.markdown(tmp_download_link, unsafe_allow_html=True)

    return wellbeing_figures



# -----------------------Define plot elements-----------------------

def plot_student_vs_collection_grades(student_df, student_label, collection_df, collection_label, task_order, collection_color='purple', student_color='#601ef9'):

    fig, ax = plt.subplots()
    sns.lineplot(data=collection_df, x='task_order', y='score', label=collection_label, ci='sd', color=collection_color, alpha=0.5, marker='o')
    sns.lineplot(data=student_df, x='task_order', y='score',
                label=student_label, color=student_color, linewidth=3, marker='o')
    plt.xticks(rotation=45)
    plt.ylabel('Overall score (%)')

    plt.ylim(0, 100)
    ax.set_xlabel('')
    ha.make_grades_pretty(ax, task_order)
    plt.legend(ncol=2, loc=9)
    # plt.savefig(f'{output_folder}{name}_v_class.png', bbox_inches='tight')

    return fig

def plot_class_v_cohort_grades(cohort, task_order, untracked_color='darkorange', tracked_color='purple'):

    fig, ax = plt.subplots()
    sns.lineplot(data=cohort, x='task_order', y='score', hue='Tracked', hue_order=[0, 1], palette=[untracked_color, tracked_color], ax=ax, ci='sd', marker='o')
    # replace legend labels
    handles, labels = ax.get_legend_handles_labels()
    new_labels = ['Cohort', 'Class']
    ax.legend(new_labels)
    ax.set_xlabel('')
    ha.make_grades_pretty(ax, task_order)

    return fig


def plot_gender_grades(cohort, task_order, female_color='#fe01b1', male_color='#0652ff'):

    fig, ax = plt.subplots()
    sns.lineplot(data=cohort, x='task_order', y='score', hue_order=['F', 'M'],
                hue='Gender', palette=[female_color, male_color], ax=ax, marker='o')
    plt.xticks(rotation=45)
    plt.ylabel('Overall score (%)')
    plt.xlabel('Assessment number')
    plt.ylim(0, 100)
    ax.set_xlabel('')
    ha.make_grades_pretty(ax, task_order)
    plt.tight_layout()

    return fig

    # plt.show()


def plot_class_grades(cohort, task_order, class_color='purple'):

    fig, ax = plt.subplots()
    # plot whole class
    sns.lineplot(data=cohort[cohort['Tracked'] == 1], x='task_order', y='score', label='Class Average', color=class_color, alpha=0.5, ci='sd', marker='o')
    ax.set_xlabel('')
    ha.make_grades_pretty(ax, task_order)
    plt.tight_layout()

    return fig



if __name__ == "__main__":
    main()

# TODO 2021 March 07: Add statistics element, to quantify the change in academic performance over time