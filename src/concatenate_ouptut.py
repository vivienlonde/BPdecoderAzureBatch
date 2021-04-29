import azure.storage.blob as azureblob
import os
import sys
import numpy as np

import config

blob_service_client = azureblob.BlobServiceClient(
    account_url='https://{}.blob.core.windows.net/'.format(config._STORAGE_ACCOUNT_NAME),
    credential=config._STORAGE_ACCOUNT_KEY)

container_name = 'output'
container_client = blob_service_client.get_container_client(container_name)

# Create a local directory to hold blob data
local_path = os.path.join(sys.path[0], 'output_data')

first_blob = True
for blob in container_client.list_blobs():
    if first_blob:
        # print("Found blob: ", blob.name) 
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
        download_file_path = os.path.join(local_path, blob.name)
        # print('Downloading blob to ' + download_file_path)
        with open(download_file_path, 'wb') as download_file:
            
            downloaded_data = blob_client.download_blob()
            print(type(downloaded_data))
            # print(downloaded_data)
            print()
            
            downloaded_content = downloaded_data.readall()
            print(type(downloaded_content))
            print(downloaded_content)
            print()
            
            np.load(downloaded_content)
            
            
            # download_file.write(blob_client.download_blob().readall())
        first_blob = False