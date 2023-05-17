from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from typing import Sequence
import json
import io
import os

project_id = os.environ.get("project_id")
location = os.environ.get("location")  # Format is 'us' or 'eu'
processor_id = os.environ.get("processor_id")  #  Create processor before running sample
file_path = os.environ.get("file_path")
mime_type = "application/pdf"  # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types


def process_document_form_sample(
    project_id: str, location: str, processor_id: str, file_path: str, mime_type: str
):
    # Online processing request to Document AI
    document = process_document(
        project_id, location, processor_id, file_path, mime_type
    )

    # Read the table and form fields output from the processor
    # The form processor also contains OCR data. For more information
    # on how to parse OCR data please see the OCR sample.

    # For a full list of Document object attributes, please reference this page:
    # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document

    text = document.text
    print(f"Full document text: {repr(text)}\n")
    print(f"There are {len(document.pages)} page(s) in this document.")

    result = {"pageCount": len(document.pages), "pages": [], "text": text}
    # with open("results.json", "w") as text_file:
    #    text_file.write(json.dumps(document.__dict__))

    # Read the form fields and tables output from the processor
    for page in document.pages:
        print(f"\n\n**** Page {page.page_number} ****")

        print(f"\nFound {len(page.tables)} table(s):")

        newPage = {}
        newPage["tables"] = []
        newPage["fields"] = []

        for table in page.tables:
            num_collumns = len(table.header_rows[0].cells)
            num_rows = len(table.body_rows)
            print(f"Table with {num_collumns} columns and {num_rows} rows:")

            # Print header rows
            print("Columns:")
            print_table_rows(table.header_rows, text)

            newTable = {}
            newTable["headers"] = []
            for table_row in table.header_rows:
                for cell in table_row.cells:
                    cell_text = layout_to_text(cell.layout, text)
                    newTable["headers"].append(cell_text.strip())

            # Print body rows
            print("Table body data:")
            print_table_rows(table.body_rows, text)

            newTable["data"] = []
            for table_row in table.body_rows:
                row = {}
                counter = 0
                for cell in table_row.cells:
                    cell_text = layout_to_text(cell.layout, text)
                    row[newTable["headers"][counter]] = cell_text.strip()
                    counter = counter + 1

                newTable["data"].append(row)

            newPage["tables"].append(newTable)

        print(f"\nFound {len(page.form_fields)} form field(s):")
        for field in page.form_fields:
            name = layout_to_text(field.field_name, text)
            value = layout_to_text(field.field_value, text)

            newPage["fields"].append({"name": name, "value": value})

        result["pages"].append(newPage)

    with open("results.json", "w") as text_file:
        text_file.write(json.dumps(result))


def process_document(
    project_id: str, location: str, processor_id: str, file_path: str, mime_type: str
) -> documentai.Document:
    # You must set the api_endpoint if you use a location other than 'us'.
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor, e.g.:
    # projects/project_id/locations/location/processor/processor_id
    name = client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    result = client.process_document(request=request)

    return result.document


def print_table_rows(
    table_rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
) -> None:
    for table_row in table_rows:
        row_text = ""
        for cell in table_row.cells:
            cell_text = layout_to_text(cell.layout, text)
            row_text += f"{repr(cell_text.strip())} | "
        print(row_text)


def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document's text. This function converts
    offsets to a string.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in layout.text_anchor.text_segments:
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)
        response += text[start_index:end_index]
    return response


process_document_form_sample(project_id, location, processor_id, file_path, mime_type)
