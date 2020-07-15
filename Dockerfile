FROM python
COPY . /code
RUN cd /code && python setup.py install && cxmaintain init && cxmaintain version