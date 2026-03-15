
import pandas as pd
import logging
from typing import List
from app.config import settings

logger=logging.getLogger(__name__)

def export_to_csv(data:List[dict])->str:
    df=pd.DataFrame(data)
    df.to_csv(settings.OUTPUT_FILE,index=False)
    logger.info("CSV exported %s",settings.OUTPUT_FILE)
    return settings.OUTPUT_FILE
