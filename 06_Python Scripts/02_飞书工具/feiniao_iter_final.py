# -*- coding: utf-8 -*-
import sys, io, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = 'cli_a90dbd544bb8dcb2'
APP_SECRET = 'dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2'
BT = 'MZAobRwwnaxN0ls1NGpcvPNhnSb'
TBL = 'tblSBx7rHX0siCnD'

def tk():
    r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', json={'app_id': APP_ID, 'app_secret': APP_SECRET})
    return r.json().get('tenant_access_token') if r.json().get('code') == 0 else None

def up(tok, rid, title, intro, product):
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BT}/tables/{TBL}/records/{rid}'
    r = requests.put(url, headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json; charset=utf-8'}, json={'fields': {'标题': title, '简介': intro, '商品短标题': product}})
    return r.json().get('code') == 0

tok = tk()
if not tok:
    print('Token failed')
    sys.exit(1)

updates = [
    ('recvf3IcP0oSJr',
     '！郑振铎1922年翻译，至今无人超越？',
     '泰戈尔《飞鸟集》，郑振铎用白话散文诗翻译——开创白话译诗先河，奠定近百年经典地位。商务印书馆布面精装，天空蓝三面刷边，羽毛编码限量，一书一码。翻到最后一页，你想到的是谁？',
     '飞鸟集羽毛编码布面精装版'),
    ('recvf3IdqAQGRJ',
     '？地铁刷短视频的人，永远不懂"生如夏花"！',
     '泰戈尔《飞鸟集》刷边版，440克巴掌本，三面天空蓝刷边，每本轨迹不同——不是印刷品，是握在手里的精神雕塑。28克薄纸专色印刷，翻页能感受纸张呼吸。羽毛编码限量，错过即绝版。翻到最后一页，你想到的是谁？',
     '飞鸟集刷边绝版'),
    ('recvf3IdXsp0I6',
     '！亚洲首位诺奖得主，竟被误读100年？',
     '你以为《飞鸟集》只是鸡汤？1913年诺奖、1922年白话翻译开创先河。叶芝说它能忘却世间痛苦，但更狠的是——诗训练的是感受力，而不是背诵能力。布面精装、每本羽毛编码独一无二。下次有人说读诗没用，把这条转给他。',
     '飞鸟集羽毛编码绝版'),
    ('recvghqKBe8tSY',
     '？这本书的护封设计，99%的人都没注意到？',
     '《飞鸟集》护封上随机分布的金银丝线，每本都不一样——这不是瑕疵，是设计：它们轨迹不同，寓意鸟儿飞行的轨迹，终以一只飞鸟栖于书末，泰戈尔在护封里藏了一个关于自由的故事。商务印书馆为这本书量身定制纸张，28克薄纸专色印刷。一书一码，随机即限量。',
     '飞鸟集羽毛编码护封精装版'),
    ('recvghqL985vNe',
     '？碎片化时代，为什么还有人每天抄一句泰戈尔的诗？',
     '叶芝说每天读一句泰戈尔可以忘却世间痛苦——他教的不是诗，是让你在焦虑、失眠、emo里重建秩序的能力。325首，每首两行，刷牙时、地铁上、失眠夜，随手翻开都能用。布面精装刷边版，28g薄纸翻页如呼吸。不鸡汤，是武器。',
     '飞鸟集天空蓝刷边便携版'),
]

print('=' * 60)
print('Feiniao DBS Iteration Upload')
print('=' * 60)

for rid, title, intro, product in updates:
    ok = up(tok, rid, title, intro, product)
    tag = 'OK' if ok else 'FAIL'
    print(f'  {rid}: {tag} | {title[:30]}')

print()
print('Done.')
