from pydantic import BaseModel
from datetime import datetime
from typing import List
from . import db_record
from datetime import datetime

class RecordBase(BaseModel):
    id: str = ""

class Attachment(BaseModel):
    id: str = None
    extension: str = None

class Record(RecordBase):
    mesages: List[str] = []
    attachmens: List[Attachment] = []
    date: datetime = datetime.now()

    def create(self, id: str):
        self.id = id
        return self

    def create_from_db(self, rec: db_record.Record):
        self.id = rec.id
        self.date = rec.date
        self.attachmens = []
        for a in rec.attachments:
            self.attachmens.append(Attachment(id=a.id, extension=a.extension))

        if rec.get_request_request != None and rec.get_request_request != "":
            self.mesages.append("GetRequestRequest")
        if rec.get_request_response != None and rec.get_request_response != "":
            self.mesages.append("GetRequestResponse")
        if rec.get_response_request != None and rec.get_response_request != "":
            self.mesages.append("GetResponseRequest")
        if rec.get_response_response != None and rec.get_response_response != "":
            self.mesages.append("GetResponseResponse")

        if rec.send_request_request != None and rec.send_request_request != "":
            self.mesages.append("SendRequestRequest")
        if rec.send_request_response != None and rec.send_request_response != "":
            self.mesages.append("SendRequestResponse")
        if rec.send_response_request != None and rec.send_response_request != "":
            self.mesages.append("SendResponseRequest")
        if rec.send_response_response != None and rec.send_response_response != "":
            self.mesages.append("SendResponseResponse")

        if rec.ack_request != None and rec.ack_request != "":
            self.mesages.append("AckRequest")
        
        return self
        
    class Config:
        orm_mode = True

class WorkerRecord(Record):
    communication_type: str = ""

class RecordUpdate(BaseModel):
    xml: str
    attachmens: List[Attachment] = []