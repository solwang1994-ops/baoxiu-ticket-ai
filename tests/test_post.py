import requests

url = "http://127.0.0.1:5000/api/tickets"

# 工单数据，这里写普通字典，不用折腾引号转义
payload = {
    "ticket_no": "T-20260825-005",
    "customer": "测试客户",
    "phone": "13800000000",
    "device_type": "工业缝纫机",
    "device_sn": "SN-CURL-005",
    "fault": "curl联调测试"
}

# 发送POST请求，json=payload会自动帮我们处理JSON格式和请求头
resp = requests.post(url, json=payload)

print("返回结果：")
print(resp.text)
