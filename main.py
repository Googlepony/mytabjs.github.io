from flask import Flask, request, make_response
import tempfile
import tabula
import os

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
  response = make_response('Voila! The server connected successfully.')
  response.headers['Content-type'] = 'text/plain'
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
  return response


@app.route('/extract', methods=['POST'])
def extract_data():
  try:
    # Check if files are in the request
    if 'file' not in request.files:
      return {"error from server": "No file part in the request"}

    # Get the files from the request
    pdf_files = request.files.getlist('file')

    # Create a response object with the CSV data as a file attachment
    response = make_response()
    response.headers[
      'Content-Disposition'] = 'attachment; filename=merged_output.csv'
    response.headers['Content-type'] = 'text/csv'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'

    # Merge all PDFs and convert them to CSV
    for i, pdf_file in enumerate(pdf_files):
      with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(pdf_file.read())
        tmp.flush()
        tmp.seek(0)

        output_file = f"output_{i}.csv"
        tabula.convert_into(tmp.name,
                            output_path=output_file,
                            output_format='csv',
                            pages='all',
                            area=(80, 30, 1080, 810))
        #area=(100, 37.5, 450, 776.5))

        with open(output_file, 'r') as f:
          csv_data = f.read()

        response.data += csv_data.encode('utf-8')

        os.remove(output_file)

    return response

  except Exception as e:
    return {"error": str(e)}


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
