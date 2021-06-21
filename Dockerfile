FROM public.ecr.aws/lambda/python:3.8
COPY requirements.txt lambda_function.py  ./
RUN pip install -r requirements.txt
CMD ["lambda_function.lambda_handler"] 

