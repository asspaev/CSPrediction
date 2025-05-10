from celery_app import celery_app
from fastapi import Depends

import cloudpickle
import pandas as pd

from utils.predicator import Predicator


@celery_app.task(
    name="tasks.predict.task_predict", bind=True, max_retries=3, default_retry_delay=60
)
def task_predict(
    self,
    path_model: str,
    match_link: str,
):
    try:
        with open(path_model, "rb") as f:
            ml_model = cloudpickle.load(f)

        df_mean_player = pd.read_csv("data/mean_player.csv").drop(columns="Unnamed: 0")

        predicator = Predicator(
            model=ml_model,
            mean_player=df_mean_player,
        )
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": "https://www.hltv.org/results",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"134.0.6998.189"',
            "sec-ch-ua-full-version-list": '"Chromium";v="134.0.6998.189", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.189"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"19.0.0"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Cookie": "MatchFilter={%22active%22:false%2C%22live%22:false%2C%22stars%22:1%2C%22lan%22:false%2C%22teams%22:[]}; CookieConsent={stamp:%27vNAlTZ21gOE2NHPJPAw3r40p6OXnAr/qXvKsXt3SpEHW6R/ajmeRxw==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1742577465026%2Cregion:%27lv%27}; __cf_bm=nQjyJl3pKc3NGB0NZcOUPJCrtvz8uMKdOyUIlfYYlpE-1743823187-1.0.1.1-ojyBr7I0w7xXfmAa12B22oLjDREmG5GEeDW0iULpL7GANfg4Y95o4_lHoc5f3IF0ervwyJ.PUgzOVXWN4WUgPSr2PX49yzC4XI2X8C6ZGfY; cf_clearance=UrCu2MPi_s9nmFY8be54MwX22zG9ntXiFPUKAErQ.34-1743823189-1.2.1.1-SWUcFNWTAfd2Hauz7qMLc.tvQdstJTG2v0NewFsWQdodjPD7o501jCop2.0Ciz7iIrlnIIJfxzfkBccSERHaRdYJih8iDefzyyCF_l9SsDklwTfd081lY5UgrCa9LrWcmrOXmGoNV3SwjywHoR9IVx8VWxkwb2Avs8X0qLp.TyTxmvnwi7oj1jaBHGiRF2Mf5h7qWI.fU.Osb1mZxR6YuRgK3Hg1RcmkACRXBoLOWOxALx8MgIS0B3zmd8o85bz8CsZo6WBuYQEIWrAQ5CfOC49LdjgSkpiwbagiivF2EIX0vGUIYRDe_MM5d9X.aYoRShuy4ODSUYI3P351YFIoxn1AnH85gaQCeISSYd1GmR0",
        }
        cookies = {
            c.split("=")[0].strip(): c.split("=", 1)[1].strip()
            for c in headers["Cookie"].split("; ")
        }

        predicator.set_scrapp_settings(headers=headers, cookies=cookies)

        y_pred = predicator.predict(match_link)

        return y_pred[0].item()
    except Exception as exc:
        raise self.retry(exc=exc)
