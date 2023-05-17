# py-docai-pdf-tester

Tester to send documents to a Google Cloud Document AI form processor, and save the results as a JSON file.

## Quickstart

This code is based on the [Form Processing with Document AI (Python)](https://codelabs.developers.google.com/codelabs/docai-form-parser-v1-python#0) sample code and codelab.

### Step 1

To start make sure you have the [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed and set with a valid service identity.

You can use your gcloud user identity for service calls with this command.

```bash
gcloud auth application-default login
```

### Step 2

Make sure you have a [Google Cloud Document AI Form Processor](https://cloud.google.com/document-ai/docs/create-processor) created, and copy the id.

Set the following environment variables either in your shell or VSCode debug settings file if you want to debug.

```bash
export project_id="YOUR_GOOGLE_CLOUD_PROJECT_ID"
export location="PROCESSOR_LOCATION" # either eu or us, set when you created your form processor
export processor_id="YOUR_DOCAI_FORM_PROCESSOR_ID"
export file_path="PATH_TO_PDF_FILE" # path to file to process
```

### Step 3

Run the `main.py` program to do the processing. You should get a `result.json` file created with the results.

```bash
python main.py
```
