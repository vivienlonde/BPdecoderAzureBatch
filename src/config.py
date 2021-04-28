# -------------------------------------------------------------------------
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
# ----------------------------------------------------------------------------------
# The example companies, organizations, products, domain names,
# e-mail addresses, logos, people, places, and events depicted
# herein are fictitious. No association with any real company,
# organization, product, domain name, email address, logo, person,
# places, or events is intended or should be inferred.
# --------------------------------------------------------------------------

# Global constant variables (Azure Storage account/Batch details)

# import "config.py" in "python_quickstart_client.py "

_BATCH_ACCOUNT_NAME = 'myownbatchaccount'  # Your batch account name
_BATCH_ACCOUNT_KEY = 'KRDjqzdnN548Mo8rjfvM0gAHpWn0SqFHQLd9H/QlaQMbnF3M1FJ1TiQPYMX3mLEPw7QLYilFIaxf4UVIOlNThw=='  # Your batch account key
_BATCH_ACCOUNT_URL = 'https://myownbatchaccount.westeurope.batch.azure.com'  # Your batch account URL
_STORAGE_ACCOUNT_NAME = 'mystorageforbatch'  # Your storage account name
_STORAGE_ACCOUNT_KEY = 'GrWmz7B2qt6ewPypzAVSe42DYgX7daySFEBsG+ORNHcAh+48pBwHhMks4vg21Oe66EGIsSog44zUWIf7v6ocaQ=='  # Your storage account key
_POOL_ID = 'TestPool'  # Your Pool ID
_POOL_NODE_COUNT = 2  # Pool node count
_POOL_VM_SIZE = 'Standard_D2_v3'  # VM Type/Size
_JOB_ID = 'TestJob'  # Job ID
_STANDARD_OUT_FILE_NAME = 'stdout.txt'  # Standard Output file
