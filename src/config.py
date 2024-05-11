from dotenv import dotenv_values
import os

configs = {
    **dotenv_values(".env"),
    **os.environ,
}
