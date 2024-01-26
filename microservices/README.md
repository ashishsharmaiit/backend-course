## Locally running cloud functions

`functions-framework-python --target <function-entry-name>`

function will be available at http://localhost:8080

## Deploy functions

gcloud functions deploy python-http-function \
    --gen2 \
    --runtime=python312 \
    --region=REGION \
    --source=. \
    --entry-point=hello_http \
    --trigger-http