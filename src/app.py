#!/usr/bin/env python3
import configparser
import time
import threading
import mastodonTool
import os
import datetime
import markovify
import exportModel
import re

# 環境変数の読み込み
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')


def worker():
    # 学習

    domain1 = config_ini['read']['domain1']
    read_access_token1 = config_ini['read']['access_token1']
    domain2 = config_ini['read']['domain2']
    read_access_token2 = config_ini['read']['access_token2']
    domain3 = config_ini['read']['domain3']
    read_access_token3 = config_ini['read']['access_token3']
    domain4 = config_ini['read']['domain4']
    read_access_token4 = config_ini['read']['access_token4']
    
    domain = config_ini['write']['domain']
    write_access_token = config_ini['write']['access_token']

    account_info = mastodonTool.get_account_info(domain1, read_access_token1)
    params = {"exclude_replies": 1, "exclude_reblogs": 1}
    filename = "{}@{}".format(account_info["username"], domain1)
    filepath = os.path.join("./chainfiles", os.path.basename(filename.lower()) + ".json")
    if (os.path.isfile(filepath) and datetime.datetime.now().timestamp() - os.path.getmtime(filepath) < 60 * 60 * 24):
        print("モデルは再生成されません")
    else:
        account_info1 = mastodonTool.get_account_info(domain1, read_access_token1)
        exportModel.generateAndExport(mastodonTool.loadMastodonAPI(domain1, read_access_token1, account_info1['id'], params), filepath)
        print("LOG,GENMODEL," + str(datetime.datetime.now()) + "," + account_info["username"].lower())   # Log
        account_info2 = mastodonTool.get_account_info(domain2, read_access_token2)
        exportModel.generateAndExport(mastodonTool.loadMastodonAPI(domain2, read_access_token2, account_info2['id'], params), filepath)
        print("LOG,GENMODEL," + str(datetime.datetime.now()) + "," + account_info["username"].lower())   # Log
        account_info3 = mastodonTool.get_account_info(domain3, read_access_token3)
        exportModel.generateAndExport(mastodonTool.loadMastodonAPI(domain3, read_access_token3, account_info3['id'], params), filepath)
        print("LOG,GENMODEL," + str(datetime.datetime.now()) + "," + account_info["username"].lower())   # Log
        account_info4 = mastodonTool.get_account_info(domain4, read_access_token4)
        exportModel.generateAndExport(mastodonTool.loadMastodonAPI(domain4, read_access_token4, account_info4['id'], params), filepath)
        print("LOG,GENMODEL," + str(datetime.datetime.now()) + "," + account_info["username"].lower())   # Log
    # 生成
    with open("./chainfiles/{}@{}.json".format(account_info["username"].lower(), domain)) as f:
        textModel = markovify.Text.from_json(f.read())
        sentence = textModel.make_sentence(tries=300)
        sentence = "".join(sentence.split()) + ' #bot'
        sentence = re.sub(r'(:.*?:)', r' \1 ', sentence)
        print(sentence)
    try:
        mastodonTool.post_toot(domain, write_access_token, {"status": sentence})
    except Exception as e:
        print("投稿エラー: {}".format(e))


def schedule(f, interval=1200, wait=True):
    base_time = time.time()
    next_time = 0
    while True:
        t = threading.Thread(target=f)
        t.start()
        if wait:
            t.join()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)


if __name__ == "__main__":
    # 定期実行部分
    schedule(worker)
    # worker()
