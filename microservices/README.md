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

## Deploy lamda functions

[href]https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

- Navigate to the function folder,

`cd microservices/<function_name>`

- Update python dependencies,

`pip install -r requirements.txt --target ./packages`

- Create a deployment package containing your function code and dependencies. This should be a ZIP file containing your code and any required libraries. The zip folder is required to have a flat structure.

To create zip files use,

`cd packages`

`zip ../../release_v0_1.zip -r .`

`cd ..`

`zip ../release_v0_1.zip -r . -x 'packages/*' '__pycache__/*' '.DS_Store'`

- Create function,

`aws lambda create-function --function-name my-function --runtime nodejs14 --role myrole --handler index.handler --zip-file fileb://function.zip`

- Update function,

`aws lambda update-function-code --function-name my-function --zip-file fileb://updatedfunction.zip` 