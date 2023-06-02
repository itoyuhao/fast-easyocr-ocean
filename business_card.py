import streamlit as st
import requests
text = '霑鼎雲金融科技股份有限公司 PayPayCloud FinTech 山W paypaycloud.com 維運經理 Tel 04-2237-8333 張伯璜 Mobile 0912-713750 E mail bob chang@paypaycloud.com Operations Manager Line I b_o_b_0 Bob Chang 統一編號 55742415 Line@ paypaycloud'
r_info = requests.get(f'''http://bio.ppl.ai/chat.php?text=你現在是一個文字專家，現在有一個任務，會給你一串文字，這些文字都是來自辨識名片的結果。
你需要判斷這些文字所代表的意義，像是中文姓名、中文地址、英文地址、公司電話、個人手機號碼、職稱、公司名稱、
英文名字、電子郵件、社群媒體帳號或 ID （也請個別列點）、統一編號、公司/個人業務內容等等，也就是名片上會有的各種資訊。
不一定每一項資訊都會出現，要根據文字代表的意義去做分類。只需要回傳相關資訊即可。
請用列點的方式告訴我，並以 「意義：文字」的格式回答我，
任務開始：
以下是要請你幫我判斷的文字訊息
```
{text}
```''')
# st.write(r_info.text)

info_list = r_info.text.split("- ")
info_list = info_list[1:]
info_list = [i.replace("\n","") for i in info_list]

info_list_index = [i.split("：")[0] for i in info_list]
info_list_value = [i.split("：")[1] for i in info_list]

info_dict = dict(zip(info_list_index, info_list_value))

r_keywords = requests.get(f'http://bio.ppl.ai/chat.php?text=根據{info_dict["職稱"]}產生五個關鍵字描述該職位所需具備的能力，可以參考求職網站的必備技能描述，用下列的格式回傳給我「關鍵字1關鍵字2關鍵字3關鍵字4關鍵字5」')
keywords = r_keywords.text.replace("「","").replace("」","").replace("、","").replace("能力","")

r_intro = requests.get(f'http://bio.ppl.ai/chat.php?text={keywords}&name={info_dict["姓名"]}&title={info_dict["職稱"]}&company={info_dict["公司名稱"]}&html=yes')
st.write(r_intro.text)
r_card = requests.get(f'http://bio.ppl.ai/chat.php?text={r_keywords}&name={info_dict["姓名"]}&title={info_dict["職稱"]}&company={info_dict["公司名稱"]}&html=yes')
st.write(r_card.text)