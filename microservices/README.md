## Locally running cloud functions

`functions-framework --target=http_course_plan`

function will be available at http://localhost:8080

Test command,

`curl -H 'Content-Type: application/json' -X POST -d '{"course_options": {"topic": "Neural net for Robotics", "duration": "5 weeks", "teachingStyle": "easy to understand language, quiz me after every lesson, give practice assignments", "focusOn": "", "purposeFor": "", "previousKnowledge": "", "otherConsiderations": ""}}' http://localhost:8080`

## Deploy functions

`gcloud functions deploy course_plan_generator --runtime=python311 --entry-point=http_course_plan --trigger-http --memory=256MB --timeout=540s`

The functions is deployed at, 

https://us-central1-socratiq.cloudfunctions.net/course_plan_generator

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