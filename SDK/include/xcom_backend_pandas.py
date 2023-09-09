from airflow.models.xcom import BaseXCom
import pandas as pd
import json
import uuid
from minio import Minio
import os
import io

class CustomXComBackendPandas(BaseXCom):
    PREFIX = "xcom_minio://"
    BUCKET_NAME = "custom-xcom-backend"

    @staticmethod
    def serialize_value(
        value,
        key=None,
        task_id=None,
        dag_id=None,
        run_id=None,
        map_index= None,
        **kwargs
    ):
        
        client = Minio(
            os.environ["MINIO_IP"],
            os.environ["MINIO_ACCESS_KEY"],
            os.environ["MINIO_SECRET_KEY"],
            secure=False
        )

        # added serialization method if the value passed is a Pandas dataframe
        # the contents are written to a local temporary csv file
        if isinstance(value, pd.DataFrame):
            filename = "data_" + str(uuid.uuid4()) + ".csv"
            minio_key = f"{run_id}/{task_id}/{filename}"

            value.to_csv(filename)

            with open(filename, 'r') as f:
                string_file = f.read()
                bytes_to_write = io.BytesIO(bytes(string_file, 'utf-8'))

            # remove the local temporary file
            os.remove(filename)

        # if the value passed is not a Pandas dataframe, attempt to use
        # JSON serialization
        else:
            filename = "data_" + str(uuid.uuid4()) + ".json"
            minio_key = f"{run_id}/{task_id}/{filename}"

            bytes_to_write = io.BytesIO(bytes(json.dumps(value), 'utf-8'))

        client.put_object(
            CustomXComBackendPandas.BUCKET_NAME,
            minio_key,
            bytes_to_write,
            -1, # -1 = unknown filesize
            part_size=10*1024*1024,
        )

        reference_string = CustomXComBackendPandas.PREFIX + minio_key

        return BaseXCom.serialize_value(value=reference_string)

    @staticmethod
    def deserialize_value(result):
        reference_string = BaseXCom.deserialize_value(result=result)
        key = reference_string.replace(CustomXComBackendPandas.PREFIX, "")

        client = Minio(
            os.environ["MINIO_IP"],
            os.environ["MINIO_ACCESS_KEY"],
            os.environ["MINIO_SECRET_KEY"],
            secure=False
        )

        response = client.get_object(
            CustomXComBackendPandas.BUCKET_NAME,
            key
        )

        # added deserialization option to convert a CSV back to a dataframe
        if key.split(".")[-1] == "csv":

            with open("csv_xcom.csv", "w") as f:
                f.write(response.read().decode("utf-8"))
            output = pd.read_csv("csv_xcom.csv")

            # remove the local temporary file
            os.remove("csv_xcom.csv")

        # if the key does not end in 'csv' use JSON deserialization
        else:
            output = json.loads(response.read())

        return output