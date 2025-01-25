# Copyright 2022 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -------------------------------------------------------------------------

import logging
from typing import Optional

import aiofiles
import shutil
from fastapi import APIRouter, Body, File, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
import os
from controller import Orchestrator
from pydantic import BaseModel

api_router = APIRouter()

base_compress_file_name = "iac_files_"


class Doml(BaseModel):
    ecore: str
    model: Optional[str] = None
    external_iac_folder: float


@api_router.post("/infrastructure/files", deprecated=True)
def create_iac_from_intermediate_representation(intermediate_representation: dict = Body(...)):
    logging.info("Received intermediate representation create_iac_from_intermediate_representation request")
    compress_folder_info = Orchestrator.create_iac_from_intermediate_representation(intermediate_representation)
    return FileResponse(compress_folder_info.file_path, media_type='application/octet-stream',
                        filename=compress_folder_info.filename)


@api_router.post("/iac/files")
def create_iac_from_doml(data: str = Body(..., media_type="application/xml")):
    logging.info("Received create_iac_from_doml request")
    compress_folder_info = Orchestrator.create_iac_from_doml(model=data, metamodel_directory="icgparser/doml/v2",
                                                             is_multiecore_metamodel=False)
    return FileResponse(path=compress_folder_info.file_path, media_type='application/octet-stream',
                        filename=compress_folder_info.filename)


CHUNK_SIZE = 1024 * 1024  # adjust the chunk size as desired


@api_router.post("/iac/files/upload")
async def create_iac_from_doml_model(file: UploadFile = File(...)):
    try:
        filepath = os.path.join('./', os.path.basename(file.filename))
        async with aiofiles.open(filepath, 'wb') as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='There was an error uploading the file')
    finally:
        await file.close()
        #logging.info(f"Removing file {file.filename}")
    data, outputpath = Orchestrator.extract_file_zip('./'+file.filename)
    compress_folder_info = Orchestrator.create_iac_from_doml(model=data, metamodel_directory=outputpath,
                                                             is_multiecore_metamodel=False)
    shutil.unpack_archive(compress_folder_info.filename, outputpath)
    shutil.make_archive(outputpath, 'zip', outputpath )
    logging.info(f"Successfuly uploaded {file.filename}")
    return FileResponse(path=outputpath+'.zip', media_type='application/octet-stream',
                        filename=file.filename)


@api_router.post("/iac/files/extension/intermediate_representation")
async def create_iac_intermediate_representation(file: UploadFile = File(...)):
    try:
        filepath = os.path.join('./', os.path.basename(file.filename))
        async with aiofiles.open(filepath, 'wb') as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='There was an error uploading the file')
    finally:
        await file.close()
        #logging.info(f"Removing file {file.filename}")

    logging.info(f"Successfuly uploaded {file.filename}")
    return FileResponse(path=filepath, media_type='application/octet-stream',
                        filename=file.filename)

