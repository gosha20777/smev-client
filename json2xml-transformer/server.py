from fastapi import FastAPI, HTTPException, Request
from xsd_processor.processor import XsdProcessor

# init
app = FastAPI()

@app.post('/api/v1/{sheme_number}/{element_type}')
async def json2xml(sheme_number: str, element_type: str, req: Request):
    if element_type == None or element_type == "":
        raise HTTPException(status_code=400, detail='invalid element_type')

    try:
        xsd_params = await req.json()
    except:
        raise HTTPException(status_code=400, detail='invalid input json')
    
    try:
        xsd_proc = XsdProcessor(smev_number=sheme_number)
        result = await xsd_proc.process(element_type=element_type, params=xsd_params)
    except Exception as e:
        raise HTTPException(status_code=400, detail="{}".format(e))

    return {'xml': result }