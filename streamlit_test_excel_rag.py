import dotenv
import json
import openpyxl

dotenv.load_dotenv()

import pandas as pd
import streamlit as st
from preprocess_excel_sheets import ExcelSheetParser
from excel_agent import ExcelAgent
from generate_slides import GenerateSlides

if st.button('reset'):
   del st.session_state.file_name
   del st.session_state.slide_json
   del st.session_state.returned_context
   del st.session_state.agent

def load_excel_file(file_path):
   
   workbook = openpyxl.load_workbook(file_path)
   sheet = workbook.active  # or specify the sheet name with workbook['Sheet1']
   parser = ExcelSheetParser(sheet=sheet, maxn=10, debug=True)

   df = parser.parse_excel_sheet()

   df.to_csv('/Users/arjunv/Desktop/RAG-EXCEL-ANTHROPIC/excel_rag_demo/data/single_sheet_single_table/merged_cells_1.csv', index=False)
   excel_agent = ExcelAgent('/Users/arjunv/Desktop/RAG-EXCEL-ANTHROPIC/excel_rag_demo/data/single_sheet_single_table/merged_cells_1.csv')

   return excel_agent, df

def get_query(excel_agent, query):
   retrieved_context = excel_agent.get_context(query)

   gs = GenerateSlides()
   response = gs.generate_slide_content(query, retrieved_context)

   return response, retrieved_context

file_name = ''
excel_agent = ''

excel_sheets = ['None', 'Stock Item with BoM details.xlsx', 'Standard Table.xlsx'
                ,'Ledgers in Default Template.xlsx', 'Bank Ledger with bank details.xlsx']
        
file_path = f'/Users/arjunv/Desktop/RAG-EXCEL-ANTHROPIC/excel_rag_demo/data/single_sheet_single_table/{file_name}'

st.title("Excel-Rag : Slide Generator")

tile = st.container(border=True)

file_name = tile.selectbox('Choose a Supporting Document !', excel_sheets)
st.session_state.file_name = file_name

if file_name !=  'None':
   file_path = f"/Users/arjunv/Desktop/RAG-EXCEL-ANTHROPIC/excel_rag_demo/data/single_sheet_single_table/{file_name}"
   parse_flag = tile.button('Parse Excel Sheet !')

   if parse_flag:
      excel_agent, df =  load_excel_file(file_path)

      st.session_state.agent = excel_agent

      with tile.expander("Parsed Excel Sheet"):
         tile.dataframe(df, height=250)

tile  = st.container(border=True)
input_query = tile.text_input('What kind of slide you want to create ?')

# st.session_state.input_query = input_query

with tile.expander(label='Example Prompts'):

    if st.session_state.file_name == 'Stock Item with BoM details.xlsx':
      st.write("""- Create a Product Overview slide that provides a detailed breakdown of the hampers, highlighting the components and their respective quantities. 
               \n- Create a Sales and Marketing slide that provides a descriptions of the various hampers and the strategies employed to promote each one. 
               \n- Create a Distribution Overview slide that focuses on the distribution of components across various godowns.""")

    elif st.session_state.file_name == 'Standard Table.xlsx':
      st.write("""- Create a sales transactions slide that introduces a dataset showcasing the sales performance of Aayush and Sachin.
               \n- Create a slide summarising sales performance of a particular product - Pen.""")

    elif st.session_state.file_name == 'Ledgers in Default Template.xlsx':
       st.write("- Create a slide showcasing the Transaction Summary, which includes key statistics such as the total number of transactions, the total debit amount, and the total credit amount.")

    elif st.session_state.file_name == 'Bank Ledger with bank details.xlsx':
       st.write("""- Design a slide that summarizes the different banks represented in the data. List the bank names along with the total number of accounts for each bank
                \n- Develop a slide focusing on HDFC Bank's account information. Include the account holder's name, account number, IFS code, and the branch location in a clear and concise format.
                \n- Design a Q&A slide to encourage audience interaction. Include a prompt inviting questions about the bank account details and financial management practices. """)
   
generate_a_slide = tile.button('Generate a Slide')

generated = False

if generate_a_slide:

   with st.spinner("Please Wait..."):
      slide_json, returned_context = get_query(st.session_state.agent, input_query)

      st.session_state.slide_json = slide_json
      st.session_state.returned_context = returned_context

      generated = True

if generated:

    with st.expander('Extracted Context'):
        st.write(st.session_state.returned_context)

    tile = st.container(border=True)
    tile.markdown("#### Generated Slide Content")
    tile.write(st.session_state.slide_json)    