import streamlit as st
import nltk
import os
import spacy
nltk.download('stopwords')
spacy.load('en_core_web_sm')
from pyresparser import ResumeParser
import re
from pdfminer.high_level import extract_text
from docx import Document
import pandas as pd
import base64, random
import time, datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import pafy
import plotly.express as px
import youtube_dl
from IPython.display import HTML
from data_insertion import insert_user_data_mongo
from pymongo import MongoClient
import PyPDF2
from mongodb_connect import get_mongo_connection
db = get_mongo_connection()

if db:
    collection = db['user_data']  # Example collection
    # Proceed with inserting/fetching data
else:
    print("Database connection not established. Check logs for errors.")


def fetch_yt_video(link):
    # video = pafy.new(link)
    # return video.title
    try:
        with youtube_dl.YoutubeDL({}) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            return info_dict.get('url')
    except Exception as e:
        print(f"Error fetching video title: {e}")
        return None

SKILLS_DB = [
    'python', 'java', 'c++', 'sql', 'html', 'css', 'javascript',
    'react', 'node.js', 'mongodb', 'mysql', 'excel', 'git', 'github',
    'machine learning', 'data analysis', 'communication', 'leadership'
]
class MyResumeParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.custom_nlp = spacy.load("en_core_web_sm")

    def extract_text(self):
        if self.file_path.lower().endswith('.pdf'):
            return extract_text(self.file_path)
        elif self.file_path.lower().endswith('.docx'):
            doc = Document(self.file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        else:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(self.file_path, 'r', encoding='latin-1') as f:
                    return f.read()

    def extract_email(self, text):
        email = re.findall(r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+", text)
        return email[0] if email else None

    def extract_phone(self, text):
        phone = re.findall(r'\+?\d[\d -]{8,12}\d', text)
        return phone[0] if phone else None

    def get_pdf_page_count(self):
        with open(self.file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)
    

    def extract_skills(self, text):
        text = text.lower()
        return [skill for skill in SKILLS_DB if skill in text]


    def get_extracted_data(self):
        text = self.extract_text()
        doc = self.custom_nlp(text)
        name = None
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

        data = {
            "name": name,
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "raw_text": text,
            "skills": self.extract_skills(text) 

        }

        if self.file_path.lower().endswith('.pdf'):
            data["no_of_pages"] = self.get_pdf_page_count()
        else:
            data["no_of_pages"] = None  # Or 1

        return data

        

def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


connection = pymysql.connect(host='sql7.freesqldatabase.com', port=3306 ,user='sql7767123', password='bybKChl2Pf')
cursor = connection.cursor()


def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills,
                courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (
    name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
    courses)
    # cursor.execute(insert_sql, rec_values)
    # connection.commit()

    if email is None:
        email = "N/A"
    
    try:
        cursor.execute(insert_sql, rec_values)
        connection.commit()
    except pymysql.err.IntegrityError as e:
        print("Integrity Error:", e)
        connection.rollback()



st.set_page_config(
    page_title="Atingle Resume Analyzer",
    page_icon='./Logo/favicon.png',
)


def run():
    st.title("Atingle Resume Analyzer")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    # img = Image.open('./Logo/atinglelogo.png')
    # img = img.resize((250, 250))
    # st.image(img)
    client = MongoClient("mongodb+srv://jaspinder0029:harry2299@cluster0.r18ki.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Replace with your connection string
    db = client['resumeanalyzer']  # Database name
    collection = db['user_data']

    # Create the DB
    # db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    # cursor.execute(db_sql)
    # connection.select_db("sra")

    # # Create table
    # DB_table_name = 'user_data'
    # table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
    #                 (ID INT NOT NULL AUTO_INCREMENT,
    #                  Name varchar(100) NOT NULL,
    #                  Email_ID VARCHAR(50) NOT NULL,
    #                  resume_score VARCHAR(8) NOT NULL,
    #                  Timestamp VARCHAR(50) NOT NULL,
    #                  Page_no VARCHAR(5) NOT NULL,
    #                  Predicted_Field VARCHAR(25) NOT NULL,
    #                  User_level VARCHAR(30) NOT NULL,
    #                  Actual_skills VARCHAR(300) NOT NULL,
    #                  Recommended_skills VARCHAR(300) NOT NULL,
    #                  Recommended_courses VARCHAR(600) NOT NULL,
    #                  PRIMARY KEY (ID));
    #                 """
    # cursor.execute(table_sql)
    if choice == 'Normal User':
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Upload your resume, and get smart recommendation based on it."</h4>''',
        #             unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            # with st.spinner('Uploading your Resume....'):
            #     time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = MyResumeParser(save_image_path).get_extracted_data()
            #print(resume_data)
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                                unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                ## Skill shows
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')

                ##  recommendation
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask',
                              'streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                                'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                                'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                ## Courses recommendation
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                              'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                              'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='2')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='3')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='4')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='5')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                              'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                              'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                              'Solid', 'Grasp', 'User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='6')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                
                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'OBJECTIVE' in resume_text.upper():
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add your career objective, it will give your career intension to the Recruiters.</h4>''',
                        unsafe_allow_html=True)

                if 'DECLARATION' in resume_text.upper():
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration✍</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                        unsafe_allow_html=True)

                if 'HOBBIES' in resume_text.upper() or 'INTRESTS' in resume_text.upper():
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                        unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text.upper():
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.</h4>''',
                        unsafe_allow_html=True)

                if 'PROJECTS' in resume_text.upper():
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.</h4>''',
                        unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Your Resume Writing Score: ' + str(score) + '**')
                st.warning(
                    "** Note: This score is calculated based on the content that you have added in your Resume. **")
                st.balloons()

                # insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                #             str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                #             str(recommended_skills), str(rec_course))
                insert_user_data_mongo(
    resume_data,
    resume_score,
    timestamp,
    reco_field,
    cand_level,
    recommended_skills,
    rec_course
     
    
)

                # ## Resume writing video
                # st.header("**Bonus Video for Resume Writing Tips💡**")
                # resume_vid = random.choice(resume_videos)
                # res_vid_title = fetch_yt_video(resume_vid)
                # # st.subheader("✅ **" + res_vid_title + "**")
                # # st.video(resume_vid)
                # st.markdown(f'<iframe width="560" height="315" src="{resume_vid}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>',unsafe_allow_html=True)

                


                # ## Interview Preparation Video
                # st.header("**Bonus Video for Interview👨‍💼 Tips💡**")
                # interview_vid = random.choice(interview_videos)
                # int_vid_title = fetch_yt_video(interview_vid)
                # # st.subheader("✅ **" + int_vid_title + "**")
                # # st.video(interview_vid)
                # st.markdown(f'<iframe width="560" height="315" src="{interview_vid}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>', unsafe_allow_html=True)


                # connection.commit()
            else:
                st.error('Something went wrong..')
    else:
        ## Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'Atingle' and ad_password == 'atingle123':
                st.success("Welcome Boss")
                # Display Data
                cursor.execute('''SELECT * FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                          'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                          'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)
        
                ## Admin Side Data
                query = 'SELECT Predicted_Field, COUNT(*) AS count FROM user_data GROUP BY Predicted_Field;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                labels = plot_data['Predicted_Field']
                values = plot_data['count']
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(plot_data, values=values, names=labels, title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                query = 'SELECT User_level, COUNT(*) AS count FROM user_data GROUP BY User_level;'
                plot_data = pd.read_sql(query, connection)

                labels = plot_data['User_level']
                values = plot_data['count']
                st.subheader("📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(plot_data, values=values, names=labels, title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)

            else:
                st.error("Wrong ID & Password Provided")

run()
