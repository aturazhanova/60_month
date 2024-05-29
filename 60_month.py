import os
from flask import Flask, request, jsonify, send_from_directory
import tabula
import pandas as pd
from pdfminer.high_level import extract_text
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.DEBUG)

def extract_opvv_pages(pdf_path):
    try:
        text = extract_text(pdf_path)
        logging.debug(f"Extracted text from PDF: {text[:1000]}...")  # Log the first 1000 characters for brevity
        opvv_pages = []
        pages = text.split("\f")
        
        for page_num, page in enumerate(pages):
            if "ОППВ" in page:
                opvv_pages.append(page_num + 1)
        
        logging.debug(f"Identified ОППВ pages: {opvv_pages}")
        return opvv_pages
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return []

def process_pdf(pdf_path):
    try:
        opvv_pages = extract_opvv_pages(pdf_path)
        if not opvv_pages:
            logging.debug("No ОППВ pages found in the PDF.")
            return None
        tables = tabula.read_pdf(pdf_path, pages=opvv_pages, stream=True)
        
        if tables:
            combined_table = pd.concat(tables, ignore_index=True)
            os.makedirs('output', exist_ok=True)
            excel_file = os.path.join('output', 'combined_tables.xlsx')
            combined_table.to_excel(excel_file, index=False)
            logging.debug(f"Excel file created at {excel_file}")
            return excel_file
        else:
            logging.debug("No tables found in the specified ОППВ pages.")
            return None
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return None

def process_excel(excel_file):
    try:
        if excel_file and os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            if 'Жарналардың түсуі' in df.columns and 'Unnamed: 0' in df.columns:
                df_filtered = df[df['Жарналардың түсуі'].isin(['(МКЗЖ)/Поступление взносов', '(ОППВ)'])].copy()
                df_filtered['Unnamed: 0'] = pd.to_datetime(df_filtered['Unnamed: 0'], errors='coerce', format='%d.%m.%Y')
                df_filtered['МесяцГод'] = df_filtered['Unnamed: 0'].dt.strftime('%m.%Y')
                df_filtered = df_filtered.dropna(subset=['Unnamed: 0'])
                unique_months = df_filtered['МесяцГод'].nunique()
                logging.debug(f"Number of unique months: {unique_months}")
                return unique_months >= 60
            else:
                logging.debug("Required columns not found in the Excel file.")
                return False
        else:
            logging.debug("Excel file does not exist.")
            return False
    except Exception as e:
        logging.error(f"Error processing Excel file: {e}")
        return False

@app.route('/process-pdf', methods=['POST'])
def process_pdf_route():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        pdf_path = 'input_pdf.pdf'
        file.save(pdf_path)
        
        excel_file = process_pdf(pdf_path)
        if not excel_file:
            return jsonify({'result': False})
        
        result = process_excel(excel_file)
        
        return jsonify({'result': result})
    except Exception as e:
        logging.error(f"Error in /process-pdf route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return send_from_directory('.', '60_month.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005, use_reloader=False)
