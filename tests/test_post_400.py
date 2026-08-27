import requests

url = "http://127.0.0.1:5000/api/tickets"

# 故意缺少 ticket_no、fault 两个必填字段，验证校验逻辑
payload = {
    "customer": "测试客户",
    "phone": "13800000000",
    "device_type": "工业缝纫机",
    "device_sn": "SN-TEST-007"
}

resp = requests.post(url, json=payload)

print("HTTP状态码：", resp.status_code)
print("返回内容：")
print(resp.text)
