import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "https://www.foody.vn/da-nang/cafe"
OUTPUT_DIR = "/app/landing_zone"
MAX_PAGES_TO_CRAWL = 1

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    
headers = {
    "accept" : "application/json, text/javascript, */*; q=0.01",
    "accept-language": "vi,en;q=0.9,en-US;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.foody.vn/da-nang/cafe?CategoryGroup=food&c=cafe",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Microsoft Edge\";v=\"136\",\"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
    "x-foody-user-token": "CWgeVZyLOnntFbStgteOYuZzYpdYosRJw4xL9UqhKK4hVm5PsISVWUaMyuor",
    "x-requested-with": "XMLHttpRequest"
}

cookies = {
    "flg": "vn",
    "gcat": "food",
    "floc": "219",
    "__ondemand_sessionid": "lefesd4u3qzumej3ixxslieu",
    "ID_FOODY.AUTH": "C1B1CDDA4E8240F8B046BAB366CBFC6578A6C7CD7E76B58BC0ED2B855E039F0B2D24DBD229833B8527F9F3A5F00494A24ADC195DBF3AA678B9F23799B6269A9821BC76EFF60898732A31358A6E7D45F6818FCAEDD104124ABDE5B7A2C25C8C59FEE0AAA0EB24C6503EE28223EA52F054ACF5DD57AF49A3C013FD91684C047CDDCD2AEAFAF0E42C38903DBE22F66ABA8BB3985A89D1BE6554707A2B430B39AFB232DA30281ECE6D2E3DC58BF208DD8842C7E8267798ECEE2D237DF7B2FD6C3F7C9CB80C7DF0A5CCF4DC6B03E21E118DC7D9CE70FDF3F6C922832FE97703CBD815E33620120B4058EF537D1302AB32DDBA",
    "FOODY.AUTH.UDID": "c96f16dd-131e-4535-8089-2ef8f4826b6a",
    "FOODY.AUTH": "6D14B9E7F5FC7611DEABE5BE3E378D754692DF4BA82DF1BF2DB6A328155A4064ADA9CE9354BF7E9C53957D3E105ECA2F0D20BA00346D7C19D0748AB43B544A93CEEE546DAF3BDFDA1BC9DE8610D54F03625B623DA28FCC0847FC3F20A797E9E4A6C9ACCFFF8ADAE52784FDEA03984939742AAF729E192B7DAADA7CA4E26C35BFB4DFB84DD3D8800C875F4C5EEC447AA7FDC4A3F977A4D8D2A59DA84C7AC1B9C8316CA75781B9431F1DAFF14DCAA0972C9300120F6A17946D3B8E816E7C546D88FC341318BD5D1089F8448F30D0BE9F1624D2550536FD1113A4D31E53F425F52195E7E27585B9691C40D1FA4F43F29072",
    "fd.verify.password.57568525": "16/05/2025",
    "fd.keys": ""
}


# ds=Restaurant&vt=row&st=1&c=2&provinceId=219&categoryId=2&append=true
params_template = {
    "ds": "Restaurant",
    "vt": "row",
    "st": "1",
    "c": "2",
    "provinceId": "219",
    "categoryId": "2",
    "append": "true"
}


def crawl_page(page_number):
    params = params_template.copy()
    params["page"] = page_number

    try:
        print(f"Đang cào trang số: {page_number}")
        response = requests.get(BASE_URL, headers=headers, cookies=cookies, params=params)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')

        if 'application/json' in content_type:
            data = response.json()
        else:
            print(f"Trang {page_number} không trả về json trực tiếp. content-type: {content_type}")
            return None
        
        if data:
            # Tạo timestamp cho tên file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(OUTPUT_DIR, f"foody_danang_cafe_page_{page_number}_{timestamp}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                      json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Đã lưu dữ liệu trang {page_number} vào {file_path}")

            if "searchItems" in data and not data["searchItems"]:
                print(f"Trang {page_number} không có thêm địa điểm mới. Dừng crawl.")
                return "NO_MORE_ITEMS"
            return data
        else:
            print(f"Không nhận được dữ liệu từ trang {page_number}")
            return None

    
    except requests.exceptions.HTTPError as http_err:
        print(f"Lỗi HTTP khi crawl trang {page_number}: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Lỗi kết nối khi crawl trang {page_number}: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Request timeout khi crawl trang {page_number}: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Lỗi request chung khi crawl trang {page_number}: {req_err}")
    return None      


if __name__ == "__main__":
    start_page = 1
    for i in range(MAX_PAGES_TO_CRAWL):
        current_page = start_page + i
        result = crawl_page(current_page)

        if result is None:
            print(f"Gặp lỗi hoặc không có dữ liệu ở trang {current_page}, thử lại sau hoặc dừng.")
            break

        if result == "NO_MORE_ITEMS":
            break

        time.sleep(2)

    print("Done crawl.")